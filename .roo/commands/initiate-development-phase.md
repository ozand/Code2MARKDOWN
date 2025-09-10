---
description: "Провести полный цикл декомпозиции плановых документов в атомарные, готовые к работе артефакты в графе знаний Logseq."
---
<task>
    <name>Initiate Development Phase</name>
    <objective>To conduct a full decomposition cycle of planning documents into atomic, ready-to-work artifacts in the Logseq knowledge graph.</objective>
    <trigger>Start of a new development phase, presence of `roadmap.md`, `backlog.md`, `requirements.md` files in `pages/`.</trigger>
    <context>
        <source_documents>[[roadmap]], [[backlog]], [[requirements]]</source_documents>
        <standard>[[rules.04-filename_referencing_rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Decomposition of Requirements and Tasks">
            <instruction>Delegate the task to the `User Story Creator` agent.</instruction>
            <sub_task_prompt>
"**Task:** Analyze [[backlog]] and [[requirements]]. For each User Story and each requirement specified in these documents, create a separate, atomic file in the `pages/` directory according to the standard. Fill in all mandatory properties and create the necessary links."
            </sub_task_prompt>
            <on_failure>
                <instruction>Inform the user about a failure during the decomposition stage. Provide the error log from `User Story Creator`.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Implementation Planning">
            <instruction>Delegate the task to the `Architect` agent.</instruction>
            <sub_task_prompt>
"**Task:** Based on the created User Stories and requirements, develop a detailed `implementation-plan` for this phase. Create a separate page for it at `pages/phase-[X]-implementation-plan.md`. The plan should include the task implementation sequence and technical specifications."
            </sub_task_prompt>
            <human_approval_gate>true</human_approval_gate>
            <on_failure>
                <instruction>Inform the user that the `Architect` could not create the implementation plan. Provide the error log.</instruction>
            </on_failure>
        </step>
        <step id="3" name="Final Validation">
            <instruction>Run the validation script to check the integrity of the created knowledge graph.</instruction>
            <command>uv run python scripts/development/validate_kb.py</command>
            <expected_result>No validation errors.</expected_result>
            <on_failure>
                <instruction>Inform the user that the knowledge base failed validation after decomposition. Provide the report from `validation_report.log` and stop the phase initiation process.</instruction>
            </on_failure>
        </step>
    </workflow>
</task>