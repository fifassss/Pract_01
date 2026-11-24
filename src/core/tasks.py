from __future__ import annotations

from .models import Task
from .priority import validate_priority

# Хранилище задач в памяти ядра. Для дня 4 подменяется слоем данных.
_STORE: dict[int, Task] = {}
_NEXT_ID = 1


def _next_id() -> int:
    global _NEXT_ID
    current = _NEXT_ID
    _NEXT_ID += 1
    return current


def add_task(title: str, description: str = "", priority: str = "medium", due: str = "") -> Task:
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Название задачи не может быть пустым")
    if len(title) > 200:
        raise ValueError("Название задачи не может быть длиннее 200 символов")
    validate_priority(priority)

    task = Task(
        id=_next_id(),
        title=title,
        description=description,
        priority=priority,
        due=due,
    )
    _STORE[task.id] = task
    return task


def get_task(id: int) -> Task | None:
    return _STORE.get(id)


def list_tasks() -> list[Task]:
    return list(_STORE.values())


def close_task(id: int) -> Task:
    task = get_task(id)
    if task is None:
        raise ValueError("Задача не найдена")
    task.status = "done"
    return task


def delete_task(id: int) -> bool:
    if id in _STORE:
        del _STORE[id]
        return True
    return False
