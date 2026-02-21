from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import httpx


@dataclass(slots=True)
class MonitorFetchResult:
    url: str
    fetched_at: datetime
    status_code: int
    content: str
    content_hash: str


@dataclass(slots=True)
class MonitorDiffResult:
    has_changed: bool
    previous_hash: Optional[str]
    current_hash: str


def normalize_content(content: str) -> str:
    return "\n".join(line.strip() for line in content.splitlines() if line.strip())


def compute_content_hash(content: str) -> str:
    normalized = normalize_content(content)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def diff_hashes(*, previous_hash: Optional[str], current_hash: str) -> MonitorDiffResult:
    return MonitorDiffResult(
        has_changed=previous_hash is not None and previous_hash != current_hash,
        previous_hash=previous_hash,
        current_hash=current_hash,
    )


async def fetch_monitor_target(url: str, *, timeout_s: float = 15.0) -> MonitorFetchResult:
    async with httpx.AsyncClient(timeout=timeout_s, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        content = response.text

    return MonitorFetchResult(
        url=url,
        fetched_at=datetime.now(timezone.utc),
        status_code=response.status_code,
        content=content,
        content_hash=compute_content_hash(content),
    )
