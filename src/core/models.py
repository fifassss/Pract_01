from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    id: int | None = None
    title: str = ""
    description: str = ""
    priority: str = "medium"
    status: str = "open"
    due: str = ""
    created_at: datetime = field(default_factory=datetime.now)
