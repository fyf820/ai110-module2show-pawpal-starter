# PawPal+ Project Reflection

## 1. System Design

Core actions:

* Add a pet
* Add a task(walk, feed...) 
* Track today's schedule

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
Here is the Mermaid code for my UML design:

```
classDiagram
    class Owner {
        +id : String
        +name : String
        +available_hours : List
        +preferences : Dict
        +add_pet(pet : Pet)
        +remove_pet(pet_id : String)
        +add_schedule(schedule : Schedule)
        +remove_schedule(schedule_id: String)
        +get_pets() : List[String]
        +get_schedules() : List[String]
        +__str__() : String
    }

    class Pet {
        +id : String
        +name : String
        +species : String
        +age : int
        +special_needs : List
        +update_name(new_name : String)
        +update_species(new_species : String)
        +update_age(new_age : int)
        +add_special_need(need : String)
        +remove_special_need(need : String)
        +__str__() : String
    }

    class Task {
        +id : String
        +title : String
        +duration_minutes : int
        +priority : String
        +frequency : String
        +update_title(new_title : String)
        +update_duration(new_duration : int)
        +update_priority(new_priority : String)
        +update_frequency(new_frequency : String)
        +__str__() : String
    }

    class Schedule {
        +id : String
        +date : String
        +tasks : List
        +total_time : int
        +explanation : String
        +add_task(task : Task)
        +remove_task(task_id : String)
        +update_date(new_date : String)
        +update_explanation(new_explanation : String)
        +calculate_total_time() : int
        +__str__() : String
    }

    Owner "1" --> "0..*" Pet : owns
    Owner "1" --> "0..*" Schedule : creates
    Schedule "1" --> "0..*" Task : contains
    Schedule --> Pet : plans for
```
I have 4 different classes: Owner, Pet, Task, and Schedule. The Owner is pet owner, it can have multiple pets and schedule the tasks. Pet belongs to the only one owner and may have different attributes. Schedule belongs to one owner and contains different tasks. Task is similar to pet, it belongs to one schedule and have some attributes.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes,I removed age and special needs from pet, frequences from owner. And I also removed related methods. These are redundant. I also let the preference list contains preferred_tasks and preferred_pets keys, in case the users input invalid stuff. I add a generator in Schedule to generate the schedule. The biggest and most important change is that I moved the the tasks from under schedule to pet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
My scheduler has owner available time, task priority, and owner preferences. Logically, the available time will over other constraints. That is, if the task time does not meet the owner's time availability, the task will be rejected before check other constraints. And the task priority is over preferences,  it only checks the preferences when the priority is the same. The preferences contains preffered tasks and pets,  the tasks are over pets.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
The biggest tradeoff of the scheduler, even this project is that I moved the Task class from under Schedule class to Pet class. This change is because I realized that the tasks is related to a target pet rather than a broad concept. That is, I put the task under the Schedule because I think feed is like the owner will feed all pets together, but it might be not. Also for some specific tasks like walking a dog will make sense, but it is not likely to walk a cat or even a turtle.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
