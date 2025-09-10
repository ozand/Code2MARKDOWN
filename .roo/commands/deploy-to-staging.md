---
description: "Развертывает текущую версию приложения на staging (preview) окружение в Vercel."
---
<task>
    <name>Deploy to Staging</name>
    <objective>To obtain a preview link for the deployed application for final approval before release.</objective>
    <trigger>Manual trigger after successful completion of QA tests.</trigger>
    <workflow>
        <step id="1" name="Deploy to Vercel Preview">
            <instruction>Delegate to the `Code` agent.</instruction>
            <sub_task_prompt>
"**Task:** Deploy the application to staging.
1. Execute the `vercel` command.
2. Extract the preview URL from the output and provide it to me."
            </sub_task_prompt>
            <human_approval_gate>true</human_approval_gate>
            <on_failure>
                <instruction>Inform the user that the deployment to staging failed. Provide logs.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Awaiting Approval">
            <instruction>Inform the user that the application has been deployed to staging and request confirmation to release to production.</instruction>
            <tool_to_use>ask_followup_question</tool_to_use>
        </step>
    </workflow>
</task>