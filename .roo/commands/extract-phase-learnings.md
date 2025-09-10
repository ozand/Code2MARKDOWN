---
description: "Проанализировать результаты завершенной фазы и задокументировать ключевые уроки для улучшения будущих процессов."
---
<task>
    <name>Extracting Lessons from a Completed Phase</name>
    <objective>To analyze the results of a completed phase and document key lessons to improve future processes.</objective>
    <trigger>Successful completion of the "Retrospective and Phase Closure" command.</trigger>
    <context>
        <knowledge_base>All `STORY-*.md` and `REQ-*.md` files related to the completed phase.</knowledge_base>
        <standard>[[rules.04-filename_referencing-rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Analyze Phase Artifacts and Find Patterns">
            <instruction>Delegate the task to the `Project Research` agent.</instruction>
            <sub_task_prompt>
"**Task:** Analyze all artifacts (mainly `STORY-*.md`) from phase [[Phase-X]]. Your goal is to find insights for improvement.
**Look for patterns:**
- **Technical:** Which technical solutions were particularly successful or problematic? Where were the most bugs?
- **Process:** Which tasks took an unexpectedly long or short time? Were there issues with dependencies between tasks?
- **Requirement Quality:** Were there User Stories that were frequently reworked due to unclear acceptance criteria?
**Result:** Prepare a structured report with these insights in my journal for today."
            </sub_task_prompt>
            <on_failure>
                <instruction>Inform the user that the phase results could not be analyzed. Provide the error log from `Project Research`.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Formalize Lessons">
            <instruction>Based on the report from `Project Research`, delegate the task to the `User Story Creator` agent.</instruction>
            <sub_task_prompt>
"**Task:** For each insight from the `Project Research` report, create a separate, atomic file `pages/LEARNING-[ID].md`.
**Protocol:**
1. Carefully study the insight.
2. Determine its `impact` (positive/negative) and `category` (technical, process, communication).
3. Create the `LEARNING-*.md` file and fill in all properties according to the [[rules.04-filename_referencing-rules]] standard.
4. In the body of the file, describe the essence of the lesson in detail and provide a specific recommendation for the future."
            </sub_task_prompt>
            <on_failure>
                <instruction>Inform the user that the lessons could not be documented. Provide the error log from `User Story Creator`.</instruction>
            </on_failure>
        </step>
         <step id="3" name="Final Report">
             <instruction>Inform the user about the completion of the analysis and the number of "lessons" created.</instruction>
             <sub_task_prompt>
"**Task:** Prepare a brief report on the completion of the lesson extraction. State how many `LEARNING-*.md` files were created and provide links to them. Recommend that the user review them before running the command to plan the next phase."
             </sub_task_prompt>
        </step>
    </workflow>
</task>