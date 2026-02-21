from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    name: str
    payload: dict[str, Any] = Field(default_factory=dict)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: str | None = None
    payload: dict[str, Any] | None = None


class TaskResponse(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime


class JobBase(BaseModel):
    task_id: str
    schedule_every_seconds: int = Field(default=60, ge=1)
    enabled: bool = True


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    schedule_every_seconds: int | None = Field(default=None, ge=1)
    enabled: bool | None = None


class JobResponse(JobBase):
    id: str
    last_run_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class MonitorBase(BaseModel):
    name: str
    source_url: str


class MonitorCreate(MonitorBase):
    pass


class MonitorUpdate(BaseModel):
    name: str | None = None
    source_url: str | None = None


class MonitorResponse(MonitorBase):
    id: str
    last_snapshot_hash: str | None = None
    changed: bool = False
    created_at: datetime
    updated_at: datetime


class RunResponse(BaseModel):
    status: str
    details: str
