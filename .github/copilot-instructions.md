---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

## HEADERS

This file defines the rules, coding standards, workflow guidelines, references, documentation structure, and best practices for the AI coding assistant within this project. It is a living document that evolves with the project.

## TECH STACK

*   Python 3.12+
*   Streamlit (for the user interface)
*   Handlebars templating (pybars3)
*   pathspec (for .gitignore parsing)
*   SQLite (for request history)
*   pandas
*   pyperclip

## PROJECT DOCUMENTATION & CONTEXT SYSTEM

*   README.md: Project overview, setup instructions, features, and contribution guidelines.
*   Templates directory: Contains Handlebars templates for different documentation generation tasks.
*   CHANGELOG.md: Records significant changes and version updates. Documents significant changes and version updates.
*   CLEANUP_REPORT.md: Documents dependency cleanup efforts (if applicable).
*   INTERACTIVE_SELECTION_GUIDE.md: User guide for the interactive file selection feature.

## CODING STANDARDS

*   Follow PEP 8 guidelines for Python code.
*   Use descriptive variable and function names.
*   Write clear and concise comments.
*   Ensure code is modular and reusable.
*   Handle errors gracefully with try-except blocks.
*   Validate user inputs to prevent security vulnerabilities.

## FILE FILTERING RULES

*   Respect `.gitignore` files to exclude specified files and directories.
*   Exclude common virtual environment folders (e.g., `venv`, `node_modules`).
*   Exclude package lock files (e.g., `package-lock.json`).
*   Define file extensions to be processed (e.g., `.py`, `.js`, `.md`).
*   Provide UI elements to configure which file types are processed and which are excluded.
*   Ensure that when a parent folder is unchecked in the file tree, all subfolders and files within it are also deactivated.
*   Folders/files specified in the "Folders or files to exclude" UI element must be excluded from the generated markdown.
*   Support wildcard patterns for file and folder exclusion (e.g., `*.js`, `temp*`, `node_modules`).
*   Add a button to read `.gitignore` and automatically add exclusions.
*   Add buttons for quick processing of specific folders: "AI Agents" (memory-bank, .specstory) and "docs".
*   Link Filter Settings with File Selection: Only files available for processing should be displayed in the File Selection tree.
*   Add a selector or checkbox to "Show Excluded Files and Folders". When active, excluded items should be displayed but visually distinct (e.g., grayed out, strikethrough).

## TEMPLATE RULES

*   Use Handlebars templates for generating documentation.
*   Provide a variety of templates for different use cases (e.g., README generation, code documentation, security analysis).
*   Ensure templates are well-structured and easy to maintain.

## DATABASE RULES

*   Use SQLite for storing request history.
*   Implement pagination for efficient display of history.
*   Sanitize database inputs to prevent SQL injection attacks.
*   Ensure that the request history is persistent across sessions.
*   Improve the history table to include paths and other relevant information to easily identify processed data, including the project name, number of files processed, and applied filters.

## WORKFLOW & RELEASE RULES

*   Use Git for version control.
*   Create feature branches for new development.
*   Use pull requests for code review.
*   Implement a CI/CD pipeline with GitHub Actions.
*   Tag releases with semantic versioning (e.g., v1.0.0).

## DEBUGGING

*   Use structured logging for debugging.
*   Implement checks for missing dependencies.
*   Test application startup to identify import errors.

## GIT RULES

*   Commit messages should be descriptive and follow conventional format.
*   Use `.gitignore` to exclude unnecessary files.
*   Create tags for releases.
*   Push changes to the remote repository regularly.

## ERROR HANDLING

*   Handle `ModuleNotFoundError` for missing dependencies.
*   Display user-friendly error messages in the Streamlit app.
*   Log errors for debugging purposes.
*   Handle `StreamlitAPIException` for expanders nested inside other expanders.
*   Handle `UTF-8` decode errors by skipping binary files.

## USER INTERFACE (UI) RULES

*   Provide a clear and intuitive user interface.
*   Use Streamlit components for interactive elements.
*   Display loading indicators during long-running tasks.
*   Provide one-click copy functionality for generated content.
*   Offer download options in various formats (txt, md, xml).
*   Use tooltips and clear labels for UI elements.
*   Implement a file structure view with a maximum depth of 3 levels, allowing users to select which folders to include in the documentation.
*   Provide UI elements to configure which file types are processed and which are excluded.
*   Implement an interactive file selection tree, allowing users to choose which folders to include in the documentation.
*   The file selection tree should display a maximum depth of 3 levels.
*   The UI should allow users to configure which file types are processed and which are excluded.
*   Provide quick selection tools (e.g., "Select All," "Code Only," "Clear").
*   Display a live file counter to provide feedback on the number of files selected.
*   Add a button to read `.gitignore` and automatically add exclusions.
*   Add buttons for quick processing of specific folders: "AI Agents" (memory-bank, .specstory) and "docs".
*   The Filter Settings should be linked with the File Selection tree, so that only files available for processing are displayed.
*   Add a selector or checkbox to "Show Excluded Files and Folders". When active, excluded items should be displayed but visually distinct (e.g., grayed out, strikethrough).

## SECURITY RULES

*   Validate file paths to prevent unauthorized access.
*   Sanitize user inputs to prevent injection attacks.

## DEPENDENCIES

*   Use `requirements.txt` to manage project dependencies.
*   Keep dependencies up-to-date.
*   Only include necessary packages to minimize project size.

## FILE DOWNLOAD FUNCTIONALITY

*   Implement download options in TXT, MD, and XML formats.
*   Provide download buttons on the main page and in the history section.
*   Use appropriate MIME types for each file format.
*   Automatically name files for download (e.g., `{project_name}_documentation.{ext}`).

## XML CONVERSION

*   Create an XML structure with metadata (project name, generation date, generator).
*   Include the generated Markdown content within the XML structure.
*   The XML structure should include the project name, generation date, and generator.
*   The XML structure should include:
    ```xml
    <project>
      <metadata>
        <name>ProjectName</name>
        <generated_at>2025-06-10T16:47:57</generated_at>
        <generator>Code2MARKDOWN</generator>
      </metadata>
      <content>[Markdown content]</content>
    </project>
    ```
*   Clean XML content to ensure it is well-formed by escaping or removing invalid characters.

## TESTING

*   Create unit tests for core functionality.
*   Test file filtering, project structure generation, and other critical features.
*   Ensure tests pass before merging code.

## CI/CD

*   Use GitHub Actions for continuous integration.
*   Automate testing and linting.
*   Deploy changes automatically to a staging or production environment.