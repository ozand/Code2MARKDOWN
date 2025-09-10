---
description: "Последовательно реализовать все User Stories, определенные в плане реализации для текущей фазы проекта."
---
<task>
    <name>Start Development Cycle According to Plan</name>
    <objective>To sequentially implement all User Stories defined in the implementation plan for the current project phase.</objective>
    <trigger>Successful completion of the "Initiate Development Phase" task and the presence of an approved `implementation-plan`.</trigger>
    <context>
        <implementation_plan>[[pages/phase-[X]-implementation-plan]]</implementation_plan>
        <standard>[[rules.04-filename_referencing_rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Define the Task List">
            <instruction>Analyze the `<implementation_plan>` document and extract a complete, ordered list of User Stories (`[[STORY-ID]]`) to be implemented in this phase.</instruction>
            <tool_to_use>read</tool_to_use>
            <on_failure>
                <instruction>Inform the user that the implementation plan could not be read or the task list could not be extracted from it.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Sequential Implementation">
            <instruction>For each User Story from the obtained list, in strict order, delegate the implementation task to the `Code` agent.</instruction>
            <sub_task_prompt_template>
"**Task:** Implement User Story `[[STORY-ID]]`.
**Context:**
- A detailed description and acceptance criteria are in the `[[STORY-ID]]` file.
- Technical specifications and dependencies are described in the `[[implementation_plan]]`.
- Always follow the coding standards from `[[rules.01-quality_guideline]]`.
**Protocol:**
1. Before starting work, change the `status` property in the `[[STORY-ID]]` file to `[[DOING]]`.
2. After completing the implementation and passing tests, change the `status` property to `[[DONE]]`.
3. Create links to all modified or created code files in the `[[STORY-ID]]` document."
            </sub_task_prompt_template>
            <on_failure>
                <instruction>Inform the user of a failure during the implementation of `[[STORY-ID]]`. Provide the log from the `Code` agent and pause the development cycle until the issue is resolved.</instruction>
            </on_failure>
        </step>
        <step id="3" name="Phase Completion">
            <instruction>After all User Stories from the list have been completed (status changed to `[[DONE]]`), initiate the "Retrospective and Phase Closure" task.</instruction>
        </step>
    </workflow>
</task>