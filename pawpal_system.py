"""
PawPal+ System
Core classes for pet care planning and scheduling.
"""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from itertools import combinations
from typing import List, Dict, Optional


@dataclass
class TimeSlot:
    """Represents a block of time the owner is available."""
    start_time: time
    duration_minutes: int


@dataclass
class Task:
    """Represents a pet care task."""
    title: str
    duration_minutes: int
    priority: str
    completed: bool = False
    frequency: Optional[str] = None  # "daily", "weekly", or None
    due_date: Optional[date] = None
    start_time: Optional[time] = None  # e.g. time(9, 0) for 09:00, or use parse_start_time("9:00AM")
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @staticmethod
    def parse_start_time(value: str) -> time:
        """Parse a time string into a datetime.time object. Accepts '9:00AM', '09:00', '14:50'."""
        for fmt in ("%I:%M%p", "%I:%M %p", "%H:%M"):
            try:
                return datetime.strptime(value.strip().upper(), fmt).time()
            except ValueError:
                continue
        raise ValueError(f"Unrecognised time format: '{value}'. Use '9:00AM' or '14:50'.")

    def update_title(self, new_title: str) -> None:
        """Update the task's title."""
        self.title = new_title

    def update_duration(self, new_duration: int) -> None:
        """Update the task's duration in minutes."""
        self.duration_minutes = new_duration

    def update_priority(self, new_priority: str) -> None:
        """Update the task's priority (low/medium/high)."""
        self.priority = new_priority

    def update_start_time(self, new_start_time) -> None:
        """Update the task's start time. Accepts a datetime.time or a string like '9:00AM' or '14:50'."""
        if isinstance(new_start_time, str):
            self.start_time = Task.parse_start_time(new_start_time)
        else:
            self.start_time = new_start_time

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def occurs_on(self, target: date) -> bool:
        """Return True if this task should appear on the given date."""
        if self.frequency is None:
            return self.due_date == target
        if self.frequency == "daily":
            return self.due_date is None or target >= self.due_date
        if self.frequency == "weekly":
            if self.due_date is None:
                return True
            return target >= self.due_date and target.weekday() == self.due_date.weekday()
        return False

    def next_occurrence(self) -> Optional["Task"]:
        """Return a new Task instance for the next occurrence, or None if not recurring."""
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        base = self.due_date if self.due_date else date.today()
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            due_date=base + delta,
        )

    def __str__(self) -> str:
        """Return a readable string representation."""
        return f"{self.title} ({self.priority} priority) — {self.duration_minutes} min"


@dataclass
class Pet:
    """Represents a pet with care needs."""
    name: str
    species: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a care task from this pet by ID."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def complete_task(self, task_id: str) -> None:
        """Mark a task complete and auto-add the next occurrence if it is recurring."""
        for task in self.tasks:
            if task.id == task_id:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task:
                    self.tasks.append(next_task)
                break

    def update_name(self, new_name: str) -> None:
        """Update the pet's name."""
        self.name = new_name

    def update_species(self, new_species: str) -> None:
        """Update the pet's species."""
        self.species = new_species

    def __str__(self) -> str:
        """Return a readable string representation."""
        return f"{self.name} ({self.species})"


