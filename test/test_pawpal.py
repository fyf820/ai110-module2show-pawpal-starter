import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, time, timedelta
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


# --- Sorting Correctness ---

def test_sort_by_time_orders_shortest_first():
    """sort_by_time should order selected tasks from shortest to longest duration."""
    pet = Pet(name="Mochi", species="Dog")
    owner = Owner(name="Sarah")

    short_task = Task(title="Quick brush", duration_minutes=5, priority="low")
    medium_task = Task(title="Feed", duration_minutes=15, priority="low")
    long_task = Task(title="Long walk", duration_minutes=45, priority="low")
    pet.add_task(short_task)
    pet.add_task(long_task)   # added out of order intentionally
    pet.add_task(medium_task)
    owner.add_pet(pet)

    schedule = Schedule(date="2026-03-29", owner_id=owner.id)
    schedule.generate(
        available_tasks=pet.tasks,
        available_slots=[TimeSlot(start_time=time(9, 0), duration_minutes=120)],
    )
    schedule.sort_by_time(owner.get_pets())

    sorted_tasks = schedule.get_all_tasks(owner.get_pets())
    durations = [t.duration_minutes for t in sorted_tasks]
    assert durations == sorted(durations), f"Expected ascending order, got {durations}"


# --- Recurrence Logic ---

def test_daily_recurring_task_creates_next_day_occurrence():
    """Completing a daily recurring task should mark it done and append a new task due the following day."""
    due = date(2026, 3, 29)
    task = Task(title="Give meds", duration_minutes=10, priority="high", frequency="daily", due_date=due)
    pet = Pet(name="Mochi", species="Dog")
    pet.add_task(task)

    pet.complete_task(task.id)

    original = next(t for t in pet.tasks if t.id == task.id)
    assert original.completed is True

    new_tasks = [t for t in pet.tasks if t.id != task.id]
    assert len(new_tasks) == 1
    assert new_tasks[0].due_date == due + timedelta(days=1)
    assert new_tasks[0].completed is False


def test_non_recurring_task_does_not_spawn_next_occurrence():
    """Completing a one-off task should not add any new tasks to the pet."""
    task = Task(title="One-time vet visit", duration_minutes=60, priority="high")
    pet = Pet(name="Mochi", species="Dog")
    pet.add_task(task)

    pet.complete_task(task.id)

    assert len(pet.tasks) == 1
    assert pet.tasks[0].completed is True


# --- Conflict Detection ---

def test_conflict_detected_for_same_start_time():
    """Two tasks with the same start time should be flagged as overlapping."""
    pet = Pet(name="Mochi", species="Dog")
    owner = Owner(name="Sarah")

    task_a = Task(title="Walk", duration_minutes=30, priority="high", start_time=time(9, 0))
    task_b = Task(title="Bath", duration_minutes=20, priority="medium", start_time=time(9, 0))
    pet.add_task(task_a)
    pet.add_task(task_b)
    owner.add_pet(pet)

    schedule = Schedule(date="2026-03-29", owner_id=owner.id)
    schedule.selected_task_ids = [task_a.id, task_b.id]

    warnings = schedule.detect_conflicts(
        owner.get_pets(),
        available_slots=[TimeSlot(start_time=time(9, 0), duration_minutes=60)],
    )
    assert any("overlaps" in w for w in warnings)


def test_conflict_detected_when_task_outside_available_slot():
    """A task scheduled outside the owner's available window should produce an overrun warning."""
    pet = Pet(name="Mochi", species="Dog")
    owner = Owner(name="Sarah")

    # Slot is 09:00–09:30; task is at 14:00
    task = Task(title="Afternoon walk", duration_minutes=20, priority="medium", start_time=time(14, 0))
    pet.add_task(task)
    owner.add_pet(pet)

    schedule = Schedule(date="2026-03-29", owner_id=owner.id)
    schedule.selected_task_ids = [task.id]

    warnings = schedule.detect_conflicts(
        owner.get_pets(),
        available_slots=[TimeSlot(start_time=time(9, 0), duration_minutes=30)],
    )
    assert any("does not fit" in w for w in warnings)


# --- Edge Cases ---

def test_pet_with_no_tasks_produces_empty_schedule():
    """A pet with no tasks should yield an empty schedule with zero total time."""
    pet = Pet(name="Mochi", species="Dog")
    owner = Owner(name="Sarah")
    owner.add_pet(pet)

    schedule = Schedule(date="2026-03-29", owner_id=owner.id)
    schedule.generate(
        available_tasks=[],
        available_slots=[TimeSlot(start_time=time(9, 0), duration_minutes=60)],
    )

    assert schedule.get_all_tasks(owner.get_pets()) == []
    assert schedule.total_time == 0


# --- occurs_on Logic ---

def test_occurs_on_one_time_exact_date():
    """A one-time task should only occur on its due date."""
    due = date(2026, 3, 29)
    task = Task(title="Vet visit", duration_minutes=60, priority="high", due_date=due)
    assert task.occurs_on(due) is True
    assert task.occurs_on(date(2026, 3, 30)) is False


def test_occurs_on_daily_on_and_after_due():
    """A daily task should occur on its due date and any date after."""
    due = date(2026, 3, 29)
    task = Task(title="Feed", duration_minutes=10, priority="medium", frequency="daily", due_date=due)
    assert task.occurs_on(due) is True
    assert task.occurs_on(date(2026, 3, 30)) is True
    assert task.occurs_on(date(2026, 3, 28)) is False


def test_occurs_on_weekly_same_weekday():
    """A weekly task should occur on its due date and future dates sharing the same weekday."""
    due = date(2026, 3, 29)  # Sunday
    task = Task(title="Bath", duration_minutes=30, priority="low", frequency="weekly", due_date=due)
    assert task.occurs_on(due) is True                    # same Sunday
    assert task.occurs_on(date(2026, 4, 5)) is True       # next Sunday
    assert task.occurs_on(date(2026, 3, 30)) is False     # Monday
    assert task.occurs_on(date(2026, 3, 28)) is False     # before due date
