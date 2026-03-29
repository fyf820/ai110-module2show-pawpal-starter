import streamlit as st
from pawpal_system import Owner, Pet, Task, Schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner & Pet Info")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
available_minutes = st.number_input("Available minutes today", min_value=10, max_value=480, value=60)

if st.button("Save owner & pet"):
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(st.session_state.pet)
    st.success(f"Saved {owner_name} with pet {pet_name}.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if "pet" not in st.session_state:
        st.warning("Please save owner & pet info first.")
    else:
        task = Task(title=task_title, duration_minutes=int(duration), priority=priority)
        st.session_state.pet.add_task(task)
        st.session_state.tasks.append(
            {"title": task_title, "duration_minutes": int(duration), "priority": priority}
        )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button calls your scheduling logic.")

if st.button("Generate schedule"):
    if "owner" not in st.session_state or "pet" not in st.session_state:
        st.warning("Please save owner & pet info first.")
    elif not st.session_state.tasks:
        st.warning("Please add at least one task first.")
    else:
        owner = st.session_state.owner
        all_tasks = [task for pet in owner.get_pets() for task in pet.tasks]
        schedule = Schedule(
            date=str(st.session_state.get("date", "today")),
            owner_id=owner.id,
        )
        schedule.generate(
            available_tasks=all_tasks,
            available_minutes=int(available_minutes),
            owner_preferences=owner.preferences,
        )
        owner.add_schedule(schedule)
        st.session_state.schedule = schedule

if "schedule" in st.session_state:
    s = st.session_state.schedule
    st.success(f"Schedule generated: {len(s.selected_task_ids)} task(s), {s.total_time} min total")
    st.markdown(f"**Explanation:** {s.explanation}")
    st.markdown("**Tasks:**")
    for task in s.get_all_tasks(st.session_state.owner.get_pets()):
        st.write(f"- {task}")
