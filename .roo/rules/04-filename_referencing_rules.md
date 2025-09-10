# 4. Project Knowledge Base Management Standard

### 1. Philosophy and Goals

This document is the **single and exhaustive source of truth** for organizing and maintaining the project's knowledge base. Its purpose is to ensure a strict, machine-readable, and consistent structure that solves two problems:

1.  **For Logseq:** To create a cohesive, easily navigable, and queryable knowledge graph built from the `pages/` directory.
2.  **For AI agents:** To provide an unambiguous, algorithmic set of rules for creating, updating, and validating all project artifacts.

Deviation from these rules is not permitted.

-----

### 2. Knowledge Repository Structure

#### 2.1. Graph Root

The root directory of the entire project is the root of the Logseq graph. The knowledge base itself resides exclusively within the `pages/` and `journals/` directories.

#### 2.2. Mandatory Structure and Purpose of Folders

AI agents are required to create new files only in the locations specified below.

  * `pages/`: **The central repository for accessing knowledge in Logseq.** Contains all main documents: User Stories, requirements, as well as **symbolic links** to rules and commands.
  * `journals/`: **A chronological work log.** Used for daily notes and logging task completion.
  * `.roo/`: **The source of truth for operational files.** Contains the source files for rules (`.roo/rules/`) and commands (`.roo/commands/`). **This directory is not scanned by Logseq directly.**
  * `assets/`: For storing images and other media files embedded in documents.
  * `logseq/`: A folder automatically managed by Logseq. AI agents are forbidden from modifying this folder directly.

-----

### 3. Protocol for Creating and Naming Files in `pages/`

To logically group documents, a **namespace** mechanism is used, implemented via a `.` in the filename. All primary artifacts **must be** created in `pages/`.

  * **User Stories:**

      * **Location:** `pages/`
      * **Filename Format:** `STORY-[CATEGORY]-[ID].md` (e.g., `STORY-API-1.md`)
      * **Logseq Page Name:** `[[STORY-API-1]]`

  * **Requirements:**

      * **Location:** `pages/`
      * **Filename Format:** `REQ-[CATEGORY]-[ID].md` (e.g., `REQ-UI-3.md`)
      * **Logseq Page Name:** `[[REQ-UI-3]]`

  * **Rules and Commands:**

      * **Source of Truth Location:** Files **must** physically reside in `.roo/rules/` and `.roo/commands/`.
      * **Virtual Location in Logseq:** The `bootstrap.py` script automatically creates symbolic links from these files into the `pages/` directory, using the `rules.*` and `commands.*` namespaces to make them visible in the knowledge graph.
      * **Filename Format:**
          * Rules: `rules.[rule-name].md` (e.g., `pages/rules.quality-guideline.md`)
          * Commands: `commands.[command-name].md` (e.g., `pages/commands.audit-and-sync-kb.md`)
      * **Operational Location:** The `bootstrap.py` script automatically creates symbolic links from these files into the appropriate `.roo/` subdirectories (e.g., from `pages/rules.quality-guideline.md` to `.roo/rules/quality-guideline.md`).

-----

### 4. Linking Rules

#### 4.1. Links to Documents in the Knowledge Base

  * **Format:** `[[page_name]]`
  * **Example:** `This task implements the requirement [[REQ-UI-5]].`

#### 4.2. Links to Code Files, Tests, and Other External Files

  * **Principle:** The **Logseq alias** mechanism is used.
  * **Format:** `[[relative/path/to/file.py|`file.py`]]`
  * **Example:** `The main logic is located in [[b2bfinder/services/search.py|`search.py`]].`

-----

### 5. Protocol for Structuring Documents and Metadata

Every artifact in the `pages/` directory **must** contain a properties block at the beginning of the file. These properties classify the document and make it machine-readable for queries and automation.

#### 5.1. Properties Schema for a User Story

`STORY-*.md` files must contain the following properties. Using plain text instead of links for `status`, `priority`, and `assignee` is **forbidden**.

```markdown
type:: [[story]]
status:: One of the following values: `[[TODO]]`, `[[DOING]]`, `[[DONE]]`
priority:: One of the following values: `[[high]]`, `[[medium]]`, `[[low]]`
assignee:: Link to the assignee: `[[@username]]`
epic:: Link to the epic: `[[EPIC-NAME]]`
related-reqs:: A comma-separated list of links to requirements: `[[REQ-ID-1]], [[REQ-ID-2]]`
```

#### 5.2. Properties Schema for a Requirement

`REQ-*.md` files must contain the following properties:

```markdown
type:: [[requirement]]
status:: One of the following values: `[[PLANNED]]`, `[[IMPLEMENTED]]`, `[[PARTIAL]]`
```

#### 5.3. Properties Schema for an Implementation Plan