class Owner:
    """Represents a pet owner."""

    def __init__(
        self,
        name: str,
        available_hours: Optional[List[TimeSlot]] = None,
        preferences: Optional[Dict] = None
    ):
        """Initialize an owner with name, availability, and preferences."""
        self.id = str(uuid.uuid4())
        self.name = name
        self.available_hours: List[TimeSlot] = available_hours or []
        self.preferences = {"preferred_tasks": [], "preferred_pets": []}
        if preferences:
            self.preferences["preferred_tasks"] = preferences.get("preferred_tasks", [])
            self.preferences["preferred_pets"] = preferences.get("preferred_pets", [])
        self.pets: List[Pet] = []
        self.schedules: List[str] = []  # Store schedule IDs

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        if not any(p.id == pet.id for p in self.pets):
            self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet from the owner's pet list by ID."""
        self.pets = [p for p in self.pets if p.id != pet_id]

    def add_schedule(self, schedule: "Schedule") -> None:
        """Add a schedule to the owner's schedule list."""
        if schedule.id not in self.schedules:
            self.schedules.append(schedule.id)

    def remove_schedule(self, schedule_id: str) -> None:
        """Remove a schedule ID from the owner's schedule list."""
        if schedule_id in self.schedules:
            self.schedules.remove(schedule_id)

    def get_pets(self) -> List[Pet]:
        """Return list of pets owned by this owner."""
        return self.pets

    def get_schedules(self) -> List[str]:
        """Return list of schedule IDs created by this owner."""
        return self.schedules

    def update_available_hours(self, hours: List[TimeSlot]) -> None:
        """Update the owner's available hours."""
        self.available_hours = hours

    def update_preferences(self, new_preferences: Dict) -> None:
        """Update the owner's care preferences."""
        self.preferences["preferred_tasks"] = new_preferences.get("preferred_tasks", [])
        self.preferences["preferred_pets"] = new_preferences.get("preferred_pets", [])

    def __str__(self) -> str:
        """Return a readable string representation."""
        return f"{self.name} — {len(self.pets)} pet(s), {len(self.schedules)} schedule(s)"


