from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel

Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    time = Column(String, default="")
    completed = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    completedAt = Column(DateTime, nullable=True)

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