import os
import tempfile

import pytest

from src.core.models import Task
from src.core.tasks import (
    create_task,
    add_task,
    update_task,
    delete_task,
    mark_done,
)
from src.core.priority import (
    PRIORITIES,
    normalize_priority,
    is_valid_priority,
    sort_by_priority,
)
from src.core.status import STATUSES, normalize_status, is_valid_status, is_done
from src.core.search import filter_tasks


# ---------------------------------------------------------------------------
# models.Task
# ---------------------------------------------------------------------------

def test_task_defaults():
    task = Task(id=1, title="Купить молоко")
    assert task.priority == "medium"
    assert task.status == "open"
    assert task.due is None
    assert task.done is False


def test_task_done_flag_from_status():
    assert Task(id=1, title="x", status="done").done is True
    assert Task(id=1, title="x", status="open").done is False


@pytest.mark.parametrize("title", ["", "   ", None])
def test_task_empty_title_rejected(title):
    with pytest.raises(ValueError, match="название"):
        Task(id=1, title=title)


def test_task_title_too_long_rejected():
    with pytest.raises(ValueError, match="200"):
        Task(id=1, title="a" * 201)


def test_task_title_max_length_ok():
    assert Task(id=1, title="a" * 200).title == "a" * 200


@pytest.mark.parametrize("priority", ["low", "medium", "high"])
def test_task_valid_priority(priority):
    assert Task(id=1, title="t", priority=priority).priority == priority


def test_task_invalid_priority_rejected():
    with pytest.raises(ValueError, match="приоритет"):
        Task(id=1, title="t", priority="urgent")


@pytest.mark.parametrize("status", ["open", "done"])
def test_task_valid_status(status):
    assert Task(id=1, title="t", status=status).status == status


def test_task_invalid_status_rejected():
    with pytest.raises(ValueError, match="статус"):
        Task(id=1, title="t", status="closed")


def test_task_valid_iso_due():
    assert Task(id=1, title="t", due="2026-12-01").due == "2026-12-01"


@pytest.mark.parametrize("due", ["01.12.2026", "2026-13-01", "not-a-date", "12/01/2026"])
def test_task_invalid_due_rejected(due):
    with pytest.raises(ValueError, match="срок"):
        Task(id=1, title="t", due=due)


# ---------------------------------------------------------------------------
# priority
# ---------------------------------------------------------------------------

def test_priority_sets():
    assert set(PRIORITIES) == {"low", "medium", "high"}


def test_normalize_priority():
    assert normalize_priority(" HIGH ") == "high"
    assert normalize_priority("Low") == "low"


def test_normalize_priority_invalid():
    with pytest.raises(ValueError):
        normalize_priority("urgent")


def test_is_valid_priority():
    assert is_valid_priority("medium")
    assert not is_valid_priority("nope")


def test_sort_by_priority_order():
    tasks = [
        Task(id=1, title="a", priority="low"),
        Task(id=2, title="b", priority="high"),
        Task(id=3, title="c", priority="medium"),
    ]
    ordered = [t.id for t in sort_by_priority(tasks)]
    assert ordered == [2, 3, 1]


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

def test_status_sets():
    assert set(STATUSES) == {"open", "done"}


def test_normalize_status():
    assert normalize_status(" DONE ") == "done"
    assert normalize_status("Open") == "open"


def test_normalize_status_invalid():
    with pytest.raises(ValueError):
        normalize_status("closed")


def test_is_valid_status():
    assert is_valid_status("open")
    assert not is_valid_status("archived")


def test_is_done():
    assert is_done(Task(id=1, title="t", status="done"))
    assert not is_done(Task(id=1, title="t", status="open"))


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

def test_search_case_insensitive_title():
    tasks = [
        Task(id=1, title="Купить молоко"),
        Task(id=2, title="Позвонить маме"),
    ]
    assert [t.id for t in filter_tasks(tasks, "МОЛОКО")] == [1]
    assert [t.id for t in filter_tasks(tasks, "маме")] == [2]


def test_search_empty_returns_all():
    tasks = [Task(id=1, title="a"), Task(id=2, title="b")]
    assert len(filter_tasks(tasks, "")) == 2


def test_search_no_match():
    tasks = [Task(id=1, title="Купить молоко")]
    assert filter_tasks(tasks, "zzz") == []


def test_search_matches_due_date():
    tasks = [
        Task(id=1, title="a", due="2026-12-01"),
        Task(id=2, title="b", due="2027-01-15"),
    ]
    assert [t.id for t in filter_tasks(tasks, "2026-12")] == [1]


# ---------------------------------------------------------------------------
# tasks (функции над списком: создание/добавление/обновление/удаление/статус)
# ---------------------------------------------------------------------------

def test_add_task_assigns_id():
    tasks = []
    t1 = add_task(tasks, "Первая")
    t2 = add_task(tasks, "Вторая")
    assert t1.id == 1 and t2.id == 2
    assert len(tasks) == 2
    assert t2.id != t1.id


def test_add_task_validates_title():
    with pytest.raises(ValueError):
        add_task([], "")


def test_update_task_changes_fields():
    tasks = []
    t = add_task(tasks, "Задача")
    updated = update_task(tasks, t.id, title="Новая", priority="high")
    assert updated.title == "Новая"
    assert updated.priority == "high"
    assert tasks[0].title == "Новая"


def test_update_task_without_id_rejected():
    tasks = [add_task([], "Задача")]
    with pytest.raises(ValueError):
        update_task(tasks, None, title="x")


def test_update_missing_task_not_found():
    tasks = [add_task([], "Задача")]
    with pytest.raises(KeyError):
        update_task(tasks, 999, title="x")


def test_mark_done_sets_status():
    tasks = []
    t = add_task(tasks, "Задача")
    done = mark_done(tasks, t.id)
    assert done.status == "done"
    assert is_done(tasks[0])


def test_mark_done_missing_task_not_found():
    with pytest.raises(KeyError):
        mark_done([], 1)


def test_delete_task_removes_it():
    tasks = []
    t = add_task(tasks, "Задача")
    delete_task(tasks, t.id)
    assert tasks == []


def test_delete_missing_task_not_found():
    with pytest.raises(KeyError):
        delete_task([], 1)


# ---------------------------------------------------------------------------
# storage (файловое хранилище ядра — без sqlite)
# ---------------------------------------------------------------------------

def test_storage_save_and_load_roundtrip():
    from src.core.storage import save_tasks, load_tasks

    tasks = [add_task([], "Купить молоко"), add_task([], "Позвонить маме")]
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "tasks.json")
        save_tasks(tasks, path)
        loaded = load_tasks(path)
    assert [t.title for t in loaded] == ["Купить молоко", "Позвонить маме"]


def test_storage_load_missing_file_returns_empty():
    from src.core.storage import load_tasks

    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "nope.json")
        assert load_tasks(path) == []


def test_storage_load_corrupted_file_raises():
    from src.core.storage import load_tasks, StorageError

    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "broken.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("{ не json")
        with pytest.raises(StorageError):
            load_tasks(path)