class Schedule:
    """Represents a daily pet care schedule/plan."""

    def __init__(
        self,
        date: str,
        owner_id: str,
        explanation: str = ""
    ):
        """Initialize a schedule for a specific date."""
        self.id = str(uuid.uuid4())
        self.date = date
        self.owner_id = owner_id
        self.selected_task_ids: List[str] = []
        self.total_time = 0
        self.explanation = explanation

    def get_all_tasks(self, pets: List[Pet]) -> List[Task]:
        """Return all selected Task objects across any number of pets, in selected_task_ids order."""
        task_map = {task.id: task for pet in pets for task in pet.tasks}
        return [task_map[tid] for tid in self.selected_task_ids if tid in task_map]

    def filter_tasks(self, pets: List[Pet], completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Return selected tasks filtered by completion status and/or pet name."""
        pet_map = {pet.name.lower(): pet for pet in pets}
        if pet_name is not None:
            matched_pet = pet_map.get(pet_name.lower())
            id_set = set(self.selected_task_ids) & {t.id for t in matched_pet.tasks} if matched_pet else set()
        else:
            id_set = set(self.selected_task_ids)

        tasks = [task for pet in pets for task in pet.tasks if task.id in id_set]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def sort_by_time(self, pets: List[Pet]) -> None:
        """Sort selected task IDs by duration_minutes (shortest first), regardless of which pet they belong to."""
        task_map = {task.id: task for pet in pets for task in pet.tasks}
        self.selected_task_ids.sort(key=lambda tid: task_map[tid].duration_minutes)

    def detect_conflicts(self, pets: List[Pet], available_slots: List[TimeSlot]) -> List[str]:
        """Check selected tasks with a start_time for overlaps and overruns. Returns a list of warning strings."""
        task_map = {task.id: task for pet in pets for task in pet.tasks}
        pet_of = {task.id: pet for pet in pets for task in pet.tasks}
        warnings = []
        _base = date.today()

        def to_dt(t: time) -> datetime:
            return datetime.combine(_base, t)

        # Pre-compute intervals for tasks and slots (each to_dt call happens exactly once)
        task_intervals = {
            task.id: (to_dt(task.start_time), to_dt(task.start_time) + timedelta(minutes=task.duration_minutes))
            for task in (task_map[tid] for tid in self.selected_task_ids if tid in task_map)
            if task.start_time is not None
        }
        timed_tasks = [task_map[tid] for tid in self.selected_task_ids if tid in task_intervals]

        slot_intervals = [
            (to_dt(slot.start_time), to_dt(slot.start_time) + timedelta(minutes=slot.duration_minutes))
            for slot in available_slots
        ]
        slot_summary = ", ".join(
            f"{slot.start_time.strftime('%H:%M')}+{slot.duration_minutes}min"
            for slot in available_slots
        ) or "none"

        # Overlap check
        for a, b in combinations(timed_tasks, 2):
            a_start, a_end = task_intervals[a.id]
            b_start, b_end = task_intervals[b.id]
            if a_start < b_end and b_start < a_end:
                name_a = pet_of[a.id].name if a.id in pet_of else "?"
                name_b = pet_of[b.id].name if b.id in pet_of else "?"
                warnings.append(
                    f"WARNING: '{a.title}' ({name_a}, {a_start.strftime('%H:%M')}-{a_end.strftime('%H:%M')}) "
                    f"overlaps '{b.title}' ({name_b}, {b_start.strftime('%H:%M')}-{b_end.strftime('%H:%M')})."
                )

        # Overrun check: each timed task must fit within at least one owner TimeSlot
        for task in timed_tasks:
            task_start, task_end = task_intervals[task.id]
            if not any(s <= task_start and task_end <= e for s, e in slot_intervals):
                warnings.append(
                    f"WARNING: '{task.title}' "
                    f"({task_start.strftime('%H:%M')}-{task_end.strftime('%H:%M')}) "
                    f"does not fit within any available slot ({slot_summary})."
                )

        return warnings if warnings else ["No conflicts detected."]

    def update_date(self, new_date: str) -> None:
        """Update the schedule's date."""
        self.date = new_date

    def update_explanation(self, new_explanation: str) -> None:
        """Update the explanation for this schedule."""
        self.explanation = new_explanation

    def generate(self, available_tasks: List[Task], available_slots: List[TimeSlot], owner_preferences: Optional[Dict] = None) -> None:
        """Select task IDs into the schedule based on priority, preferences, and available time."""
        total_minutes = sum(slot.duration_minutes for slot in available_slots)
        priority_order = {"high": 3, "medium": 2, "low": 1}
        preferred_tasks = (owner_preferences or {}).get("preferred_tasks", [])
        preferred_pets = (owner_preferences or {}).get("preferred_pets", [])

        def sort_key(task: Task):
            priority_score = priority_order.get(task.priority, 0)
            title_lower = task.title.lower()
            preference_score = 0
            if any(t.lower() in title_lower for t in preferred_tasks):
                preference_score += 2
            if any(p.lower() in title_lower for p in preferred_pets):
                preference_score += 1
            # Earlier start time wins tiebreaks; tasks with no start_time sort last
            start_min = (
                task.start_time.hour * 60 + task.start_time.minute
                if task.start_time is not None
                else float("inf")
            )
            return (priority_score, preference_score, -start_min)

        def to_min(t: time) -> int:
            return t.hour * 60 + t.minute

        def conflicts_with_selected(task: Task, selected_intervals: list) -> bool:
            """Return True if task's time window overlaps any already-selected timed interval."""
            if task.start_time is None:
                return False
            t_start = to_min(task.start_time)
            t_end = t_start + task.duration_minutes
            return any(t_start < sel_end and sel_start < t_end for sel_start, sel_end in selected_intervals)

        sorted_tasks = sorted(available_tasks, key=sort_key, reverse=True)
        self.selected_task_ids = []
        selected_intervals: list = []  # (start_min, end_min) for timed tasks already selected
        remaining = total_minutes
        reasons = []
        for task in sorted_tasks:
            if task.duration_minutes > remaining:
                continue
            if conflicts_with_selected(task, selected_intervals):
                continue
            self.selected_task_ids.append(task.id)
            remaining -= task.duration_minutes
            if task.start_time is not None:
                t_start = to_min(task.start_time)
                selected_intervals.append((t_start, t_start + task.duration_minutes))
            title_lower = task.title.lower()
            if any(t.lower() in title_lower for t in preferred_tasks):
                reasons.append(f"{task.title} (owner preferred task)")
            elif any(p.lower() in title_lower for p in preferred_pets):
                reasons.append(f"{task.title} (owner preferred pet)")
            else:
                reasons.append(f"{task.title} ({task.priority} priority)")
        self.total_time = total_minutes - remaining
        self.explanation = "Tasks selected: " + ", ".join(reasons) if reasons else "No tasks could fit in the available time."

    def __str__(self) -> str:
        """Return a readable string representation."""
        return (
            f"Schedule {self.date} — {len(self.selected_task_ids)} task(s), {self.total_time} min total\n"
            f"Explanation: {self.explanation}"
        )
