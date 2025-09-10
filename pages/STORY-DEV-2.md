type:: [[story]]
status:: [[TODO]]
priority:: [[high]]
assignee:: [[@documentation-writer]]
epic:: [[Development-Scripts-Improvement]]
related-reqs:: [[REQ-DEV-3]], [[REQ-DEV-4]]

# Shared Utilities Module for Development Scripts

## User Story
As a developer writing maintenance and utility scripts, I want a shared utilities module that provides common functionality, so that I can avoid code duplication and maintain consistency across all development scripts.

## Acceptance Criteria

### Core Functionality Requirements
1. **Logging Utilities**: Standardized logging setup with configurable levels, formats, and output destinations
2. **File System Operations**: Common file operations like safe file reading/writing, directory creation, and path validation
3. **User Input Handling**: Consistent prompts, confirmations, and input validation
4. **Error Handling**: Standardized error reporting and exception handling patterns
5. **Configuration Management**: Utilities for loading and validating configuration files

### Specific Utility Functions
1. **Logging Setup**:
   - `setup_logging(level="INFO", format=None, file_path=None)` - Configure logging with project standards
   - `get_logger(name)` - Get a properly configured logger instance
   - `log_execution_summary(start_time, end_time, success=True, errors=[])` - Standard execution summary

2. **File Operations**:
   - `safe_read_file(path, encoding="utf-8")` - Read file with error handling
   - `safe_write_file(path, content, encoding="utf-8", backup=True)` - Write file with backup option
   - `ensure_directory(path)` - Create directory if it doesn't exist
   - `find_files_by_pattern(pattern, root_dir=".")` - Find files using glob patterns

3. **User Interaction**:
   - `confirm_action(message, default=False)` - Get user confirmation with consistent formatting
   - `prompt_for_input(message, validator=None, default=None)` - Get user input with validation
   - `select_from_options(options, message="Select an option:")` - Present selection menu

4. **Error Handling**:
   - `handle_script_error(error, context="")` - Standard error handling and reporting
   - `validate_required_tools(tools_list)` - Check for required system tools
   - `check_python_version(min_version="3.8")` - Validate Python version compatibility

### Quality and Design Requirements
1. **Modularity**: Each utility category should be in its own submodule or class
2. **Type Hints**: All functions must have proper type annotations
3. **Documentation**: Comprehensive docstrings with examples for all public functions
4. **Error Handling**: Robust error handling with meaningful error messages
5. **Testing**: Functions should be designed to be easily testable

### Integration Requirements
1. **Import Structure**: Support both `import utils` and `from utils import specific_function` patterns
2. **Configuration**: Respect project-wide configuration settings
3. **Compatibility**: Work with existing scripts without breaking changes
4. **Extensibility**: Easy to add new utility functions following the same patterns

## Technical Implementation Notes
- Follow the guidelines from [`rules.02-scripts-structure`](rules.02-scripts-structure.md)
- Use absolute imports for all internal project dependencies
- Implement proper logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Support both console and file logging simultaneously
- Include timestamps and script names in log messages
- Provide colored output for console logging when supported

## Definition of Done
- [ ] [`scripts/development/utils.py`](scripts/development/utils.py) exists with all core utility functions
- [ ] All functions have comprehensive docstrings with usage examples
- [ ] Type hints are implemented for all public functions
- [ ] Error handling is robust and provides meaningful messages
- [ ] Logging utilities support both console and file output
- [ ] File operations include safety features (backups, validation)
- [ ] User interaction utilities provide consistent experience
- [ ] Module is properly structured and can be imported in multiple ways
- [ ] Documentation includes usage examples for each utility category
- [ ] Existing scripts can be refactored to use the new utilities
- [ ] Unit tests are provided for utility functions (separate story)

## Related Files
- [`doc/rules/02-scripts-structure.md`](doc/rules/02-scripts-structure.md) - Script structure guidelines
- [`scripts/development/`](scripts/development/) - Development scripts directory
- Existing scripts that can benefit from shared utilities:
  - [`scripts/development/validate_kb.py`](scripts/development/validate_kb.py)
  - [`scripts/development/sync_git_kb.py`](scripts/development/sync_git_kb.py)
  - [`scripts/development/generate_logseq_config.py`](scripts/development/generate_logseq_config.py)

## Future Considerations
- Consider creating submodules for different utility categories (logging, filesystem, user interaction)
- Add configuration file support for default settings
- Implement plugin system for extensible utilities
- Add progress bars and status indicators for long-running operations