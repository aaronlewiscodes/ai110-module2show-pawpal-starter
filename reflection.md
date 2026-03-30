# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Some actions the app needs
1. Adding Medications the Pet has taken
2. Adding a Walk that the Pet has been on
3. Adding a meal the Pet has ate 

Structure: Three-level hierarchy — Owner holds Pets, Pets hold Tasks — with Scheduler sitting above it all managing owners.

Relationships:

Owner 1→many Pet (owns)
Pet 1→many Task (has)
Scheduler 1→many Owner (manages)
Division of responsibility: Owner, Pet, and Task are pure data models with basic CRUD methods. Scheduler is the only class with business logic — it aggregates tasks across all pets, prioritizes them, and generates + explains the daily plan.

Classes I created and each responsibility they have:
Owner
Represents the person using the app. Stores contact info and acts as the top-level container for a user's pets. Responsible for managing (adding/removing/listing) the pets they own.

Pet
Represents an individual animal. Stores identifying info (species, breed, age) and owns a collection of tasks specific to that pet. Responsible for managing its own task list and filtering tasks by status (e.g., pending).

Task
The core unit of work. Stores what needs to be done, when, how long it takes, how urgent it is, and whether it's been completed. Responsible for its own state — marking itself complete and allowing edits to its own fields.

Scheduler
The "brain" of the app. Has visibility across all owners and their pets. Responsible for aggregating tasks, applying sorting/prioritization logic, generating a coherent daily plan, and explaining the reasoning behind that plan. It's the only class that works across pet boundaries.

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

Based on the current implementation, the scheduler considers two constraints:

Priority — tasks are ordered high → medium → low in generate_daily_schedule and get_tasks_by_priority.
Time — tasks are filtered by due_datetime.date() for a given day, then sorted by due_datetime as a tiebreaker within the same priority level.

As directed by the instructions I thought these two criteria were most important.


**b. Tradeoffs**

The conflict detection is O(n²) — it checks every task pair. That's fine for a handful of pets, but if you had hundreds of tasks it would slow down noticeably. A faster approach would be to group tasks by due_datetime using a dict, which would be O(n). For our scenario with a small amount of data it is ok. 


---

## 3. AI Collaboration

**a. How you used AI**

I used AI to generate most code, tests, and the diagram. AI was good at getting ideas and learning about UML diagram. 

**b. Judgment and verification**

I did not accept the name of the file it set for pawpal_system.py. I thought
it would be simpler if I followed the naming standard of what we were provided in the project. 

---

## 4. Testing and Verification

**a. What you tested**

Tasks sort into chronological order via sort_by_time
Marking a daily or weekly task complete spawns a next occurrence with the correct shifted date
A one-off task (frequency=None) does not spawn anything
Two tasks at the same due_datetime — on the same pet and across different pets — produce a WARNING string
Tasks at different times produce no warnings
Completed tasks are excluded from conflict checks


**b. Confidence**

I am above average in confidence. I thought the AI sped up development greatly. 

Edge cases
Duration overlap — a 60-minute task at 9:00 and a task at 9:45 won't be flagged, because conflict detection only compares exact due_datetime equality
Recurrence across DST boundaries — adding timedelta(days=1) near a daylight-saving transition can produce the wrong wall-clock time


---

## 5. Reflection

**a. What went well**

Learning about UML diagrams and system design.

**b. What you would improve**

More UI components to make the website look cool would be fun. 

**c. Key takeaway**

Keeping data (Task, Pet, Owner) and logic (Scheduler) in separate classes made every feature addition straightforward — conflict detection, recurrence, and sorting all landed in one place without touching the data models. The takeaway: separating what a thing is from what you do with it keeps a system easy to extend.