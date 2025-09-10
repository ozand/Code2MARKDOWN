---
description: "Выявить и устранить расхождения между фактическим состоянием реализации в Git и документированным состоянием в базе знаний Logseq."
---
<task>
    <name>Knowledge Base Audit and Synchronization</name>
    <objective>Identify and resolve discrepancies between the actual implementation state in Git and the documented state in the Logseq knowledge base.</objective>
    <trigger>Scheduled (weekly) or manually triggered.</trigger>
    <context>
        <knowledge_base>All `STORY-*.md` files in the `pages/` directory.</knowledge_base>
        <source_of_truth_code>Git commit logs in the current branch.</source_of_truth_code>
        <standard>[[rules.04-filename_referencing_rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Analyze Discrepancies">
            <instruction>Delegate the task to the `Project Research` agent.</instruction>
            <sub_task_prompt>
"**Task:** Conduct an audit.
1. Find all User Stories with the status `[[DONE]]` that do not have a corresponding Git commit (with the story ID in the message).
2. Find all User Stories with the status `[[TODO]]` or `[[DOING]]` for which a closing commit already exists.
3. Generate a report of all found discrepancies in my journal for today."
            </sub_task_prompt>
            <on_failure>
                <instruction>Inform the user that the `Project Research` agent failed to conduct the audit and provide the error log.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Request for Correction">
            <instruction>Based on the report from `Project Research`, request user confirmation to correct the statuses in the `STORY-*.md` files.</instruction>
            <tool_to_use>ask_followup_question</tool_to_use>
            <human_approval_gate>true</human_approval_gate>
        </step>
        <step id="3" name="Correction">
            <instruction>After receiving confirmation, delegate the task of correcting the statuses to the `Code` agent.</instruction>
            <sub_task_prompt>
"**Task:** Correct the `status` property in the following User Story files according to the audit report: [list of files]."
            </sub_task_prompt>
            <on_failure>
                <instruction>Inform the user that the `Code` agent failed to correct the statuses and provide the error log. Recommend checking file write permissions.</instruction>
            </on_failure>
        </step>
    </workflow>
</task>
