from datetime import datetime, date
import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session state bootstrap ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []

# --- Owner + Pet info ---
st.subheader("Owner & Pet Info")

with st.form("owner_form"):
    owner_name = st.text_input("Owner name", value="Jordan")
    email = st.text_input("Email", value="jordan@email.com")
    phone = st.text_input("Phone", value="555-1234")
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed", value="Shiba Inu")
    age = st.number_input("Age", min_value=0, max_value=30, value=3)
    submitted = st.form_submit_button("Save Owner & Pet")

if submitted:
    pet = Pet(name=pet_name, species=species, breed=breed, age=int(age))
    owner = Owner(name=owner_name, email=email, phone=phone)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pets = owner.list_pets()
    st.success(f"Saved {owner_name} with pet {pet_name}!")

st.divider()

# --- Add tasks ---
st.subheader("Add a Task")

if not st.session_state.pets:
    st.info("Save an owner and pet above before adding tasks.")
else:
    pet_names = [p.name for p in st.session_state.pets]

    with st.form("task_form"):
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
        description = st.text_input("Task description", value="Morning walk")
        due_time = st.time_input("Due time", value=datetime(2026, 1, 1, 8, 0).time())
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Frequency", ["none", "daily", "weekly"])
        add_task = st.form_submit_button("Add Task")

    if add_task:
        due_dt = datetime.combine(date.today(), due_time)
        task = Task(
            description=description,
            due_datetime=due_dt,
            duration_minutes=int(duration),
            priority=priority,
            frequency=None if frequency == "none" else frequency,
        )
        pet = next(p for p in st.session_state.pets if p.name == selected_pet_name)
        pet.add_task(task)
        st.success(f"Added '{description}' to {selected_pet_name}.")

    # Display tasks per pet sorted by due time
    scheduler = Scheduler(owners=[st.session_state.owner])

    for pet in st.session_state.pets:
        tasks = pet.list_tasks()
        if tasks:
            sorted_tasks = scheduler.sort_by_time(tasks)
            st.markdown(f"**{pet.name}'s tasks** (sorted by due time):")
            st.table([
                {
                    "Description": t.description,
                    "Due": t.due_datetime.strftime("%I:%M %p"),
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.capitalize(),
                    "Frequency": t.frequency or "—",
                    "Done": "✓" if t.is_complete else "",
                }
                for t in sorted_tasks
            ])

st.divider()

# --- Generate schedule ---
st.subheader("Generate Today's Schedule")

if st.button("Generate schedule"):
    if not st.session_state.owner:
        st.warning("No owner set up yet. Fill in the form above first.")
    else:
        scheduler = Scheduler(owners=[st.session_state.owner])

        # Conflict warnings
        conflicts = scheduler.check_conflicts()
        if conflicts:
            for msg in conflicts:
                st.warning(msg)
        else:
            st.success("No scheduling conflicts detected.")

        # Today's schedule as a table
        schedule = scheduler.generate_daily_schedule(date.today())
        if schedule:
            st.markdown(f"**Today's schedule — {len(schedule)} task(s):**")
            st.table([
                {
                    "Priority": t.priority.upper(),
                    "Description": t.description,
                    "Due": t.due_datetime.strftime("%I:%M %p"),
                    "Duration (min)": t.duration_minutes,
                    "Frequency": t.frequency or "—",
                }
                for t in schedule
            ])
            st.caption(
                "Tasks are ordered by priority (HIGH → MEDIUM → LOW), "
                "then by due time within each priority level."
            )
        else:
            st.info("No pending tasks scheduled for today.")
