---
description: "Корректно задокументировать и интегрировать в текущий план новую задачу (баг, доработка), которая не была предусмотрена изначально."
---
<task>
    <name>Handling an Unplanned Task</name>
    <objective>To correctly document and integrate a new task (bug, enhancement) that was not originally planned into the current plan.</objective>
    <trigger>Receiving a bug report or a new feature request from the user.</trigger>
    <context>
        <user_input>[Insert bug report text or new feature description here]</user_input>
        <standard>[[rules.04-filename_referencing_rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Creation and Documentation">
            <instruction>Delegate the task to the `User Story Creator` agent.</instruction>
            <sub_task_prompt>
"**Task:** Based on the provided data, create a new file `pages/STORY-[DEFECT/FEATURE]-[ID].md`. Describe the User Story, Acceptance Criteria, and fill in all mandatory properties (`type`, `status`, `priority`)."
            </sub_task_prompt>
            <on_failure>
                <instruction>Inform the user that the User Story could not be created. Provide the error log from `User Story Creator`.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Integration into the Plan">
            <instruction>Delegate the task to the `Architect` agent.</instruction>
            <sub_task_prompt>
"**Task:** Analyze the new User Story `[[NEW_TASK_ID]]`. Find the most suitable epic (`[[EPIC-...]]`) and requirement (`[[REQ-...]]`) and link them to the new task via properties. If no suitable ones exist, create a report for the Product Owner. Assess the impact of the new task on the current `sprint-plan`."
            </sub_task_prompt>
            <on_failure>
                <instruction>Inform the user that the new task could not be integrated into the plan. Provide the error log from `Architect`.</instruction>
            </on_failure>
        </step>
    </workflow>
</task>