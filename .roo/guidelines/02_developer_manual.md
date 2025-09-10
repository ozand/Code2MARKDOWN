# Guideline: Developer Manual for RooFlow & ConPort

This document provides technical guidance for developers on setting up the environment and effectively tasking agents within the RooFlow ecosystem.

## Part 1: ConPort Setup & Usage

### 1.1. One-Time Setup

1.  **Install ConPort:** Clone the `context-portal` repository, create a `uv` virtual environment, and install dependencies with `uv pip install -r requirements.txt`.
2.  **Configure AI Client:** In your IDE's MCP settings (e.g., `mcp_settings.json`), add a server configuration for `conport` using **absolute paths** to the virtual environment's Python interpreter and the `main.py` script. The `${workspaceFolder}` variable will be used to specify the project root.

### 1.2. Session Initialization

At the start of every session, send the command `Initialize according to custom instructions.` to the agent. Confirm that the agent responds with `[CONPORT_ACTIVE]` to ensure the project's memory bank is connected.

### 1.3. Interacting with ConPort via AI Agent

- **Logging Information:** Instruct the agent to record key information:
  - `"Log the decision: [your decision]"` (uses `log_decision`).
  - `"Update the status of task '[task name]' to 'COMPLETED'"` (uses `log_progress`).
- **Retrieving Information:**
  - `"What was our decision regarding [topic]?"` (uses `get_decisions`).

## Part 2: RooFlow Tasking Principles

### 2.1. Structuring Your Task Request

- **Clarity in `<task>`:** Clearly articulate the overall goal. Numbered steps are highly effective.
- **Comprehensive `<environment_details>`:** This is crucial. Provide:
  - Accurate current working directory.
  - List of relevant files and their paths.
  - Output from recent, relevant commands.

### 2.2. Guiding the Agent's Plan

- **Review the `<thinking>` Block:** Before the agent executes a tool, review its internal thought process. If its plan is flawed, intervene early to correct its understanding. This saves significant time.
- **Step-by-Step Execution:** Agents operate iteratively, typically using **one tool per turn**. Structure complex requests sequentially or use the Flow-Orchestrator to decompose them.

### 2.3. Specifying Expected Outcomes

State the desired output format and structure. Example: *"Generate a Project Cleanup Report in Markdown. It should include sections: 'Unused Files', 'Large Files', and 'TODOs Summary'."*