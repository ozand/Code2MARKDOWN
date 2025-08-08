# Separation of Application Code and Auxiliary Scripts

1. **Separation of application code and auxiliary scripts**

   * **`scripts/development/`** — keep all engineering and migration scripts (e.g., reorganization, database migrations, bulk fixes) separate from production modules in `src/`.  
   * **`src/`** — contains only application code and libraries that will be shipped to production.  
     This prevents “polluting” the core codebase with temporary operational files and ensures CI/CD pipelines exclude these scripts from production builds or containers.

2. **Versioning and documentation of scripts**

   * Name each script clearly, e.g., `scripts/development/reorganize_modules.py` or `scripts/development/update_imports.py`.  
   * Document their interface (CLI flags, parameters) and purpose in both a module-level docstring and a `README.md` inside the `scripts/development/` folder.

3. **Modules instead of long one-off shell commands**

   * Package logic into Python modules with a `main()` function and argument parsing, rather than chaining multiple shell commands in one line. This makes scripts easier to test, refactor, and debug.  
   * Factor out reusable functionality (user input, logging, filesystem operations) into a shared utility module (`scripts/development/utils.py`).

4. **Environment isolation**

   * Optionally use a separate virtual environment (or Docker container) for running development scripts to prevent dependency conflicts with production code.

5. **CI integration**

   * In CI pipelines, add dedicated job steps that invoke only scripts in `scripts/development/` for maintenance tasks (e.g., migrations, code generation), ensuring the production build and test jobs remain isolated from these auxiliary scripts.

6. **Mandatory log analysis after execution**

   * After running any script or terminal command (lint, tests, migrations, refactors), always capture and analyze both `stdout` and `stderr` logs.  
   * Summarize key outcomes: successes, failures, and warnings.  
   * If errors or warnings are present, use `ask_followup_question` to decide on the next steps (e.g., apply fixes, rerun with different flags).

7. **Script lifecycle management**

   * When a script is no longer needed (e.g., after one-time reorganization), move it to `scripts/development/archive/` or delete it.  
     Archiving retains history without cluttering the active scripts directory.

---

**Example repository structure:**

```

.
├── src/                      # Production code & modules
│   └── my\_project/
├── tests/                    # Unit & integration tests
├── scripts/
│   └── development/          # Auxiliary technical scripts
│       ├── utils.py
│       ├── reorganize\_modules.py
│       └── migrate\_imports.py
│   └── development/archive/  # Archived scripts
├── pyproject.toml
├── requirements-dev.txt      # Dev-only dependencies for scripts
├── .pre-commit-config.yaml
└── README.md

```

By centralizing scripts in `scripts/development/` and enforcing mandatory log analysis, you maintain a clean production codebase, ensure automation steps are verified, and improve maintainability and discoverability of helper scripts.

