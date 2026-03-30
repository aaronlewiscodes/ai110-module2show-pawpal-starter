from datetime import datetime, date
from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup ---
today = date.today()

owner = Owner(name="Jordan", email="jordan@email.com", phone="555-1234")

mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
luna = Pet(name="Luna", species="cat", breed="Maine Coon", age=5)

# --- Tasks for Mochi ---
mochi.add_task(Task(
    description="Morning walk",
    due_datetime=datetime(today.year, today.month, today.day, 7, 30),
    duration_minutes=30,
    priority="high",
))
mochi.add_task(Task(
    description="Flea medication",
    due_datetime=datetime(today.year, today.month, today.day, 9, 0),
    duration_minutes=5,
    priority="medium",
))

# --- Tasks for Luna ---
luna.add_task(Task(
    description="Clean litter box",
    due_datetime=datetime(today.year, today.month, today.day, 8, 0),
    duration_minutes=10,
    priority="high",
))
luna.add_task(Task(
    description="Brush coat",
    due_datetime=datetime(today.year, today.month, today.day, 18, 0),
    duration_minutes=15,
    priority="low",
))
# Intentional conflict: same time as Mochi's "Morning walk"
luna.add_task(Task(
    description="Vet check-in call",
    due_datetime=datetime(today.year, today.month, today.day, 7, 30),
    duration_minutes=10,
    priority="medium",
))

# --- Wire up owner and scheduler ---
owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owners=[owner])

# --- Check for scheduling conflicts ---
conflicts = scheduler.check_conflicts()
if conflicts:
    for warning in conflicts:
        print(warning)
else:
    print("No scheduling conflicts detected.")

print()

# --- Print today's schedule ---
print(scheduler.explain_schedule(today))
