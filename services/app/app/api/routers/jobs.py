from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import JobCreate, JobResponse, JobUpdate, RunResponse
from app.dependencies import get_repository, get_scheduler
from app.services.repositories import InMemoryRepository
from app.services.scheduler import Scheduler

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate,
    repository: InMemoryRepository = Depends(get_repository),
) -> JobResponse:
    if not await repository.get_task(payload.task_id):
        raise HTTPException(status_code=404, detail="task not found")
    job = await repository.create_job(payload.task_id, payload.schedule_every_seconds, payload.enabled)
    return JobResponse.model_validate(job.__dict__)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    repository: InMemoryRepository = Depends(get_repository),
) -> list[JobResponse]:
    return [JobResponse.model_validate(job.__dict__) for job in await repository.list_jobs()]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, repository: InMemoryRepository = Depends(get_repository)) -> JobResponse:
    job = await repository.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JobResponse.model_validate(job.__dict__)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    payload: JobUpdate,
    repository: InMemoryRepository = Depends(get_repository),
) -> JobResponse:
    job = await repository.update_job(job_id, **payload.model_dump())
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JobResponse.model_validate(job.__dict__)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, repository: InMemoryRepository = Depends(get_repository)) -> None:
    deleted = await repository.delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="job not found")


@router.post("/run", response_model=RunResponse)
async def run_scheduler_once(
    scheduler: Scheduler = Depends(get_scheduler),
) -> RunResponse:
    result = await scheduler.run_once()
    return RunResponse(status="ok", details=f"success={result['success']} failures={result['failures']}")
