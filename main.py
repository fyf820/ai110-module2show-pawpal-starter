from datetime import date, time
from pawpal_system import Owner, Pet, Task, Schedule, TimeSlot

# --- Setup ---
owner = Owner(
    name="Sarah",
    available_hours=[
        TimeSlot(start_time=time(9, 0),  duration_minutes=30),
        TimeSlot(start_time=time(10, 0), duration_minutes=30),
        TimeSlot(start_time=time(11, 0), duration_minutes=30),
    ],
    preferences={
        "preferred_tasks": ["walk"],
        "preferred_pets": ["Mochi"],
    },
)

pet1 = Pet(name="Mochi", species="Dog")
pet2 = Pet(name="Whiskers", species="Cat")

# --- Tasks: two intentionally overlap at 09:00 ---
pet1.add_task(Task(title="Walk Mochi",      duration_minutes=30, priority="medium",
                   start_time=Task.parse_start_time("9:00AM")))
pet1.add_task(Task(title="Groom Mochi",     duration_minutes=20, priority="low",
                   start_time=Task.parse_start_time("9:15AM")))   # overlaps Walk Mochi (09:00-09:30)
pet1.add_task(Task(title="Give Mochi meds", duration_minutes=5,  priority="high",
                   start_time=Task.parse_start_time("10:00AM")))
pet2.add_task(Task(title="Feed Whiskers",   duration_minutes=10, priority="high",
                   start_time=Task.parse_start_time("10:30AM")))
pet2.add_task(Task(title="Play Whiskers",   duration_minutes=15, priority="low",
                   start_time=Task.parse_start_time("11:00AM")))

owner.add_pet(pet1)
owner.add_pet(pet2)

# --- Generate schedule (90 min available) ---
all_tasks = [task for pet in owner.get_pets() for task in pet.tasks]

schedule = Schedule(date=str(date.today()), owner_id=owner.id)
schedule.generate(
    available_tasks=all_tasks,
    available_slots=owner.available_hours,
    owner_preferences=owner.preferences,
)
owner.add_schedule(schedule)

# --- Print schedule ---
print("=== Today's Schedule ===")
print(f"Owner : {owner}")
print(f"Pets  : {', '.join(str(p) for p in owner.get_pets())}")
print()
print(schedule)
print()
print("Tasks included:")
for task in schedule.get_all_tasks(owner.get_pets()):
    start = task.start_time.strftime("%H:%M") if task.start_time else "no time set"
    print(f"  - {task}  [starts {start}]")

# --- Conflict detection ---
print()
print("=== Conflict Detection ===")
warnings = schedule.detect_conflicts(owner.get_pets(), available_slots=owner.available_hours)
for w in warnings:
    print(w)
