from __future__ import annotations

from .models import Task

PRIORITIES = ("low", "medium", "high")

_ORDER = {"high": 0, "medium": 1, "low": 2}


def validate_priority(priority: str) -> str:
    if priority not in PRIORITIES:
        raise ValueError("Недопустимый приоритет")
    return priority


def sort_tasks(tasks: list[Task]) -> list[Task]:
    return sorted(tasks, key=lambda t: (_ORDER[t.priority], t.created_at))
