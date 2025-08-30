import httpx
import re
from typing import List, Dict
from core.config import settings

class AIService:
    def __init__(self):
        self.user_conversations: Dict[str, List[Dict[str, str]]] = {}

    def clean_response(self, text: str) -> str:
        if '</think>' in text:
            text = text.split('</think>')[-1].strip()
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            trimmed_line = line.strip()
            if trimmed_line and not self._is_marker_only(trimmed_line):
                cleaned_line = self._remove_initial_markers(trimmed_line)
                cleaned_lines.append(cleaned_line)
            elif not trimmed_line:
                cleaned_lines.append('')
                
        return '\n'.join(cleaned_lines).strip()
    
    def _is_marker_only(self, line: str) -> bool:
        return bool(re.match(r'^[\*\-# ]+$', line))
    
    def _remove_initial_markers(self, line: str) -> str:
        return re.sub(r'^[\*\-# ]+', '', line)
    
    def format_code_response(self, text: str) -> str:
        if '```' in text:
            return text
            
        is_code = self._is_likely_code(text)
        if not is_code:
            return text
            
        lang = self._detect_language(text)
        return f"```{lang}\n{text}\n```" if lang else f"```text\n{text}\n```"
    
    def _is_likely_code(self, text: str) -> bool:
        lines = text.split('\n')
        if len(lines) > 3:
            code_keywords = ['public ', 'private ', 'def ', 'function ', 'class ', 'import ', '#include']
            if any(any(line.strip().startswith(kw) for kw in code_keywords) for line in lines):
                return True
        
        return (';' in text and '{' in text and '}' in text) or \
               text.startswith('#!/') or \
               ('def ' in text or 'class ' in text)
    
    def _detect_language(self, text: str) -> str:
        lang_keywords = {
            "java": ["public class", "import java.", "System.out.println", "@Override"],
            "python": ["import ", "def ", "print(", "lambda ", "if __name__"],
            "javascript": ["function ", "const ", "let ", "console.log", "=>"],
            "c++": ["#include", "using namespace", "std::", "cout <<"],
            "html": ["<!DOCTYPE", "<html>", "<div>", "<script"],
            "css": ["{", "}", "font-", "color:", "background:"],
            "sql": ["SELECT", "FROM", "WHERE", "JOIN"],
            "bash": ["#!/bin/bash", "#!/bin/sh", "chmod +x"],
            "dart": ["import ", "void main", "class ", "final ", "const "],
        }
        
        for lang, keywords in lang_keywords.items():
            if any(keyword in text for keyword in keywords):
                return lang
        return ""
    
    def split_text(self, text: str, max_length: int = 4096) -> List[str]:
        parts = []
        
        if "```" in text:
            while text:
                start_idx = text.find("```")
                if start_idx == -1:
                    parts.append(text)
                    break
                    
                end_idx = text.find("```", start_idx + 3)
                if end_idx == -1:
                    parts.append(text)
                    break
                    
                if start_idx > 0:
                    parts.append(text[:start_idx])
                    
                code_block = text[start_idx:end_idx + 3]
                parts.append(code_block)
                
                text = text[end_idx + 3:]
            return parts
            
        while text:
            if len(text) <= max_length:
                parts.append(text)
                break
                
            split_index = max_length
            if text[:max_length].find('\n\n') != -1:
                split_index = text.rfind('\n\n', 0, max_length) + 2
            elif text[:max_length].find('\n') != -1:
                split_index = text.rfind('\n', 0, max_length) + 1
            elif text[:max_length].find(' ') != -1:
                split_index = text.rfind(' ', 0, max_length) + 1
                
            if split_index <= 0:
                split_index = max_length
                
            part = text[:split_index].strip()
            if part:
                parts.append(part)
            text = text[split_index:].strip()
            
        return parts
    
    async def get_ai_response(self, user_id: str, message: str, active_todos: List[str], completed_todos: List[str]) -> List[str]:
        try:
            if user_id not in self.user_conversations:
                self.user_conversations[user_id] = []
                
            self.user_conversations[user_id].append({
                "role": "user",
                "content": message
            })
            
            if len(self.user_conversations[user_id]) > settings.MAX_HISTORY:
                self.user_conversations[user_id] = self.user_conversations[user_id][-settings.MAX_HISTORY:]
                
            productivity_context = ""
            if active_todos or completed_todos:
                total_tasks = len(active_todos) + len(completed_todos)
                productivity = (len(completed_todos) / total_tasks * 100) if total_tasks > 0 else 0
                productivity_context = f"""
                Текущая продуктивность: {productivity:.0f}%
                Активные задачи: {', '.join(active_todos)}
                Завершенные задачи: {', '.join(completed_todos)}
                """
                
            full_message = f"{productivity_context}\n{message}".strip()
            
            messages = [
                {"role": "system", "content": settings.SYSTEM_PROMPT},
                *self.user_conversations[user_id]
            ]
            
            messages[-1]["content"] = full_message
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.API_CHAT_URL,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {settings.API_AUTH_TOKEN}"
                    },
                    json={
                        "model": settings.MODEL_NAME,
                        "messages": messages
                    },
                    timeout=30.0
                )
                
            if response.status_code == 200:
                data = response.json()
                raw_text = data['choices'][0]['message']['content']
                
                cleaned_text = self.clean_response(raw_text)
                formatted_text = self.format_code_response(cleaned_text)
                parts = self.split_text(formatted_text)
                
                self.user_conversations[user_id].append({
                    "role": "assistant",
                    "content": formatted_text
                })
                
                return parts
            else:
                raise Exception(f"AI API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to get AI response: {str(e)}")

ai_service = AIService()