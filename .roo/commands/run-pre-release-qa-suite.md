---
description: "Запускает полный набор тестов (unit, integration, e2e) для проверки качества перед релизом."
---
<task>
    <name>Run Pre-Release QA Tests</name>
    <objective>To ensure that all tests pass successfully before creating a release tag and description.</objective>
    <trigger>Manual trigger after the completion of the development phase.</trigger>
    <context>
        <tool_to_use>scripts/run_all_tests.sh</tool_to_use>
        <standard>[[rules.03-e2e_tests_guidline]]</standard>
    </context>
    <workflow>
        <step id="1" name="Run All Tests">
            <instruction>Delegate to the `Code` agent.</instruction>
            <sub_task_prompt>
"**Task:** Run the full suite of QA tests.
1. Execute the command `uv run pytest`.
2. Analyze the output. If there are any failed tests, stop execution, create an error report in my journal, and attach the logs."
            </sub_task_prompt>
            <on_failure>
                <instruction>Inform the user that the QA tests have failed. Provide the report and logs. The release is blocked.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Report Success">
            <instruction>Inform the user that all tests have passed and the release process can begin.</instruction>
        </step>
    </workflow>
</task>