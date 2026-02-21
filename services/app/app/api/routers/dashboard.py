"""Simple frontend dashboard for inspecting WebIntel sample state."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])


@router.get("/", response_class=HTMLResponse, summary="WebIntel dashboard")
async def dashboard() -> HTMLResponse:
    """Render a lightweight dashboard powered by API endpoints."""

    html = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>WebIntel AI Dashboard</title>
    <style>
      :root { color-scheme: light dark; }
      body {
        margin: 0;
        font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        background: #0b1020;
        color: #e6ecff;
      }
      .wrap { max-width: 1080px; margin: 0 auto; padding: 2rem 1rem 3rem; }
      h1 { margin: 0 0 1rem; font-size: 1.8rem; }
      p { color: #adbbf5; }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
      }
      .card {
        background: #141b33;
        border: 1px solid #2a3563;
        border-radius: 12px;
        padding: 1rem;
      }
      .label { color: #8fa0e6; font-size: 0.85rem; margin-bottom: 0.3rem; }
      .value { font-size: 1.6rem; font-weight: 700; }
      table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        background: #141b33;
        border: 1px solid #2a3563;
        border-radius: 12px;
        overflow: hidden;
      }
      th, td {
        text-align: left;
        padding: 0.7rem;
        border-bottom: 1px solid #222c53;
        font-size: 0.95rem;
      }
      th { color: #9cadf0; background: #10162c; }
      button {
        background: #5670ff;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 0.85rem;
        cursor: pointer;
        font-weight: 600;
      }
      .muted { color: #8fa0e6; font-size: 0.9rem; }
    </style>
  </head>
  <body>
    <main class="wrap">
      <h1>WebIntel AI Dashboard</h1>
      <p>Sample operational view of tasks, jobs, and monitors from the API.</p>
      <button id="refresh">Refresh</button>

      <section class="grid" aria-label="summary cards">
        <div class="card"><div class="label">Tasks</div><div class="value" id="task-count">-</div></div>
        <div class="card"><div class="label">Jobs</div><div class="value" id="job-count">-</div></div>
        <div class="card"><div class="label">Monitors</div><div class="value" id="monitor-count">-</div></div>
      </section>

      <h2>Recent Jobs</h2>
      <table>
        <thead><tr><th>Job ID</th><th>Task ID</th><th>Interval (s)</th><th>Enabled</th></tr></thead>
        <tbody id="job-rows"><tr><td colspan="4" class="muted">Loading...</td></tr></tbody>
      </table>
    </main>
    <script>
      const toRows = (jobs) => {
        if (!jobs.length) {
          return '<tr><td colspan="4" class="muted">No jobs created yet.</td></tr>';
        }
        return jobs
          .slice(0, 6)
          .map((job) =>
            `<tr><td>${job.id}</td><td>${job.task_id}</td><td>${job.schedule_every_seconds}</td><td>${job.enabled}</td></tr>`
          )
          .join('');
      };

      const loadDashboard = async () => {
        const [tasks, jobs, monitors] = await Promise.all([
          fetch('/api/tasks').then((res) => res.json()),
          fetch('/api/jobs').then((res) => res.json()),
          fetch('/api/monitors').then((res) => res.json()),
        ]);

        document.getElementById('task-count').textContent = tasks.length;
        document.getElementById('job-count').textContent = jobs.length;
        document.getElementById('monitor-count').textContent = monitors.length;
        document.getElementById('job-rows').innerHTML = toRows(jobs);
      };

      document.getElementById('refresh').addEventListener('click', loadDashboard);
      loadDashboard().catch((error) => {
        document.getElementById('job-rows').innerHTML =
          `<tr><td colspan="4" class="muted">Failed to load dashboard data: ${error}</td></tr>`;
      });
    </script>
  </body>
</html>
"""
    return HTMLResponse(content=html)

