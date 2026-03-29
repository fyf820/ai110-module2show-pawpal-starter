import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import time
from pawpal_system import Pet, Task, Owner, Schedule, TimeSlot


def test_mark_complete_changes_status():
    """Calling mark_complete() should set the task's completed status to True."""
    task = Task(title="Walk Mochi", duration_minutes=30, priority="medium")

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_generate_respects_priority():
    """High priority tasks should be selected before low priority ones when time is tight."""
    pet = Pet(name="Mochi", species="Dog")
    owner = Owner(name="Sarah")

    high_task = Task(title="Give meds", duration_minutes=10, priority="high")
    low_task = Task(title="Bath time", duration_minutes=10, priority="low")
    pet.add_task(high_task)
    pet.add_task(low_task)
    owner.add_pet(pet)

    schedule = Schedule(date="2026-03-29", owner_id=owner.id)
    # Only 10 minutes available — only one task can fit
    schedule.generate(
        available_tasks=[task for p in owner.get_pets() for task in p.tasks],
        available_slots=[TimeSlot(start_time=time(9, 0), duration_minutes=10)],
    )

    selected = schedule.get_all_tasks(owner.get_pets())
    assert len(selected) == 1
    assert selected[0].priority == "high"


def test_add_task_increases_task_count():
    """Adding a task to a pet should increase its task count, and the schedule should reflect total time."""
    pet = Pet(name="Whiskers", species="Cat")
    owner = Owner(name="Sarah")

    task = Task(title="Feed Whiskers", duration_minutes=10, priority="high")
    pet.add_task(task)
    owner.add_pet(pet)

    schedule = Schedule(date="2026-03-29", owner_id=owner.id)
    schedule.generate(
        available_tasks=[task for p in owner.get_pets() for task in p.tasks],
        available_slots=[TimeSlot(start_time=time(9, 0), duration_minutes=60)],
    )

    selected = schedule.get_all_tasks(owner.get_pets())
    assert len(selected) == 1
    assert schedule.total_time == 10
