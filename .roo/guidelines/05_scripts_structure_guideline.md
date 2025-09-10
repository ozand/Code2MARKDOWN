# Guideline: Separation of Application Code and Auxiliary Scripts

1.  **`scripts/development/`**: Keep all engineering and migration scripts separate from production modules in `src/`.
2.  **`src/`**: Contains only application code and libraries that will be shipped to production.
    * This prevents "polluting" the core codebase with temporary operational files.
3.  **Versioning and documentation**: Name each script clearly and document its purpose in a module-level docstring.
4.  **Modules over shell commands**: Package logic into Python modules with a `main()` function rather than chaining multiple shell commands.
5.  **Mandatory log analysis**: After running any script or terminal command, always capture and analyze both `stdout` and `stderr` logs.