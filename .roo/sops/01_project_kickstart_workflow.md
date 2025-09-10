# SOP: Project Kickstart Workflow

This document describes the standard operating procedure for initializing a new project using RooFlow and ConPort to ensure correct setup of the environment and knowledge base.

### Step 0: Initial Environment Setup (One-Time)

If ConPort is being set up for the first time, follow these steps. Otherwise, proceed to Step 1.

1. **Install ConPort:**
   - Clone the context-portal repository.
   - Create and activate a Python virtual environment (`uv venv`).
   - Install dependencies (`uv pip install -r requirements.txt`).
2. **Configure AI Client (e.g., Roo Code):**
   - Open the MCP servers configuration file (e.g., `mcp_settings.json`).
   - Add the configuration for `conport`, using **absolute paths** to the Python interpreter in the ConPort virtual environment and to the `main.py` script.

### Step 1: Activate Virtual Environment (Mandatory for each session)

**Rule:** Before executing any commands in the project terminal, the virtual environment **must** be activated.

- **AI Agent Task:** "Before executing [command], ensure the .venv is active. If not, run `source .venv/bin/activate` (Linux) or `.venv\\Scripts\\activate` (Windows)."

### Step 2: Initialize ConPort for the Project

This must be done at the start of each new work session to connect the AI agent to the project's knowledge base.

1. **Send Initialization Command:** Start the dialog with the AI agent with the exact command:
   `Initialize according to custom instructions.`
2. **Check Status:** Ensure the agent responds with a message containing `[CONPORT_ACTIVE]`. If `[CONPORT_INACTIVE]` is shown, repeat the command.

### Step 3: Initial Knowledge Base Bootstrap (One-Time for new projects)

1. **Create Project Brief:**
   - In the project root, create `projectBrief.md`.
   - Describe the main goals, key features, target audience, and tech stack.
2. **Load Brief into ConPort:**
   - After initialization, the agent will detect `projectBrief.md` and ask to import its content into the Product Context. **Confirm this action.**
3. **Load Development Standards into ConPort:**
   - Ensure `project_development_guidelines.md` exists.
   - Task an agent: "Load the development standards into ConPort. Read the file `'docs/project_development_guidelines.md`' (see below for file content) and save its full content using the `log_custom_data` tool. Use parameters: category: 'ProjectStandards', key: 'DevelopmentGuidelines'."