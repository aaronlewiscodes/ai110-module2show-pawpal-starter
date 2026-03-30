from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def make_task(**kwargs):
    defaults = dict(
        description="Test task",
        due_datetime=datetime(2026, 3, 29, 9, 0),
        duration_minutes=15,
        priority="medium",
    )
    return Task(**{**defaults, **kwargs})


def make_scheduler(*pets):
    owner = Owner(name="Test Owner", email="t@t.com", phone="555-0000")
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owners=[owner])


def test_mark_complete_changes_status():
    task = make_task()
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(make_task(description="Morning walk"))
    pet.add_task(make_task(description="Evening walk"))
    assert len(pet.tasks) == 2


# --- Sorting correctness ---

def test_sort_by_time_returns_chronological_order():
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    t1 = make_task(description="Late task",  due_datetime=datetime(2026, 3, 29, 18, 0))
    t2 = make_task(description="Early task", due_datetime=datetime(2026, 3, 29,  7, 0))
    t3 = make_task(description="Mid task",   due_datetime=datetime(2026, 3, 29, 12, 0))
    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)
    scheduler = make_scheduler(pet)
    sorted_tasks = scheduler.sort_by_time(pet.list_tasks())
    due_times = [t.due_datetime for t in sorted_tasks]
    assert due_times == sorted(due_times)


# --- Recurrence logic ---

def test_daily_task_creates_next_day_occurrence():
    pet = Pet(name="Luna", species="cat", breed="Maine Coon", age=5)
    task = make_task(
        description="Feed Luna",
        due_datetime=datetime(2026, 3, 29, 8, 0),
        frequency="daily",
    )
    pet.add_task(task)
    scheduler = make_scheduler(pet)
    scheduler.mark_task_complete(pet, task)

    assert task.is_complete is True
    assert len(pet.tasks) == 2
    next_task = pet.tasks[1]
    assert next_task.due_datetime == datetime(2026, 3, 30, 8, 0)
    assert next_task.is_complete is False


def test_weekly_task_creates_next_week_occurrence():
    pet = Pet(name="Luna", species="cat", breed="Maine Coon", age=5)
    task = make_task(
        description="Flea treatment",
        due_datetime=datetime(2026, 3, 29, 9, 0),
        frequency="weekly",
    )
    pet.add_task(task)
    scheduler = make_scheduler(pet)
    scheduler.mark_task_complete(pet, task)

    next_task = pet.tasks[1]
    assert next_task.due_datetime == datetime(2026, 4, 5, 9, 0)


def test_non_recurring_task_does_not_spawn_new_task():
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    task = make_task(frequency=None)
    pet.add_task(task)
    scheduler = make_scheduler(pet)
    scheduler.mark_task_complete(pet, task)

    assert len(pet.tasks) == 1


# --- Conflict detection ---

def test_conflict_detected_for_same_pet():
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    shared_time = datetime(2026, 3, 29, 9, 0)
    pet.add_task(make_task(description="Walk",    due_datetime=shared_time))
    pet.add_task(make_task(description="Feeding", due_datetime=shared_time))
    scheduler = make_scheduler(pet)

    warnings = scheduler.check_conflicts()
    assert len(warnings) == 1
    assert "WARNING" in warnings[0]


def test_conflict_detected_across_different_pets():
    shared_time = datetime(2026, 3, 29, 7, 30)
    mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    luna  = Pet(name="Luna",  species="cat", breed="Maine Coon", age=5)
    mochi.add_task(make_task(description="Morning walk",    due_datetime=shared_time))
    luna.add_task( make_task(description="Vet check-in call", due_datetime=shared_time))
    scheduler = make_scheduler(mochi, luna)

    warnings = scheduler.check_conflicts()
    assert len(warnings) == 1
    assert "Mochi" in warnings[0]
    assert "Luna" in warnings[0]


def test_no_conflict_when_times_differ():
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    pet.add_task(make_task(description="Walk",    due_datetime=datetime(2026, 3, 29, 7, 0)))
    pet.add_task(make_task(description="Feeding", due_datetime=datetime(2026, 3, 29, 8, 0)))
    scheduler = make_scheduler(pet)

    assert scheduler.check_conflicts() == []


def test_completed_tasks_excluded_from_conflict_check():
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    shared_time = datetime(2026, 3, 29, 9, 0)
    t1 = make_task(description="Walk",    due_datetime=shared_time)
    t2 = make_task(description="Feeding", due_datetime=shared_time)
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    scheduler = make_scheduler(pet)

    assert scheduler.check_conflicts() == []
