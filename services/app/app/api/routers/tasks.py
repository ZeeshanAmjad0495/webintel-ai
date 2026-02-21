from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import TaskCreate, TaskResponse, TaskUpdate
from app.dependencies import get_repository
from app.services.repositories import InMemoryRepository

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    repository: InMemoryRepository = Depends(get_repository),
) -> TaskResponse:
    task = await repository.create_task(payload.name, payload.payload)
    return TaskResponse.model_validate(task.__dict__)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    repository: InMemoryRepository = Depends(get_repository),
) -> list[TaskResponse]:
    return [TaskResponse.model_validate(task.__dict__) for task in await repository.list_tasks()]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, repository: InMemoryRepository = Depends(get_repository)) -> TaskResponse:
    task = await repository.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return TaskResponse.model_validate(task.__dict__)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    repository: InMemoryRepository = Depends(get_repository),
) -> TaskResponse:
    task = await repository.update_task(task_id, **payload.model_dump())
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return TaskResponse.model_validate(task.__dict__)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, repository: InMemoryRepository = Depends(get_repository)) -> None:
    deleted = await repository.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="task not found")
