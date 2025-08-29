from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
import os

# Загрузка переменных из .env
load_dotenv()

# Настройка FastAPI
app = FastAPI()

# Настройка CORS

origins = [
    "http://localhost:8080",
    "http://localhost:8000",
    "http://10.0.2.2:8080",  # Для Android-эмулятора
    "http://localhost:*",     # Для веб-версии Flutter
    "http://127.0.0.1:*",    # Альтернативный адрес
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель SQLAlchemy для таблицы todos
class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    time = Column(String, default="")
    completed = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    completedAt = Column(DateTime, nullable=True)

# Pydantic модели
class TodoCreate(BaseModel):
    title: str
    time: str = ""
    completed: bool = False

class TodoResponse(BaseModel):
    id: int
    title: str
    time: str
    completed: bool
    createdAt: datetime | None
    completedAt: datetime | None

    class Config:
        from_attributes = True

# Создание таблицы
Base.metadata.create_all(bind=engine)

# Эндпоинты
@app.get("/")
async def root():
    return {"message": "Welcome to the Todo List API!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/todos", response_model=list[TodoResponse])
async def get_todos():
    db = SessionLocal()
    try:
        todos = db.query(Todo).all()
        return todos
    finally:
        db.close()

@app.post("/todos", response_model=TodoResponse)
async def create_todo(todo: TodoCreate):
    db = SessionLocal()
    try:
        db_todo = Todo(title=todo.title, time=todo.time, completed=todo.completed)
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    finally:
        db.close()

@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo: TodoCreate):
    db = SessionLocal()
    try:
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if db_todo is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        db_todo.title = todo.title
        db_todo.time = todo.time
        db_todo.completed = todo.completed
        db_todo.completedAt = datetime.utcnow() if todo.completed else None
        db.commit()
        db.refresh(db_todo)
        return db_todo
    finally:
        db.close()

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    db = SessionLocal()
    try:
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if db_todo is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        db.delete(db_todo)
        db.commit()
        return {"message": "Todo deleted"}
    finally:
        db.close()

@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int):
    db = SessionLocal()
    try:
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if todo is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo
    finally:
        db.close()