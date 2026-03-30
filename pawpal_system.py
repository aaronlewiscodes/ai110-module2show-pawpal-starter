from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Task:
    description: str
    due_datetime: datetime
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    frequency: Optional[str] = None  # None, "daily", or "weekly"
    is_complete: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_complete = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a new incomplete Task shifted by one frequency interval, or None if not recurring."""
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        return Task(
            description=self.description,
            due_datetime=self.due_datetime + delta,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
        )

    def edit(
        self,
        description: Optional[str] = None,
        due_datetime: Optional[datetime] = None,
        duration_minutes: Optional[int] = None,
        priority: Optional[str] = None,
        frequency: Optional[str] = None,
    ):
        """Update any subset of the task's fields, leaving others unchanged."""
        if description is not None:
            self.description = description
        if due_datetime is not None:
            self.due_datetime = due_datetime
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = priority
        if frequency is not None:
            self.frequency = frequency


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a specific task from this pet's task list."""
        self.tasks.remove(task)

    def list_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.is_complete]


@dataclass
class Owner:
    name: str
    email: str
    phone: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet):
        """Remove a specific pet from this owner's pet list."""
        self.pets.remove(pet)

    def list_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets


class Scheduler:
    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owners: list[Owner]):
        self.owners = owners

    def get_all_tasks_across_pets(self) -> list[Task]:
        """Collect and return every task from all pets across all owners."""
        tasks = []
        for owner in self.owners:
            for pet in owner.pets:
                tasks.extend(pet.tasks)
        return tasks

    def get_all_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks assigned to a specific pet."""
        return pet.list_tasks()

    def get_tasks_by_priority(self) -> list[Task]:
        """Return all tasks across pets sorted from highest to lowest priority."""
        return sorted(
            self.get_all_tasks_across_pets(),
            key=lambda t: self.PRIORITY_ORDER.get(t.priority, 99),
        )

    def get_tasks_by_due_time(self) -> list[Task]:
        """Return all tasks across pets sorted by due datetime ascending."""
        return sorted(self.get_all_tasks_across_pets(), key=lambda t: t.due_datetime)

    def check_conflicts(self) -> list[str]:
        """Return warning messages for any two pending tasks scheduled at the same datetime.

        Compares every pair of incomplete tasks across all pets/owners.
        Returns an empty list when no conflicts are found.
        """
        warnings = []
        pending = [
            (task, pet)
            for owner in self.owners
            for pet in owner.pets
            for task in pet.tasks
            if not task.is_complete
        ]
        for i in range(len(pending)):
            for j in range(i + 1, len(pending)):
                task_a, pet_a = pending[i]
                task_b, pet_b = pending[j]
                if task_a.due_datetime == task_b.due_datetime:
                    warnings.append(
                        f"WARNING: Conflict at {task_a.due_datetime.strftime('%I:%M %p')} — "
                        f'"{task_a.description}" ({pet_a.name}) conflicts with '
                        f'"{task_b.description}" ({pet_b.name})'
                    )
        return warnings

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        """Mark a task complete and, if it recurs, add the next occurrence to the pet.

        Returns the newly created Task if one was spawned, otherwise None.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return the given tasks sorted by due_datetime ascending."""
        return sorted(tasks, key=lambda t: t.due_datetime)

    def generate_daily_schedule(self, date: datetime.date) -> list[Task]:
        """Return pending tasks for the given date, sorted by priority then due time."""
        daily = [
            t
            for t in self.get_all_tasks_across_pets()
            if not t.is_complete and t.due_datetime.date() == date
        ]
        return sorted(
            daily,
            key=lambda t: (self.PRIORITY_ORDER.get(t.priority, 99), t.due_datetime),
        )

    def explain_schedule(self, date: datetime.date) -> str:
        """Return a human-readable schedule with ordering reasoning for the given date."""
        schedule = self.generate_daily_schedule(date)
        if not schedule:
            return "No pending tasks scheduled for this date."

        lines = [f"Schedule for {date} ({len(schedule)} tasks):\n"]
        for i, task in enumerate(schedule, 1):
            lines.append(
                f"{i}. [{task.priority.upper()}] {task.description} "
                f"— due {task.due_datetime.strftime('%I:%M %p')}, "
                f"{task.duration_minutes} min"
            )
        lines.append(
            "\nTasks are ordered by priority (high → medium → low), "
            "then by due time within each priority level."
        )
        return "\n".join(lines)
