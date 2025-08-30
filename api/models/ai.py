from pydantic import BaseModel
from typing import List

class MessageRequest(BaseModel):
    user_id: str
    message: str
    active_todos: List[str] = []
    completed_todos: List[str] = []

class MessageResponse(BaseModel):
    parts: List[str]