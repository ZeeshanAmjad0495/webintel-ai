from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.schemas import MonitorCreate, MonitorResponse, MonitorUpdate
from app.dependencies import monitor_service, repository

router = APIRouter(prefix="/monitors", tags=["monitors"])


class SnapshotRequest(BaseModel):
    snapshot: str


@router.post("", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
async def create_monitor(payload: MonitorCreate) -> MonitorResponse:
    monitor = await repository.create_monitor(payload.name, payload.source_url)
    return MonitorResponse.model_validate(monitor.__dict__)


@router.get("", response_model=list[MonitorResponse])
async def list_monitors() -> list[MonitorResponse]:
    return [MonitorResponse.model_validate(monitor.__dict__) for monitor in await repository.list_monitors()]


@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_monitor(monitor_id: str) -> MonitorResponse:
    monitor = await repository.get_monitor(monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="monitor not found")
    return MonitorResponse.model_validate(monitor.__dict__)


@router.put("/{monitor_id}", response_model=MonitorResponse)
async def update_monitor(monitor_id: str, payload: MonitorUpdate) -> MonitorResponse:
    monitor = await repository.update_monitor(monitor_id, **payload.model_dump())
    if not monitor:
        raise HTTPException(status_code=404, detail="monitor not found")
    return MonitorResponse.model_validate(monitor.__dict__)


@router.post("/{monitor_id}/snapshot", response_model=MonitorResponse)
async def ingest_snapshot(monitor_id: str, payload: SnapshotRequest) -> MonitorResponse:
    changed = await monitor_service.ingest_snapshot(monitor_id, payload.snapshot)
    monitor = await repository.get_monitor(monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="monitor not found")
    monitor.changed = changed
    return MonitorResponse.model_validate(monitor.__dict__)


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor(monitor_id: str) -> None:
    deleted = await repository.delete_monitor(monitor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="monitor not found")
