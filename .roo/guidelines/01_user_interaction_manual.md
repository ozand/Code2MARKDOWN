# Guideline: Effective User Interaction with AI Agents

This document contains a set of rules and best practices for writing prompts and managing AI agents to significantly improve their reliability, predictability, and quality of work.

### Principle 1: Clarity and Atomicity of Tasks

AI agents work best with clearly defined, focused tasks.

- **Be specific.** Avoid general phrases. Instead of "fix the code," use "in file `'src/utils.js'` (see below for file content), in the function `calculateTotal`, fix the error that incorrectly handles negative numbers."
- **One task per message.** Do not combine multiple unrelated actions in one prompt. Break down complex goals into a sequence of simple steps.

### Principle 2: Provide Maximum Context via Tools

The agent does not see your screen. Provide all necessary information using built-in tools like `@mentions`.

- **Reference files:** Always specify the path to the file you are working with using `@`. Example: "analyze the file `'src/api/auth.js`."' (see below for file content)
- **Use `@problems` for errors:** To fix code errors, the command "fix all errors from `@problems`" is highly effective, as it provides the agent with a complete list of errors from the IDE's "Problems" panel.
- **Reference the terminal:** If a command in the terminal fails, use `@terminal` to provide the agent with its output for analysis.

### Principle 3: The Right Tool (Mode) for the Right Job

Use specialized modes to increase efficiency and safety.

- **`🏛️ Architect`:** For high-level planning and design. **Will not and should not write code** (except for `.md` documentation files).
- **`💻 Code`:** The primary mode for writing and editing code.
- **`❓ Ask`:** **The safest mode.** It cannot modify files or execute commands. Ideal for exploring the codebase and getting answers without risk.
- **`🪲 Debug`:** Use this mode when you encounter an error.
- **`🪃 Orchestrator`:** For very complex, multi-step tasks.

### Principle 4: Verify, Don't Trust (The Action-Verification Cycle)

You are the manager; the agent is the performer. Control every step.

- **Verify results:** After an agent performs an action (`execute_command`, `write_to_file`), ask it to verify the outcome.
  - *"Show the list of files in directory X"* to confirm a file was created.
  - *"Read the contents of file Y"* to ensure the content was written correctly.
- **Approve actions carefully:** Review the agent's proposed action before clicking "Approve." This is your main point of control.

### Principle 5: Handling Context Poisoning

If an agent begins to behave erratically (forgetting instructions, looping), it may be due to "Context Poisoning."

- **Don't try to "cure" it:** Do not waste time with prompts like "remember everything." This is ineffective.
- **The best solution is a "Reboot":** The most reliable way to fix the situation is to **start a new session (task)**. This completely clears the poisoned context and restores the agent to its initial, working state.