This type of document is created by the `Architect` agent for planning work on an epic or phase.

```markdown
type:: [[implementation-plan]]
phase:: Link to the phase: `[[Phase-5]]`
related-epics:: A comma-separated list of links to epics: `[[EPIC-UI]], [[EPIC-INFRA]]`
status:: One of the following values: `[[DRAFT]]`, `[[APPROVED]]`, `[[COMPLETED]]`
```

#### 5.4. Properties Schema for a Learning

This artifact is created at the end of a phase to document key lessons learned. It serves as input for planning future phases.

  * **Location:** `pages/`
  * **Filename Format:** `LEARNING-[ID].md`
  * **Logseq Page Name:** `[[LEARNING-ID]]`
  * **Properties Schema:**
    ```markdown
    type:: [[learning]]
    phase:: [[Phase-X]] 
    impact:: [[positive]] or [[negative]]
    related-stories:: [[STORY-API-5]], [[STORY-UI-12]]
    category:: [[technical]], [[process]], or [[communication]]
    ```

-----

### 6. Project Management and Visualization

#### 6.1. Rule: Mandatory Creation of a Project Hub

A file named `Project Hub.md` **must be** created in the root of the `pages/` directory. It serves as the main entry point for navigating the knowledge base. AI agents must keep it up to date.

**Structure of the `pages/Project Hub.md` file:**

```markdown
title:: Project b2bfinder Hub
---
## 🧭 Navigation
- **Rules and Guidelines:** [[rules.quality-guideline]], [[rules.scripts-structure]], [[rules.e2e-tests-guideline]], [[rules.filename-referencing-rules]]
- **Product:** [[product.vision]], [[requirements]], [[backlog]], [[roadmap]]
- **Technical Documentation:** [[api]], [[caching-strategy]], [[DEPLOYMENT_PLAN]]

---
## 🚀 Development Dashboard
### 👨‍💻 Tasks in Progress (DOING)
{{query (and (property type story) (page-ref "DOING"))}}

### 🔥 Critical Tasks to Do (TODO High Prio)
{{query (and (and (property type story) (page-ref "TODO")) (property priority high))}}
```

#### 6.2. Protocol for Kanban Visualization

For automatic visualization of tasks on a Kanban board (using the Kanban plugin), AI agents must strictly follow these rules.

  * **Data Source for Columns:** The `status` property in a User Story is the single source of truth for determining which column of the Kanban board a task is in.
  * **Mapping Statuses to Columns:**
      * `status:: [[TODO]]` ➔ **"To Do"** column
      * `status:: [[DOING]]` ➔ **"In Progress"** column
      * `status:: [[DONE]]` ➔ **"Done"** column
  * **Data on Cards:** The Kanban plugin should be configured to display the values of the `priority` and `assignee` properties on the cards for quick assessment of the task.
  * **Updating:** An AI agent, upon completing a task or starting to work on it, **must** update the `status` property in the corresponding `STORY-*.md` file. The Kanban board on the `[[Project Hub.md]]` page will update automatically.

-----

### 7. AI Agent Work Protocols

**Critical Rule:** Before executing any task, you are **obligated** to review and strictly follow the document **[[rules.06-tool-usage-protocol]]**. Violation of this protocol, especially the improper use of `execute_command`, is considered a serious error.

#### 7.1. Work Algorithm (Task Lifecycle)

AI agents are required to follow this algorithm when working on new phases or tasks.

**Phase 1: Analysis and Decomposition**

1.  **Input:** Receive a link to a high-level document with tasks (e.g., `[[phase5-implementation-plan]]`).
2.  **Action:** Analyze the document. For **each** individual feature or improvement, follow this protocol:
      * Create a new file `pages/STORY-[CATEGORY]-[ID].md`.
      * Fill out the file according to the User Story template, adding the **mandatory properties** from section 5.1.
      * Inside the file, describe the User Story and Acceptance Criteria in detail.
3.  **Output:** A set of new, atomic User Story pages in the `pages/` folder.

**Phase 2: Implementation**

1.  **Input:** Pick up one User Story with the status `[[TODO]]`.
2.  **Action:**
      * **Immediately** update the status in the `STORY-*.md` file to `status:: [[DOING]]`.
      * Proceed with implementing the code and tests.
      * Git commits **must** include the story ID (e.g., `feat: Implement search filters (STORY-API-1)`).
3.  **Output:** Completed code that corresponds to the User Story.

**Phase 3: Completion**

1.  **Input:** A completed and tested implementation.
2.  **Action:**
      * **Immediately** update the status in the `STORY-*.md` file to `status:: [[DONE]]`.
      * Check if the implementation requires updating other documentation and make the necessary changes.
      * **Create a journal entry** for the current day according to the format specified in rule `7.5. Journaling on Task Completion`.
