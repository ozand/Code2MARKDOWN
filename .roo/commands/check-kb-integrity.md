---
description: "Выполняет синхронизацию статусов User Stories в базе знаний с их реальным состоянием в Git, используя автоматизированные скрипты для анализа."
---

<task>
    <name>Audit and Synchronize Knowledge Base with Git</name>
    <objective>Automatically identify and resolve discrepancies between User Story statuses in Logseq and the presence of closing commits in Git.</objective>
    <trigger>Manual trigger before closing a phase or weekly.</trigger>
    <context>
        <tool_to_use>scripts/development/validate_kb.py</tool_to_use>
        <tool_to_use>scripts/development/sync_git_kb.py</tool_to_use>
        <source_of_truth>Git commit logs and `STORY-*.md` files in `pages/`.</source_of_truth>
        <standard>[[04-filename-referencing-rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Preliminary Integrity Check">
            <instruction>Delegate to the `Code` agent.</instruction>
            <sub_task_prompt>
"**Task:** Before starting synchronization, ensure the knowledge base does not contain basic errors.
1.  Execute the command: `python scripts/development/validate_kb.py`.
2.  If the script finds errors, stop execution and report them to me. Otherwise, proceed to the next step."
            </sub_task_prompt>
        </step>

        <step id="2" name="Analyze Report and Determine Next Steps">
            <instruction>Analyze the validation report and determine the next actions.</instruction>
            <sub_task_prompt>
"**Task:** Analyze `validation_report.log` and determine a plan.
1.  Read the `validation_report.log` file.
2.  **If the report contains 'Misplaced file' errors**:
    -   Inform me about it.
    -   Recommend running the `Integrate Stray Files` command to fix them.
    -   **Do not continue** with the current task, as the file locations need to be corrected first.
3.  **If there are other errors (e.g., 'Broken link')**:
    -   Create a JSON plan to fix them and request my confirmation, as before.
4.  **If there are no errors**:
    -   Report that the check was successful and complete the task."
            </sub_task_prompt>
        </step>

        <step id="3" name="Automatic Status Correction">
            <instruction>Based on the `sync_report.json` report, delegate the task of correcting statuses to the `Code` agent.</instruction>
            <sub_task_prompt>
"**Task:** Correct the statuses in the User Story files according to the report.
1.  Read the `sync_report.json` file.
2.  For **each** entry in the report, open the specified `STORY-*.md` file and set the correct status (`status:: [[DONE]]` or `status:: [[TODO]]`) according to the recommendation in the report.
3.  After making all corrections, delete the `sync_report.json` file."
            </sub_task_prompt>
        </step>

        <step id="4" name="Final Report">
             <instruction>Report completion and make a journal entry.</instruction>
             <sub_task_prompt>
"**Task:** Complete the task and document the result.
1.  Create a brief report on how many User Stories were corrected.
2.  Create a journal entry for today according to the `7.5. Journaling on Task Completion` standard."
             </sub_task_prompt>
        </step>
    </workflow>
</task>