# Maintenance Guide

This document outlines the regular maintenance routines for the Code2MARKDOWN project to keep the codebase clean, efficient, and up-to-date.

## Dead Code Removal

To identify and remove unused code (dead code) from the project, use the following command:

```bash
ruff check . --select F401,F841 --fix
```

This command will:
- Identify unused imports (F401)
- Identify unused local variables (F841)
- Automatically fix these issues where possible

Run this command regularly to keep the codebase clean and maintainable.

**Note:** The command has identified an issue in `test_service_debug.py` with an unused local variable `template_content`. This should be addressed manually.

## Dependency Audit

To audit project dependencies and identify outdated packages, use the following command:

```bash
uv pip list --outdated
```

This command will list all dependencies that have newer versions available.