3.  **Output:** An updated knowledge base and a new entry in the daily journal. The dashboards on `[[Project Hub.md]]` will update automatically.

#### 7.2. Protocol for Using Datalog Queries

To obtain global context and analyze relationships, AI agents are **permitted and instructed** to use Datalog queries.

  * **Purpose:** Queries are used to retrieve information that is not contained in a single file.
  * **Example Scenario:** Before starting work on `[[STORY-API-3]]`, the agent must check the status of the dependent task `[[STORY-INFRA-1]]` by executing the query `{{query (and (page-ref "STORY-INFRA-1") (property type story))}}` and analyzing the `status` property.

#### 7.3. Rule: Contextual Linking

When working on any artifact, the AI agent **must** add links to all related entities: requirements, other tasks, code files, test results.

#### 7.4. Rule: Descriptive Page Names

Page names should be full and descriptive (e.g., `[[Redis Caching Strategy]]` instead of `[[cache]]`).

#### 7.5. Rule: Journaling on Task Completion

To provide a clear chronological log for the Observer, every AI agent **must** create an entry in the daily journal upon successfully completing a task.

  * **Trigger:** Successful completion of a delegated task.
  * **Action:** Append a new block to the journal file for the current date (e.g., `journals/YYYY_MM_DD.md`).
  * **Format:** The journal entry **must** follow this template:
    ```markdown
    - Task Completed: `[[Name of the completed task or Story]]`
      - **Status:** `SUCCESS`
      - **Agent:** `[[Agent Name]]`
      - **Summary:** A brief, one-sentence summary of the outcome.
      - **Link to Artifacts:** Links to any primary pages that were created or modified, e.g., `[[STORY-API-5]]`.
    ```

-----

### 8. Automation and Validation

#### 8.1. Knowledge Base Linter Script

To maintain the integrity of the knowledge base, the script `scripts/development/validate_kb.py` is used. Its primary function is to scan the `pages/` and `journals/` directories to ensure compliance with all standards.

#### 8.2. Validation Checklist (for `validate_kb.py`)

The script **must** perform the following checks. This checklist serves as a backlog for enhancing the validation script.

  * [x] **Link Integrity:** All links `[[filename]]` resolve to existing files. *(Implemented)*
  * [x] **Correct Link Formatting:** All links to external files (code, tests) follow the alias format `[[path/to/code.py|...]]`.
  * [x] **File Structure:** All documents are created in the correct directories (`pages/`, `journals/`) and follow the naming conventions (`STORY-*.md`, `REQ-*.md`, etc.).
  * [x] **Properties Schema:** All User Stories and Requirements have the mandatory properties (`type::`, `status::`, etc.).
  * [x] **Status Correctness:** The values of the `status` property correspond to the allowed list (`[[TODO]]`, `[[DONE]]`, etc.).
  * [x] **`title` Integrity in READMEs:** All `README.md` files have a `title::` property.
  * [x] **Handling Temporary Artifacts:** Files that are "raw" command outputs (e.g., `raw.md`, `error.errors`) must not be saved in `pages/`.

-----

### 9. Fault Tolerance and Interaction Protocols

#### 9.1. Error Handling Protocol

To ensure predictability and reliability, any AI agent or automated `command` is **obligated** to follow this protocol when an error occurs (e.g., script failure, invalid artifact, unexpected result).

1.  **Immediate Halt:** The agent must stop the execution of the current task chain to prevent further issues.
2.  **Failure Documentation:** The agent must create an entry in `journals/` for the current day with a `FAILURE` status.
      * **Failure Log Format:**
        ```markdown
        - Task Failed: `[[Name of the failed task or command]]`
          - **Status:** `FAILURE`
          - **Agent:** `[[Agent Name]]`
          - **Reason:** A brief but clear description of the cause of the failure.
          - **Logs:** A link to the log file or inclusion of key error messages.
        ```
3.  **User Notification:** The agent must inform the user about the failure, providing a link to the journal entry and recommendations for a possible fix.

#### 9.2. Human Approval Gates

The system aims for automation, but key strategic decisions must remain with a human. Approval gates are steps in `commands` where explicit user approval is required to proceed.

  * **Trigger:** A step in a `command` is marked as requiring confirmation (e.g., via the `human_approval_gate: true` property).
  * **Action:**
    1.  The agent pauses the execution of the `command` at this step.
    2.  It presents the artifact to the user for approval (e.g., "Here is the draft implementation plan for Phase 3: `[[phase-3-implementation-plan]]`").
    3.  Using the `ask_followup_question` tool, the agent requests explicit confirmation, offering options like: "Approve and continue," "Request revision," "Cancel."
    4.  The agent continues executing the `command` only after receiving a positive response.