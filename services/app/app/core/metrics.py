from prometheus_client import Counter, Gauge, Histogram

TASK_COUNT = Gauge("task_count", "Current number of tasks")
JOB_COUNT = Gauge("job_count", "Current number of jobs")
MONITOR_COUNT = Gauge("monitor_count", "Current number of monitors")

RUN_DURATION_SECONDS = Histogram(
    "run_duration_seconds",
    "Execution duration for monitored operations",
    labelnames=("operation", "status"),
)

FAILURE_COUNTER = Counter(
    "failure_total",
    "Failure counts by operation",
    labelnames=("operation",),
)
