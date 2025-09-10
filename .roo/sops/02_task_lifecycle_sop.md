# SOP: Task Lifecycle

This SOP outlines the required algorithm for AI agents when working on new development tasks, from analysis to completion.

### Phase 1: Analysis and Decomposition

1.  **Input:** Receive a link to a high-level document with tasks (e.g., `[[phase5-implementation-plan]]`).
2.  **Action:** Analyze the document. For **each** individual feature or improvement, follow this protocol:
    * Create a new file `pages/STORY-[CATEGORY]-[ID].md`.
    * Fill out the file according to the User Story template, adding the **mandatory properties** from the metadata reference.
    * Inside the file, describe the User Story and Acceptance Criteria in detail.
3.  **Output:** A set of new, atomic User Story pages in the `pages/` folder.

### Phase 2: Implementation

1.  **Input:** Pick up one User Story with the status `[[TODO]]`.
2.  **Action:**
    * **Immediately** update the status in the `STORY-*.md` file to `status:: [[DOING]]`.
    * Proceed with implementing the code and tests.
    * Git commits **must** include the story ID (e.g., `feat: Implement search filters (STORY-API-1)`).
3.  **Output:** Completed code that corresponds to the User Story.

### Phase 3: Completion

1.  **Input:** A completed and tested implementation.
2.  **Action:**
    * **Immediately** update the status in the `STORY-*.md` file to `status:: [[DONE]]`.
    * Check if the implementation requires updating other documentation and make the necessary changes.
    * **Create a journal entry** for the current day according to the journaling protocol.
3.  **Output:** An updated knowledge base and a new entry in the daily journal.