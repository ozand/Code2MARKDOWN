# Code2MARKDOWN Project Overview

## Project Summary

Code2MARKDOWN is a Python-based Streamlit web application that generates structured Markdown documentation from source code projects. It allows users to interactively select files, apply filters, and use customizable templates to generate documentation.

## Key Features

- Interactive file selection with a visual tree structure
- Advanced filtering options (include/exclude patterns, file size limits)
- Multiple customizable Handlebars templates for different documentation needs
- Support for exporting generated documentation in TXT, MD, and XML formats
- Request history management with SQLite database storage
- Real-time processing and user feedback

## Technologies Used

- **Python 3.12+**
- **Streamlit** - Web application framework
- **Pybars3** - Handlebars templating engine
- **PathSpec** - Gitignore-style pattern matching
- **SQLite3** - Database for storing history
- **Pandas** - Data handling (used in history display)
- **Pyperclip** - Clipboard integration

## Project Architecture

The project follows a layered architecture:

- `app.py`: Main Streamlit application file
- `domain/`: Core business logic entities and value objects
  - `files.py`: File and directory node representations, ProjectTreeBuilder
  - `filters.py`: FilterSettings and FileSize value objects
  - `request.py`: GenerationRequest entity
- `application/`: Service layer
  - `services.py`: GenerationService for documentation creation
  - `repository.py`: Interface for history repository
- `infrastructure/`: Implementation details
  - `database.py`: SQLite implementation of IHistoryRepository
- `templates/`: Handlebars templates for documentation generation

## How to Run

1. Ensure Python 3.12+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

Alternatively, on Windows, you can use the provided batch scripts:
- `setup.bat`: Sets up the virtual environment and installs dependencies
- `start.bat`: Launches the application

## How to Use

1. Open the application in your browser (typically at `http://localhost:8501`)
2. Enter the path to your project folder
3. Select a template from the dropdown
4. Configure filter settings (optional):
   - Include/Exclude file patterns
   - Maximum file size
   - Show/hide excluded files
5. Scan the project folder to see the file structure
6. Interactively select files and folders to include
7. Click "Generate Markdown" to create documentation
8. Use "Copy to Clipboard" or download buttons to export the result

## Customization

- Add new templates by creating `.hbs` files in the `templates/` directory
- Modify default filters in `app.py`
- Extend functionality by adding new methods to `GenerationService`

## Development Notes

- The application uses caching for file tree structures to improve performance
- Binary files are automatically detected and excluded from processing
- File selection state is managed through Streamlit's session state
- The UI uses a wide layout for better visualization of file trees

## Project Quality Guidelines

The project includes quality guidelines in the `.roo/rules` directory:

1. **Python Project Quality Guideline** (`01-quality-guideline.md`):
   - Project initialization and dependency management using `uv`
   - Directory structure and organization mirroring `src/` and `tests/`
   - Import rules (absolute imports only) and architecture principles
   - Automated quality control with Ruff, pre-commit hooks, and mypy
   - Testing and coverage enforcement
   - Maintenance and refactoring practices

2. **Scripts Structure Guideline** (`02-scripts-structure.md`):
   - Separation of application code and auxiliary scripts
   - Versioning and documentation of scripts
   - Packaging logic into Python modules rather than shell commands
   - Environment isolation for development scripts
   - CI integration for auxiliary scripts
   - Mandatory log analysis after script execution
   - Script lifecycle management