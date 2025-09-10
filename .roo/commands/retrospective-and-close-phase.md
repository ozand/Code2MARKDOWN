---
description: "Автоматически собрать итоговый отчет по завершенной фазе, а затем запустить процесс извлечения уроков."
---
<task>
    <name>Retrospective, Phase Closure, and Lessons Learned</name>
    <objective>To automatically generate a summary report for a completed phase, and then initiate the process of extracting lessons for analyzing results and planning the next phase.</objective>
    <trigger>All User Stories related to a specific phase are marked with the status `[[DONE]]`.</trigger>
    <context>
        <knowledge_base>All `STORY-*.md` files with the property `phase:: [[Phase-X]]`.</knowledge_base>
        <standard>[[rules.04-filename-referencing-rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Data Collection and Analysis for Retrospective">
            <instruction>Delegate the task to the `Project Research` agent.</instruction>
            <sub_task_prompt>
"**Task:** Prepare a report on the completion of Phase [[Phase-X]].
1. Using a Datalog query, find all User Stories related to this phase.
2. Gather statistics: total number of tasks, distribution by category (API, UI, INFRA), and distribution by priority.
3. Create a new page `pages/reports.phase-[X]-summary.md` and populate it with the collected statistics and a list of all completed tasks."
            </sub_task_prompt>
            <on_failure>
                <instruction>Inform the user that the retrospective report could not be generated. Provide the error log from `Project Research`.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Informing About Report Readiness">
            <instruction>Inform the user that the retrospective report is ready and that the process of extracting lessons has begun.</instruction>
        </step>
        <step id="3" name="Initiate Lesson Extraction">
            <instruction>Initiate the execution of the `[[commands.extract-phase-learnings]]` command.</instruction>
            <on_failure>
                <instruction>Inform the user that the lesson extraction process could not be started.</instruction>
            </on_failure>
        </step>
    </workflow>
</task>