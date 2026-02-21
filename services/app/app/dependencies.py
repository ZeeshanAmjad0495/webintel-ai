from app.services.executor import JobExecutor
from app.services.monitoring import MonitorService
from app.services.repositories import InMemoryRepository
from app.services.scheduler import Scheduler

repository = InMemoryRepository()
executor = JobExecutor()
monitor_service = MonitorService(repository)
scheduler = Scheduler(repository, executor)
