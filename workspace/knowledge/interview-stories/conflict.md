# Interview Story: Conflict Resolution

## Situation
While designing the dashboard UI elements at Nestbotics, a colleague wanted to build and ship the layout features as fast as possible by copy-pasting styling definitions and component structures. I argued that we should spend time extracting these into a shared library. This led to a conflict, as my colleague felt my approach would slow down our delivery targets.

## Task
To find a compromise that would resolve their concerns about delivery speed while preventing technical debt and layout inconsistency in our codebase.

## Action
1.  **Listen & Quantify:** Scheduled a quick 1-on-1 to listen to their timeline pressures. I then demonstrated that copy-pasting code might save an hour today, but debugging styling mismatches or fixing visual bugs on 10 different dashboards later would cost days of rework.
2.  **Proposed a Hybrid Strategy:** Suggested we divide the work. They could build the raw layout shells using basic placeholder styling while I focused on extracting the core components (cards, filters) in parallel.
3.  **Execute & Support:** I provided pre-configured code structures that they could drop in with single-line imports.

## Result
*   We resolved the conflict constructively, maintaining a good working relationship.
*   We delivered the dashboards on schedule.
*   My colleague realized the benefits when we needed to change a table styling color globally; we changed it in *one* file in the shared library, and it instantly updated all 10+ dashboards, saving hours of work.
*   The shared library reduced feature delivery times by **40%** moving forward.
