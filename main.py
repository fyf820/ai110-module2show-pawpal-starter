from datetime import date
from pawpal_system import Owner, Pet, Task, Schedule

# --- Setup ---
owner = Owner(
    name="Sarah",
    available_hours=["09:00", "10:00", "11:00"],
    preferences={
        "preferred_tasks": ["walk"],
        "preferred_pets": ["Mochi"],
    },
)

pet1 = Pet(name="Mochi", species="Dog")
pet2 = Pet(name="Whiskers", species="Cat")
owner.add_pet(pet1)
owner.add_pet(pet2)

# --- Tasks ---
tasks = [
    Task(title="Walk Mochi",        duration_minutes=30, priority="medium"),
    Task(title="Feed Whiskers",     duration_minutes=10, priority="high"),
    Task(title="Groom Mochi",       duration_minutes=20, priority="low"),
    Task(title="Give Mochi meds",   duration_minutes=5,  priority="high"),
]

# --- Generate schedule (90 min available) ---
schedule = Schedule(
    date=str(date.today()),
    pet_id=pet1.id,
    owner_id=owner.id,
)
schedule.generate(
    available_tasks=tasks,
    available_minutes=90,
    owner_preferences=owner.preferences,
)
owner.add_schedule(schedule)

# --- Print ---
print("=== Today's Schedule ===")
print(f"Owner : {owner}")
print(f"Pets  : {pet1}, {pet2}")
print()
print(schedule)
print()
print("Tasks included:")
for task in schedule.tasks:
    print(f"  - {task}")
