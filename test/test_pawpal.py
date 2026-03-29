import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task, Owner, Schedule


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
    schedule = Schedule(date="2026-03-29", pet_id=pet.id, owner_id=owner.id)

    high_task = Task(title="Give meds", duration_minutes=10, priority="high")
    low_task = Task(title="Bath time", duration_minutes=10, priority="low")

    # Only 10 minutes available — only one task can fit
    schedule.generate(available_tasks=[low_task, high_task], available_minutes=10)

    assert len(schedule.tasks) == 1
    assert schedule.tasks[0].priority == "high"


def test_add_task_increases_task_count():
    """Adding a task to a schedule should increase its task count and total time."""
    pet = Pet(name="Whiskers", species="Cat")
    owner = Owner(name="Sarah")
    schedule = Schedule(date="2026-03-29", pet_id=pet.id, owner_id=owner.id)

    task = Task(title="Feed Whiskers", duration_minutes=10, priority="high")
    schedule.add_task(task)

    assert len(schedule.tasks) == 1
    assert schedule.total_time == 10
