from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from core.config import settings
from services.todo_service import todo_service
from services.ai_service import ai_service
from api.models.todo import Base

# Создаем engine для базы данных
engine = create_engine(settings.DATABASE_URL)

def get_db():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

def get_todo_service():
    return todo_service

def get_ai_service():
    return ai_service