"""Application-scoped dependency wiring for services and repositories."""

from app.services.executor import JobExecutor
from app.services.monitoring import MonitorService
from app.services.repositories import InMemoryRepository
from app.services.scheduler import Scheduler

repository = InMemoryRepository()
executor = JobExecutor()
monitor_service = MonitorService(repository)
scheduler = Scheduler(repository, executor)


def get_repository() -> InMemoryRepository:
    """Return the active repository implementation."""

    return repository


def get_monitor_service() -> MonitorService:
    """Return the monitor service."""

    return monitor_service


def get_scheduler() -> Scheduler:
    """Return the scheduler service."""

    return scheduler
