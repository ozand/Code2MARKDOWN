---
description: "Запускает статический анализ кода для поиска проблемных мест, 'кодовых запахов' и оценки сложности."
---
<task>
    <name>Code Quality Analysis</name>
    <objective>To generate a report on the current state of code quality with recommendations for refactoring.</objective>
    <trigger>Manual trigger or scheduled.</trigger>
    <context>
        <tool_to_use>ruff, SonarQube, etc.</tool_to_use>
        <standard>[[rules.01-quality_guideline]]</standard>
    </context>
    <workflow>
        <step id="1" name="Run Analyzers">
            <instruction>Delegate to the `Architect` agent.</instruction>
            <sub_task_prompt>
"**Task:** Conduct a code quality analysis.
1. Execute `ruff check . --statistics`.
2. Analyze the output for critical issues.
3. Create a page `pages/reports.code-quality-[YYYY-MM-DD].md` and document the key metrics and problem areas there."
            </sub_task_prompt>
            <on_failure>
                <instruction>Inform the user that the code analysis could not be performed.</instruction>
            </on_failure>
        </step>
    </workflow>
</task>