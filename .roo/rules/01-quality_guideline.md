# Python Project Quality Guideline

## 1\. Project Initialization & Dependency Management

  - Use `uv init <project>` to bootstrap your project (creates `pyproject.toml` + `.venv`).
  - Manage dependencies with `uv add <package>` (runtime) and `uv add --dev <package>` (dev).
  - Synchronize environments via `uv sync`.

-----

## 2\. Directory Structure & Organization

  - Mirror the `src` and `tests` directories:

    ```text
    my_project/
    ├── src/my_project/
    │   ├── payments/
    │   └── search/
    └── tests/
        ├── payments/
        └── search/
    ```

  - Keep `.gitignore` up-to-date to exclude logs, build artifacts, and temp files.

-----

## 3\. Imports & Architecture

  - Always use **absolute imports**; forbid relative imports (`from ..module import ...`).
  - Enforce the **Dependency Inversion Principle**: high-level modules should depend on abstractions.

-----

## 4\. Automated Quality Control

  - Configure `Ruff` in `pyproject.toml`:

    ```toml
    [tool.ruff]
    line-length = 90
    select = ["F","E","W","I","UP","B","BLE"]
    ignore = ["E501"]

    [tool.ruff.format]
    quote-style = "double"
    ```

  - Enable `pre-commit` hooks:

    ```yaml
    -   repo: https://github.com/astral-sh/ruff-pre-commit
        hooks:
          - id: ruff
            args: [--fix]
          - id: ruff-format
    -   repo: https://github.com/pre-commit/mirrors-mypy
        hooks:
          - id: mypy
    -   repo: local
        hooks:
          - id: validate-kb
            name: Validate Knowledge Base
            entry: python scripts/development/validate_kb.py
            language: python
            types: [markdown]
            pass_filenames: false
    ```

  - Run `pre-commit install` once to activate checks on every commit.

-----

## 5\. Testing & Coverage

  - Place tests under the `tests` directory, mirroring `src`.

  - Execute tests with `uv run pytest`.

  - Enforce coverage:

    ```bash
    pytest --cov=src --cov-report=xml
    ```

-----

## 6\. Maintenance & Refactoring

  - **Dead code removal**: `ruff check . --select F401,F841 --fix`.
  - **Dependency audits**: perform a monthly check with `uv pip list --outdated`.
  - Follow the "small steps" rule when refactoring:
    1.  Make an isolated change
    2.  Run tests
    3.  Commit
    4.  Repeat