from __future__ import annotations

import json
from datetime import datetime

from .models import Task


def save_store(path: str, tasks: list[Task]) -> None:
    data = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "status": t.status,
            "due": t.due,
            "created_at": t.created_at.isoformat(),
        }
        for t in tasks
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_store(path: str) -> list[Task]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Не удалось прочитать файл задач: {exc}") from exc

    tasks: list[Task] = []
    for item in raw:
        created_at = item.get("created_at")
        tasks.append(
            Task(
                id=item.get("id"),
                title=item.get("title", ""),
                description=item.get("description", ""),
                priority=item.get("priority", "medium"),
                status=item.get("status", "open"),
                due=item.get("due", ""),
                created_at=datetime.fromisoformat(created_at) if created_at else datetime.now(),
            )
        )
    return tasks
