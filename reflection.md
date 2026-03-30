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
I ask AI for suggestions that I am not sure how to solve or which choice is better when design. I asked AI to debug itself first, then I will go over the code/output to see if there is anything needed to be changed. I will give AI some suggestions and examples to fix this bug. For refactoring part, I will ask for suggestions and optimize the suggestion and ask AI to implement it.

- What kinds of prompts or questions were most helpful?
Give detailed examples and pointed out the issue to ask AI to do/fix is the most effected prompt. Also, ask suggestions first and choose which option to implement is also helpful. Choose an option and tell AI some personal idea is a great way of prompting.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
The AI tried to add the checkbox of complement in add ask UI. I think it would be better if the checkbox is in the task items under the schedule. If the checkbox in add tasks, it would be hard to track daily and weekly tasks. 
- How did you evaluate or verify what the AI suggested?
I will review AI's explanation and my experience to see if the suggestion works. Also, I will check the output(tests/real APP/main output) to see if it meets what I want. If it is what I want, I will give prompt to clarify my requirement.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested core user flows in the app, such as adding owners, pets, and tasks, generating schedules, modifying or deleting tasks, and managing available time slots.
- Why were these tests important?
These tests were important because they represent the main actions a user would take when using the app. I could endure the system works well and aligns the requirement through test them. They also help me to catch logic bugs and design issues to make sure that I am in the right track.

**b. Confidence**

- How confident are you that your scheduler works correctly?
5
- What edge cases would you test next if you had more time?
I want to test what will happen if the one time task and weekly task with the same priority have time conflict. I have a potential rule: FIFO(that is, first added task will be chosen if they have the same priority). However, as the weekly task will be updated, I am not sure which one would be chosen. 

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I implemented all the requiremented features, and I even changed the structure to meet those requirements. I think I also guided the AI to build this APP well. I am proud of my work.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I have rejected attributes/features that AI suggested but later I added them back. I think next time I need to ask AI for more specific details about what I want to delete. Also I have a big change, that is I changed Task class from owed by Schedule to Pet. This happened when I almost finished all the basic classes, and I costed a lot of time to make this change and fix related bugs. Next time I need to ask AI more about the structure details to find the issue eariler.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
Clarify the pain point and give examples are very important to work with AI, they cannot understand what I want. Also, asking suggestions and be sure this word is in the prompt, I have some time that forget add this word and the AI just modified my code file before I check what AI want to do.