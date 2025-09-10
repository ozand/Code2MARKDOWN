---
description: "Создать черновик плана реализации для следующей фазы, учитывая бэклог, дорожную карту и уроки предыдущей фазы."
---
<task>
    <name>Plan Next Development Phase</name>
    <objective>To create a draft implementation plan for the next phase, considering the backlog, roadmap, and lessons from the previous phase.</objective>
    <trigger>Manual trigger by the user after analyzing `LEARNING-*.md` artifacts.</trigger>
    <context>
        <source_documents>[[roadmap]], [[backlog]]</source_documents>
        <learnings>All `LEARNING-*.md` from the previous phase.</learnings>
        <standard>[[rules.04-filename-referencing-rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Develop Draft Plan Incorporating Lessons">
            <instruction>Delegate the task to the `Architect` agent.</instruction>
            <sub_task_prompt>
"**Task:** Develop a draft of `[[phase-[X+1]-implementation-plan]]`.
**Mandatory sources for analysis:**
1. `[[roadmap]]` and `[[backlog]]` to determine WHAT to do.
2. All `[[LEARNING-*.md]]` artifacts from the previous phase to determine HOW to do it better.
**Plan Requirements:**
- The plan must contain the implementation sequence of User Stories.
- **Critically important:** The plan must include explicit references to the 'lessons'. You must show exactly how you have incorporated previous experience.
- **Example:** *'Additional time is allocated for testing the API module (tasks [[STORY-API-15]], [[STORY-API-16]]), as a problem with insufficient test coverage was identified in the last phase (see [[LEARNING-1]]).'*
"
            </sub_task_prompt>
            <human_approval_gate>true</human_approval_gate>
            <on_failure>
                <instruction>Inform the user that the `Architect` could not create the plan. Provide the error log and recommend checking the clarity of the backlog and the 'lessons'.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Informing of Readiness">
            <instruction>After the user approves the plan, inform them that the phase is ready for initiation.</instruction>
            <sub_task_prompt>
"**Task:** The plan is approved. Inform the user that the `[[commands.initiate-development-phase]]` command can now be run to start the new phase."
            </sub_task_prompt>
        </step>
    </workflow>
</task>