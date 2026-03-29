"""
PawPal+ System
Core classes for pet care planning and scheduling.
"""

import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Pet:
    """Represents a pet with care needs."""
    name: str
    species: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def update_name(self, new_name: str) -> None:
        """Update the pet's name."""
        self.name = new_name

    def update_species(self, new_species: str) -> None:
        """Update the pet's species."""
        self.species = new_species

    def __str__(self) -> str:
        """Return a readable string representation."""
        return f"{self.name} ({self.species})"


@dataclass
class Task:
    """Represents a pet care task."""
    title: str
    duration_minutes: int
    priority: str
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def update_title(self, new_title: str) -> None:
        """Update the task's title."""
        self.title = new_title

    def update_duration(self, new_duration: int) -> None:
        """Update the task's duration in minutes."""
        self.duration_minutes = new_duration

    def update_priority(self, new_priority: str) -> None:
        """Update the task's priority (low/medium/high)."""
        self.priority = new_priority

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def __str__(self) -> str:
        """Return a readable string representation."""
        return f"{self.title} ({self.priority} priority) — {self.duration_minutes} min"


class Owner:
    """Represents a pet owner."""

    def __init__(
        self,
        name: str,
        available_hours: Optional[List[str]] = None,
        preferences: Optional[Dict] = None
    ):
        """Initialize an owner with name, availability, and preferences."""
        self.id = str(uuid.uuid4())
        self.name = name
        self.available_hours = available_hours or []
        self.preferences = {"preferred_tasks": [], "preferred_pets": []}
        if preferences:
            self.preferences["preferred_tasks"] = preferences.get("preferred_tasks", [])
            self.preferences["preferred_pets"] = preferences.get("preferred_pets", [])
        self.pets: List[str] = []  # Store pet IDs
        self.schedules: List[str] = []  # Store schedule IDs

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        if pet.id not in self.pets:
            self.pets.append(pet.id)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet ID from the owner's pet list."""
        if pet_id in self.pets:
            self.pets.remove(pet_id)

    def add_schedule(self, schedule: "Schedule") -> None:
        """Add a schedule to the owner's schedule list."""
        if schedule.id not in self.schedules:
            self.schedules.append(schedule.id)

    def remove_schedule(self, schedule_id: str) -> None:
        """Remove a schedule ID from the owner's schedule list."""
        if schedule_id in self.schedules:
            self.schedules.remove(schedule_id)

    def get_pets(self) -> List[str]:
        """Return list of pet IDs owned by this owner."""
        return self.pets

    def get_schedules(self) -> List[str]:
        """Return list of schedule IDs created by this owner."""
        return self.schedules

    def update_available_hours(self, hours: List[str]) -> None:
        "Update the owner's available hours."
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
        pet_id: str,
        owner_id: str,
        tasks: Optional[List[Task]] = None,
        explanation: str = ""
    ):
        """Initialize a schedule for a specific date and pet."""
        self.id = str(uuid.uuid4())
        self.date = date
        self.pet_id = pet_id
        self.owner_id = owner_id
        self.tasks = tasks or []
        self.total_time = 0
        self.explanation = explanation

    def add_task(self, task: Task) -> None:
        """Add a task to the schedule."""
        self.tasks.append(task)
        self.total_time += task.duration_minutes

    def remove_task(self, task_id: str) -> None:
        """Remove a task by ID from the schedule."""
        for task in self.tasks:
            if task.id == task_id:
                self.tasks.remove(task)
                self.total_time -= task.duration_minutes
                break

    def update_date(self, new_date: str) -> None:
        """Update the schedule's date."""
        self.date = new_date

    def update_explanation(self, new_explanation: str) -> None:
        """Update the explanation for this schedule."""
        self.explanation = new_explanation

    def generate(self, available_tasks: List[Task], available_minutes: int, owner_preferences: Optional[Dict] = None) -> None:
        """Select and order tasks into the schedule based on priority, preferences, and available time."""
        priority_order = {"high": 3, "medium": 2, "low": 1}
        preferred_tasks = (owner_preferences or {}).get("preferred_tasks", [])
        preferred_pets = (owner_preferences or {}).get("preferred_pets", [])

        def sort_key(task: Task):
            priority_score = priority_order.get(task.priority, 0)
            title_lower = task.title.lower()
            is_preferred = (
                any(t.lower() in title_lower for t in preferred_tasks) or
                any(p.lower() in title_lower for p in preferred_pets)
            )
            return (priority_score, int(is_preferred))

        sorted_tasks = sorted(available_tasks, key=sort_key, reverse=True)
        self.tasks = []
        remaining = available_minutes
        reasons = []
        for task in sorted_tasks:
            if task.duration_minutes <= remaining:
                self.tasks.append(task)
                remaining -= task.duration_minutes
                title_lower = task.title.lower()
                if any(t.lower() in title_lower for t in preferred_tasks):
                    reasons.append(f"{task.title} (owner preferred task)")
                elif any(p.lower() in title_lower for p in preferred_pets):
                    reasons.append(f"{task.title} (owner preferred pet)")
                else:
                    reasons.append(f"{task.title} ({task.priority} priority)")
        self.total_time = available_minutes - remaining
        self.explanation = "Tasks selected: " + ", ".join(reasons) if reasons else "No tasks could fit in the available time."

    def __str__(self) -> str:
        """Return a readable string representation."""
        return (
            f"Schedule {self.date} — {len(self.tasks)} task(s), {self.total_time} min total\n"
            f"Explanation: {self.explanation}"
        )
