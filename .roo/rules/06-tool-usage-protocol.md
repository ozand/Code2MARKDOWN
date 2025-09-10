# 6. Tool Preference Protocol

### 1. The Golden Rule

**MANDATE:** You **must** always prefer specialized RooCode tools (`read_file`, `list_files`, `write_to_file`, etc.) over the general-purpose `execute_command` tool. The `execute_command` tool should only be used for tasks that cannot be accomplished with a specialized tool.

### 2. Equivalency Table: What to Use Instead of Terminal Commands

This table defines which RooCode tool is preferred for performing common tasks.

| Instead of these terminal commands... | **Always use this RooCode tool** | Why this is better |
| :--- | :--- | :--- |
| `cat`, `head`, `tail`, `less`, `more` | **`<read_file>`** | [cite_start]Returns content with line numbers, supports partial reading of large files, and is safe[cite: 485, 487]. |
| `ls`, `find`, `tree` | **`<list_files>`** | [cite_start]Works recursively, respects `.gitignore` and `.rooignore`, and intelligently formats output for a better understanding of the project structure[cite: 445, 450]. |
| `echo "..." >`, `echo "..." >>` | **`<write_to_file>`** or **`<insert_content>`** | [cite_start]Provides an **interactive diff view** for approving changes, which is a critical security feature[cite: 679, 391]. Prevents accidental file overwrites. |
| `touch`, `mkdir` | **`<write_to_file>`** | `write_to_file` automatically creates the file and necessary directories. [cite_start]Explicitly creating an empty file or folder is rarely needed[cite: 680]. |
| `sed`, `awk` | **`<search_and_replace>`** or **`<apply_diff>`** | [cite_start]Provide powerful and safe methods for searching and replacing, including regex support and interactive approval[cite: 542, 241]. |
| `grep`, `rg` | **`<search_files>`** or **`<codebase_search>`** | [cite_start]`search_files` uses Ripgrep for fast searching and provides context[cite: 578, 583]. [cite_start]`codebase_search` performs semantic searches by meaning, not just keywords[cite: 354, 355]. |
| `mv`, `cp`, `rm` | **(Exception) `execute_command`** | There are no specialized tools for these operations yet. Use `execute_command`, but you **must** request confirmation from the user via `<ask_followup_question>` before deleting or moving files. |

### 3. When Using `execute_command` IS Justified

You **should** use `execute_command` for the following types of tasks:

* [cite_start]**Running scripts and processes:** Installing dependencies (`npm install`, `pip install`), starting development servers (`npm run dev`), building the project (`npm run build`)[cite: 383, 384, 387].
* [cite_start]**Working with version control systems:** `git status`, `git commit`, `git push`[cite: 385].
* [cite_start]**Executing specific utilities:** Running tests (`pytest`), linters (`eslint`), or other command-line tools that do not have a RooCode equivalent[cite: 388].
* **File system operations (with caution):** Moving, copying, and deleting files, as specified in the table above.

### 4. Rationale

This protocol exists to increase the **reliability, security, and efficiency** of your work. Specialized tools provide structured data, have built-in safety mechanisms (like diff approval), and are better integrated into the RooCode environment.