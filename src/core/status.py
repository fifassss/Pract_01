from __future__ import annotations

from .models import Task
from .tasks import get_task

STATUSES = ("open", "done")


def task_status(id: int) -> str:
    task = get_task(id)
    if task is None:
        raise ValueError("Задача не найдена")
    return task.status


def set_status(id: int, status: str) -> Task:
    if status not in STATUSES:
        raise ValueError("Недопустимый статус")
    task = get_task(id)
    if task is None:
        raise ValueError("Задача не найдена")
    task.status = status
    return task
