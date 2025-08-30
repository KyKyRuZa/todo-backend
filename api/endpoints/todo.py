from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.models.todo import TodoCreate, TodoResponse
from dependencies import get_db, get_todo_service
from services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/", response_model=list[TodoResponse])
async def get_todos(
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    return todo_service.get_todos(db)

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    todo = todo_service.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.post("/", response_model=TodoResponse)
async def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    return todo_service.create_todo(db, todo)

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo: TodoCreate,
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    updated_todo = todo_service.update_todo(db, todo_id, todo)
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo

@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    if not todo_service.delete_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted"}