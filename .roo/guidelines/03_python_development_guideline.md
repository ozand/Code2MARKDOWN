# Guideline: Python Project Development

This document contains the core development rules and standards for Python projects.

## 1. Environment and Dependency Management

### 1.1. Virtual Environment (CRITICAL)

**Rule:** The virtual environment **must** be activated before running any project-specific commands (uv, pytest, ruff).
- **Activation (Linux/macOS):** `source .venv/bin/activate`
- **Activation (Windows):** `.venv\\Scripts\\activate`

### 1.2. Package Management

- **Tool:** **Exclusively uv** must be used for Python package management.
- **Installation:** `uv add <package>` (runtime) and `uv add --dev <package>` (dev).
- **Execution:** `uv run <tool-name>`.

## 2. Code Quality and Style

- **Typing:** All code must include type hints.
- **Documentation:** All public APIs must have detailed docstrings.
- **Line Length:** The maximum line length is 88 characters.
- **Imports:** Always use **absolute imports**.

## 3. Testing

- **Framework:** Tests are run using `uv run pytest`.
- **Coverage:** Tests must cover primary use cases, edge cases, and error handling. Every bug fix must be accompanied by a regression test.

## 4. Static Analysis Tools

### 4.1. Formatting and Linting (Ruff)

- **Format:** `uv run ruff format .`
- **Check & Auto-fix:** `uv run ruff check . --fix`

### 4.2. Type Checking (Pyright)

- **Command:** `uv run pyright`

### 4.3. Pre-commit Hooks

- **Configuration:** `.pre-commit-config.yaml` manages all static analysis tools.
- **Execution:** Tools are run automatically on every commit after `pre-commit install` is run once.

## 5. Version Control (Git)

- **Commit Messages:** Must follow Conventional Commits format. For commits related to a GitHub issue, use the `Github-Issue:#<number>` trailer.
- **Pull Requests (PRs):** A PR must contain a detailed, high-level description of the changes.