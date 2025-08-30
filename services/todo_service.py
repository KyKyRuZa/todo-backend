from sqlalchemy.orm import Session
from api.models.todo import Todo, TodoCreate
from datetime import datetime

class TodoService:
    def get_todos(self, db: Session):
        return db.query(Todo).all()
    
    def get_todo(self, db: Session, todo_id: int):
        return db.query(Todo).filter(Todo.id == todo_id).first()
    
    def create_todo(self, db: Session, todo: TodoCreate):
        db_todo = Todo(
            title=todo.title,
            time=todo.time,
            completed=todo.completed
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    
    def update_todo(self, db: Session, todo_id: int, todo: TodoCreate):
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if not db_todo:
            return None
            
        db_todo.title = todo.title
        db_todo.time = todo.time
        db_todo.completed = todo.completed
        db_todo.completedAt = datetime.utcnow() if todo.completed else None
        
        db.commit()
        db.refresh(db_todo)
        return db_todo
    
    def delete_todo(self, db: Session, todo_id: int):
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if not db_todo:
            return False
            
        db.delete(db_todo)
        db.commit()
        return True

# Создаем глобальный экземпляр
todo_service = TodoService()