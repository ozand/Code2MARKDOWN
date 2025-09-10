# Guideline: Project Knowledge Base Management

This document provides the standard for organizing and maintaining the project's knowledge base in Logseq.

### 1. Knowledge Repository Structure

- `pages/`: The central repository for knowledge. Contains all main documents and symbolic links to rules.
- `journals/`: A chronological work log for daily notes.
- `.roo/`: The source of truth for operational files (rules, sops, etc.).

### 2. File Naming Conventions in `pages/`

- **User Stories:** `STORY-[CATEGORY]-[ID].md` (e.g., `STORY-API-1.md`)
- **Requirements:** `REQ-[CATEGORY]-[ID].md` (e.g., `REQ-UI-3.md`)

### 3. Linking Rules

- **Internal Links (to KB documents):** `[[page_name]]` (e.g., `[[REQ-UI-5]]`)
- **External Links (to code files):** Use a Logseq alias: `[[relative/path/to/file.py|`file.py`]]`

### 4. Mandatory Metadata

Every artifact in `pages/` **must** contain a properties block at the beginning of the file. Refer to the `03_metadata_schema_reference.md` for the specific schemas for Stories, Requirements, etc.