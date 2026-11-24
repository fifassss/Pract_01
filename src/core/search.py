from __future__ import annotations

from .models import Task


def filter_tasks(tasks: list[Task], query: str) -> list[Task]:
    if not query or not query.strip():
        return list(tasks)
    needle = query.lower()
    return [
        t
        for t in tasks
        if needle in t.title.lower() or needle in t.description.lower()
    ]
