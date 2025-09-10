# 7. Entity Linking Validation Protocol

### 1. The Critical Rule

When creating a new artifact (e.g., `REQ-*.md`) that references other artifacts (e.g., `[[STORY-*.md]]`), you **must** first use the available tools to verify that all referenced artifacts **physically exist** in the `pages/` directory.

**Creating a link to a non-existent document is a serious violation of this protocol.**

### 2. Verification Mechanism

Before creating a file that contains a link `[[DOCUMENT-NAME]]`, you must follow this procedure:

1.  **Formulate the filename:** Convert `[[DOCUMENT-NAME]]` into the expected filename (e.g., `pages/DOCUMENT-NAME.md`).
2.  **Perform the check:** Use the `<list_files path="pages/">` or `<read_file path="pages/DOCUMENT-NAME.md">` tool to verify the file's existence.
3.  **Make a decision:**
    * **If the file exists:** Proceed with creating your artifact and linking to it.
    * **If the file does NOT exist:** **Stop** the task. Inform the user about the attempt to create a "broken link" to a non-existent document and ask for further instructions.

### 3. Example Agent Workflow

**Incorrect:**
1.  Decide to create `REQ-PERF-39.md`.
2.  Inside the file, write a link to `[[STORY-PERF-77]]`.
3.  Save the file. *(Error! `STORY-PERF-77.md` does not exist)*

**Correct:**
1.  Decide to create `REQ-PERF-39.md`, which must link to `[[STORY-PERF-77]]`.
2.  **Verify:** Call `<list_files path="pages/">` and search for `STORY-PERF-77.md`.
3.  **Result:** The file is not found.
4.  **Action:** Abort the creation of `REQ-PERF-39.md`. Report to the user: "I cannot create `REQ-PERF-39` because it must link to the non-existent `STORY-PERF-77`. How should I proceed?"