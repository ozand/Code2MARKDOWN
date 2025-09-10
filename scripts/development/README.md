title:: Development Scripts Documentation
---
# Development Scripts Directory

This directory contains auxiliary technical scripts for engineering, maintenance, and development tasks. These scripts are separate from production code and follow the guidelines outlined in [`rules.02-scripts-structure`](rules.02-scripts-structure.md).

## 📋 Table of Contents

- [Overview](#overview)
- [Available Scripts](#available-scripts)
- [Usage Guidelines](#usage-guidelines)
- [Common Workflows](#common-workflows)
- [Development Guidelines](#development-guidelines)
- [Troubleshooting](#troubleshooting)
- [Archive](#archive)

## 🔍 Overview

The `scripts/development/` directory contains Python modules designed to support development workflows, automate maintenance tasks, and provide utilities for project management. Each script is a self-contained module with proper CLI interfaces, logging, and documentation.

### Key Principles
- **Separation of Concerns**: Scripts are isolated from production code
- **Modular Design**: Each script has a clear, single purpose
- **Comprehensive Documentation**: All scripts include detailed usage instructions
- **Error Handling**: Robust error handling and logging
- **Testability**: Scripts are designed to be easily testable

## 🛠️ Available Scripts

### Knowledge Base Management

#### [`validate_kb.py`](validate_kb.py)
Comprehensive validator for the Logseq knowledge base that ensures all documentation follows project standards and maintains integrity across the entire knowledge graph.

**Purpose**: Validates the entire knowledge base according to strict project standards, checking link integrity, file structure, properties schema, status correctness, and preventing common documentation errors.

**Usage**:
```bash
# Validate the entire knowledge base with default project root
python scripts/development/validate_kb.py

# Validate specific project root
python scripts/development/validate_kb.py --project-root /path/to/project

# Run with uv for better dependency management
uv run python scripts/development/validate_kb.py
```

**Comprehensive Validation Checks**:

1. **Link Integrity** ✅
   - Verifies all `[[...]]` links point to existing pages
   - Ignores links in code blocks (```...``` and `...`) to prevent false positives
   - Checks both internal knowledge base links and external file references

2. **Correct Link Formatting** ✅
   - Ensures external file links follow the alias format `[[path/to/file.py|`file.py`]]`
   - Validates that alias filenames match actual filenames in the path
   - Verifies referenced files exist for local paths

3. **File Structure Validation** ✅
   - Validates User Story filenames follow `STORY-[CATEGORY]-[ID].md` pattern
   - Ensures Requirement filenames follow `REQ-[CATEGORY]-[ID].md` pattern
   - Checks that rule files are placed directly in `.roo/rules/` (no subdirectories)

4. **Properties Schema Validation** ✅
   - **User Stories**: Validates all required properties exist:
     - `type:: [[story]]`
     - `status:: [[TODO]]|[[DOING]]|[[DONE]]`
     - `priority:: [[high]]|[[medium]]|[[low]]`
     - `assignee:: [[@username]]`
     - `epic:: [[EPIC-NAME]]`
     - `related-reqs:: [[REQ-ID-1]], [[REQ-ID-2]]`
   - **Requirements**: Validates required properties:
     - `type:: [[requirement]]`
     - `status:: [[PLANNED]]|[[IMPLEMENTED]]|[[PARTIAL]]`

5. **Status Correctness** ✅
   - User Stories: Only allows `[[TODO]]`, `[[DOING]]`, `[[DONE]]`
   - Requirements: Only allows `[[PLANNED]]`, `[[IMPLEMENTED]]`, `[[PARTIAL]]`

6. **README Title Integrity** ✅
   - Ensures all `README.md` files have a `title::` property

7. **Temporary Artifact Detection** ✅
   - Prevents "raw" command output files (e.g., `raw.md`, `error.errors`) from being saved in `pages/`

8. **Misplaced Files Detection** ✅
   - Ensures markdown files are only in allowed directories: `pages/`, `journals/`, `.roo/rules/`
   - Validates root-level files against allowed list: `README.md`, `CONTRIBUTING.md`

9. **Gitignore Integration** ✅
   - Respects `.gitignore` patterns when scanning files
   - Filters out ignored files from validation

**Advanced Features**:
- **Multi-language Support**: Documentation and error messages in Russian and English
- **Comprehensive Error Reporting**: Detailed error messages with file paths and line numbers
- **Warning System**: Non-blocking issues reported as warnings
- **Performance Optimization**: Efficient regex patterns and file caching
- **Extensible Architecture**: Easy to add new validation rules

**Validation Workflow**:
1. **Discovery Phase**: Scans all markdown files in knowledge base directories
2. **Pattern Matching**: Uses regex to identify and categorize different file types
3. **Content Analysis**: Parses file content to extract properties and links
4. **Cross-Reference Validation**: Checks links against existing files and validates formats
5. **Schema Compliance**: Verifies all required properties and their values
6. **Report Generation**: Creates comprehensive validation report with errors and warnings

**Common Issues Detected**:
- Broken internal links pointing to non-existent pages
- Incorrect external file link formatting
- Missing required properties in User Stories or Requirements
- Invalid status values
- Files in unauthorized directories
- Temporary artifacts saved in knowledge base

**Integration with CI/CD**:
This script is integrated into the pre-commit hooks and should be run before commits to ensure knowledge base integrity. It's also used in CI pipelines to validate documentation quality.

**Performance Characteristics**:
- Processes hundreds of files efficiently
- Uses optimized regex patterns for link extraction
- Implements smart caching for repeated validations
- Provides progress indicators during long validation runs

#### [`sync_git_kb.py`](sync_git_kb.py)
Synchronizes User Story statuses between the Logseq knowledge base and Git commits to ensure consistency between documentation and actual development progress.

**Purpose**: Analyzes User Story files in the knowledge base and compares their status with Git commit history to identify discrepancies where story statuses don't match their actual implementation state.

**Usage**:
```bash
# Generate synchronization report with default project root
python scripts/development/sync_git_kb.py --report-path reports/kb-sync-report.json

# Specify custom project root
python scripts/development/sync_git_kb.py --report-path reports/sync-report.json --project-root /path/to/project

# Run with uv for better dependency management
uv run python scripts/development/sync_git_kb.py --report-path reports/sync-report.json
```

**Key Features**:
- **Automated Status Detection**: Scans all User Story files in `pages/` directory
- **Git Integration**: Uses `git log --grep` to search for commits containing story IDs
- **Comprehensive Analysis**: Identifies two types of mismatches:
  - Stories marked as `[[DONE]]` but without corresponding Git commits
  - Stories marked as `[[TODO]]` or `[[DOING]]` but with existing commits
- **Detailed JSON Reports**: Generates structured reports with file paths, story IDs, issues, and recommended actions
- **Pattern-based Recognition**: Uses regex patterns to identify story files and extract status information
- **Error Handling**: Gracefully handles missing directories and Git command failures

**Synchronization Logic**:
1. **Story Discovery**: Finds all files matching `STORY-*.md` pattern in `pages/` directory
2. **Status Extraction**: Parses story files to extract status properties (`[[TODO]]`, `[[DOING]]`, `[[DONE]]`)
3. **Git History Check**: Searches Git commit messages for story ID references
4. **Mismatch Detection**: Compares story status with commit existence
5. **Report Generation**: Creates detailed JSON report with findings and recommendations

**Report Format**:
```json
[
  {
    "file_path": "pages/STORY-API-5.md",
    "story_id": "STORY-API-5",
    "issue": "Status is DONE, but no corresponding Git commit was found.",
    "recommended_action": "Change status to [[TODO]] or investigate."
  }
]
```

**Common Use Cases**:
- **Pre-release Validation**: Ensure all completed stories have corresponding commits
- **Status Cleanup**: Identify stories that need status updates after development
- **Progress Tracking**: Verify that documentation accurately reflects development progress
- **Quality Assurance**: Maintain consistency between knowledge base and actual work

**Integration with Development Workflow**:
This script should be run regularly to maintain synchronization between the knowledge base and Git history, especially before releases or status reviews.

#### [`generate_logseq_config.py`](generate_logseq_config.py)
Automatically generates and updates Logseq configuration files to maintain proper knowledge base visibility.

**Purpose**: Analyzes project structure and generates/updates `logseq/config.edn`, automatically hiding all directories that are not part of the knowledge base to ensure Logseq focuses only on relevant content.

**Usage**:
```bash
# Generate/update Logseq configuration
python scripts/development/generate_logseq_config.py

# Run with uv for better dependency management
uv run python scripts/development/generate_logseq_config.py
```

**Key Features**:
- **Automatic Project Analysis**: Scans the entire project root directory
- **Whitelist-based Filtering**: Only shows knowledge base directories (`journals`, `logseq`, `pages`, `assets`)
- **Safe Configuration Updates**: Preserves existing Logseq settings while updating only the `:hidden` parameter
- **Directory Creation**: Automatically creates the `logseq/` directory if it doesn't exist
- **Non-destructive**: Only modifies the `:hidden` configuration, leaving other settings intact

**Knowledge Base Directories** (always visible):
- `journals/` - Daily notes and chronological work log
- `logseq/` - Logseq configuration and metadata
- `pages/` - Main knowledge base documents
- `assets/` - Images and media files

**Hidden Directories** (automatically detected and hidden):
- `src/` - Production source code
- `tests/` - Test files
- `scripts/` - Development scripts
- `.venv/` - Virtual environment
- `.git/` - Git repository data
- `.roo/` - AI agent operational files
- Any other non-knowledge-base directories

**Configuration Format**:
The script generates an EDN configuration file with the `:hidden` parameter containing a vector of directory names to hide from Logseq's interface.

**Example Output**:
```
:hidden ["src" "tests" "scripts" ".venv" ".git" ".roo"]
```

**Integration with Project Workflow**:
This script should be run after any significant project structure changes to ensure Logseq maintains optimal performance by only indexing relevant knowledge base content.

### Git Integration

#### [`parser_script.py`](parser_script.py)
Parses raw markdown files containing documentation blocks and extracts them into separate files. Designed to process AI-generated documentation blocks and organize them into proper project structure.

**Purpose**: Extracts documentation blocks from raw markdown files and creates individual documentation files following project naming conventions.

**Usage**:
```bash
# Parse default raw.md file
python scripts/development/parser_script.py

# Parse specific file with verbose output
python scripts/development/parser_script.py --input my_docs.md --verbose

# Parse to specific output directory
python scripts/development/parser_script.py --input raw.md --output-dir docs/

# Parse with custom expected filenames
python scripts/development/parser_script.py --input raw.md --expected gap.md roadmap.md

# Dry run to see what would be created
python scripts/development/parser_script.py --input raw.md --dry-run
```

**Key Features**:
- Extracts documentation blocks from markdown files using regex patterns
- Supports custom expected filenames list
- Dry-run mode for safe testing
- Comprehensive logging with debug output
- Error handling with detailed error messages
- Automatic directory creation for output files
- Integration with shared utilities for logging and file operations

**Expected Documentation Format**:
The script expects documentation blocks in the format:
```markdown
`filename.md`
```markdown
# Document Title
Document content here...
```
```

**Default Expected Files**:
- `gap.md` - Gap analysis documentation
- `requirements.md` - Project requirements
- `backlog.md` - Product backlog
- `roadmap.md` - Development roadmap
- `sprint-plan.md` - Sprint planning documents
- `documentation-maintenance.md` - Documentation maintenance guidelines

#### [`analyze_architecture.py`](analyze_architecture.py)
Analyzes project architecture to detect circular imports and potential architectural issues. This script is used by the pre-commit hook to prevent circular dependencies.

**Purpose**: Detects circular imports in the project's Python modules to maintain a clean architecture and prevent issues that can arise from circular dependencies.

**Usage**:
```bash
# Analyze the project for circular imports
python scripts/development/analyze_architecture.py
```

**Key Features**:
- **Comprehensive File Discovery**: Automatically discovers all Python files in the project
- **Import Graph Construction**: Builds a detailed graph of module imports across the codebase
- **Circular Dependency Detection**: Uses depth-first search to identify circular import chains
- **Clear Reporting**: Provides detailed output of any detected circular dependencies
- **Non-destructive**: Only analyzes the codebase without making changes

**Analysis Process**:
1. **File Discovery**: Scans the project directory for all Python files
2. **Import Extraction**: Parses each file to extract import statements
3. **Graph Building**: Constructs an import graph mapping module relationships
4. **Cycle Detection**: Uses DFS algorithm to identify circular dependencies
5. **Reporting**: Outputs findings with clear descriptions of any issues

**Integration with Pre-commit**:
This script is integrated into the pre-commit hooks as the `check-circular-imports` hook and will automatically run during the commit process to prevent circular dependencies from being committed.

**Exit Codes**:
- `0`: No circular imports detected
- `1`: Circular imports detected

### Shared Utilities

#### [`utils.py`](utils.py)
Comprehensive shared utility module providing common functionality for all development scripts. Following the DRY principle to eliminate code duplication and ensure consistency across the development toolchain.

**Purpose**: Provides a robust, well-tested collection of utility functions that handle logging, file operations, user interaction, error handling, and system validation for development scripts.

**Key Features**:

**🔧 Logging Management**
- **Flexible Logging Setup**: Configurable log levels, formats, and output destinations
- **Dual Output Support**: Console and file logging simultaneously
- **Custom Format Strings**: Project-standard log formatting with timestamps and log levels
- **Logger Instance Management**: Proper logger naming and hierarchy management

**📁 Safe File Operations**
- **Atomic File Writing**: Safe file creation with optional backup functionality
- **Comprehensive Error Handling**: Detailed error messages for file operation failures
- **Encoding Management**: UTF-8 encoding support with proper error handling
- **Directory Creation**: Automatic directory creation with parent directories
- **File Information**: Comprehensive file metadata extraction (size, dates, permissions)

**👤 User Interaction Utilities**
- **Confirmation Prompts**: Standardized yes/no confirmation dialogs
- **Input Validation**: Configurable input validation with custom validators
- **Selection Menus**: Interactive selection from option lists with single/multiple choice support
- **Default Values**: Support for default responses and empty input handling

**⚠️ Error Handling & Reporting**
- **Standardized Error Format**: Consistent error message formatting across scripts
- **Exception Context**: Detailed error context with stack trace logging
- **Graceful Exit**: Proper script termination with appropriate exit codes
- **Debug Information**: Optional debug logging with exception details

**🔍 System Validation**
- **Tool Availability**: Check for required system tools and dependencies
- **Python Version**: Validate Python version compatibility
- **File Existence**: Robust file existence and accessibility checks

**📊 Utility Functions**
- **File Size Formatting**: Human-readable file size formatting (B, KB, MB, GB, TB, PB)
- **File Pattern Matching**: Glob pattern-based file discovery with recursive search
- **Path Management**: Cross-platform path handling and normalization

**🛡️ Safety Features**
- **Backup Creation**: Optional file backup before modifications
- **Atomic Operations**: All-or-nothing file operations to prevent corruption
- **Validation**: Input validation and sanitization for user interactions
- **Error Recovery**: Graceful handling of partial failures

**API Reference**:

**Logging Functions**:
```python
# Setup logging with custom configuration
logger = setup_logging(level="DEBUG", file_path="script.log")

# Get properly configured logger instance
logger = get_logger(__name__)

# Log execution summary with timing information
log_execution_summary(start_time, end_time, success=True, errors=[])
```

**File Operations**:
```python
# Safe file reading with comprehensive error handling
content = safe_read_file("config.yaml", encoding="utf-8")

# Safe file writing with optional backup
safe_write_file("output.txt", "content", backup=True, backup_suffix=".backup")

# Ensure directory exists
config_dir = ensure_directory("config/settings")
```

**User Interaction**:
```python
# Get user confirmation
if confirm_action("Delete all temporary files?", default=False):
    delete_temp_files()

# Prompt for validated input
age = prompt_for_input("Enter your age:", validator=str.isdigit)

# Select from options
choice = select_from_options(["Option A", "Option B", "Option C"])
```

**System Validation**:
```python
# Check for required tools
if validate_required_tools(["git", "python", "node"]):
    print("All tools available")

# Validate Python version
if check_python_version("3.8"):
    print("Python version is compatible")
```

**File Utilities**:
```python
# Find files by pattern
md_files = find_files_by_pattern("**/*.md", "docs", recursive=True)

# Get comprehensive file information
info = get_file_info("example.txt")
print(f"Size: {info['size_formatted']}")
```

**Error Handling**:
```python
# Standardized error handling
try:
    risky_operation()
except Exception as e:
    handle_script_error(e, "Failed to process files", exit_on_error=True)
```

**Integration with Development Scripts**:
The utils module is designed to be imported by all development scripts and provides:
- Consistent logging behavior across all scripts
- Standardized error handling and user feedback
- Reusable file operations with safety guarantees
- Cross-platform compatibility and path handling
- Extensible architecture for adding new utility functions

**Best Practices**:
- Always use absolute imports: `from scripts.development.utils import setup_logging`
- Configure logging at script startup for consistent behavior
- Use safe file operations instead of direct file system calls
- Implement proper error handling with context information
- Validate user input and system requirements early in script execution

**Performance Characteristics**:
- Minimal overhead for utility function calls
- Efficient file operations with proper resource management
- Memory-conscious implementation for large file processing
- Cross-platform compatibility without performance penalties

## 📖 Usage Guidelines

### Running Scripts

All scripts support standard Python execution with command-line arguments:

```bash
# Basic execution
python scripts/development/script_name.py

# With arguments
python scripts/development/script_name.py --arg1 value1 --arg2 value2

# With help
python scripts/development/script_name.py --help
```

### Using uv (Recommended)

For better dependency management and isolation:

```bash
# Run with uv
uv run python scripts/development/script_name.py

# With arguments
uv run python scripts/development/script_name.py --project-root . --verbose
```

### Environment Variables

Some scripts may use environment variables:
- `PROJECT_ROOT`: Override default project root directory
- `LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `DRY_RUN`: Perform dry-run operations where supported

## 🔄 Common Workflows

### Knowledge Base Validation Workflow

```bash
# 1. Validate knowledge base
uv run python scripts/development/validate_kb.py

# 2. Fix any reported issues
# [Manual fixes based on validation report]

# 3. Re-validate to confirm fixes
uv run python scripts/development/validate_kb.py
```

### Git-Knowledge Base Synchronization Workflow

```bash
# 1. Generate sync report
uv run python scripts/development/sync_git_kb.py --report-path reports/sync-report.json

# 2. Review report and update story statuses
# [Manual updates based on report]

# 3. Commit changes with proper story references
git add pages/STORY-*.md
git commit -m "Update story statuses based on Git sync (STORY-DEV-5)"
```

### Logseq Configuration Update Workflow

```bash
# Update Logseq configuration after project structure changes
uv run python scripts/development/generate_logseq_config.py

# Verify configuration
cat logseq/config.edn
```

## 📝 Development Guidelines

### Creating New Scripts

When creating new development scripts, follow these guidelines:

1. **Use the utils module**: Import and use [`utils.py`](utils.py) for common operations
2. **Implement proper CLI**: Use `argparse` for command-line interfaces
3. **Add comprehensive logging**: Use the logging utilities from utils
4. **Include error handling**: Implement robust error handling and user feedback
5. **Document thoroughly**: Add module-level docstrings and usage examples
6. **Follow naming conventions**: Use descriptive names like `task_description.py`

### Script Template

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.

Detailed explanation of purpose, functionality, and use cases.
"""

import argparse
import logging
from pathlib import Path
from scripts.development.utils import setup_logging, get_logger, handle_script_error

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Brief description")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    # Add more arguments as needed
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)
    logger = get_logger(__name__)
    
    try:
        # Script logic here
        logger.info("Starting script execution")
        
        # Your code here
        
        logger.info("Script completed successfully")
        
    except Exception as e:
        handle_script_error(e, context="Script execution failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
```

## 📊 Log Analysis Protocol

All script executions must follow the mandatory log analysis protocol as defined in [`rules.02-scripts_structure`](rules.02-scripts_structure.md). This ensures that script outputs are properly monitored, analyzed, and validated.

### Log Analyzer Script

The primary tool for log analysis is the [`log_analyzer.py`](log_analyzer.py) script, which provides comprehensive analysis capabilities:

```bash
# Analyze an existing log file
python scripts/development/log_analyzer.py --log-file script.log

# Execute a command and analyze its output
python scripts/development/log_analyzer.py --command "python my_script.py"

# Execute a command, save output to file, and analyze
python scripts/development/log_analyzer.py --command "python my_script.py" --output script.log
```

### Log Analysis Categories

The log analyzer categorizes messages into four types:

1. **Errors** - Critical failures that prevent script completion
2. **Warnings** - Non-critical issues that should be reviewed
3. **Successes** - Confirmation of completed operations
4. **Info** - General progress information and status updates

### Integration with Development Scripts

All development scripts should follow the log analysis integration patterns:

1. **Use Standard Logging**: Utilize the project's logging utilities from [`utils.py`](utils.py)
2. **Structured Output**: Format log messages with clear indicators for different levels
3. **Execution Summaries**: Include start/end timestamps and execution status
4. **Error Handling**: Properly catch and log exceptions with context

See [`log_analysis_protocol.md`](log_analysis_protocol.md) for detailed guidelines and best practices.

### CI/CD Integration

In continuous integration pipelines, ensure all script executions are analyzed:

```yaml
- name: Run validation script
  run: |
    python scripts/development/validate_kb.py > validation.log 2>&1
    python scripts/development/log_analyzer.py --log-file validation.log
```

## 🔧 Troubleshooting

### Common Issues

#### Permission Errors
```bash
# Make script executable
chmod +x scripts/development/script_name.py

# Or run with python explicitly
python scripts/development/script_name.py
```

#### Import Errors
```bash
# Ensure you're running from project root
cd /path/to/project/root
python scripts/development/script_name.py

# Or set PYTHONPATH
PYTHONPATH=. python scripts/development/script_name.py
```

#### Missing Dependencies
```bash
# Install development dependencies
uv sync

# Or install specific packages
uv add --dev package-name
```

### Getting Help

Each script includes built-in help:
```bash
python scripts/development/script_name.py --help
```

For additional support:
- Check the script's module-level docstring
- Review this README for usage examples
- Examine the script's source code for detailed implementation
- Check project documentation in [`pages/`](../../pages/) directory

## 📦 Archive

Obsolete scripts are moved to [`archive/`](archive/) directory. See [`archive/README.md`](archive/README.md) for information about archived scripts and the archival process.

## 🔗 Related Documentation

- [`rules.02-scripts-structure`](rules.02-scripts-structure.md) - Script structure guidelines
- [`log_analysis_protocol.md`](log_analysis_protocol.md) - Log analysis protocol documentation
- [`STORY-DEV-1`](STORY-DEV-1.md) - User story for this documentation improvement
- Project Hub - Central project documentation
- Individual script documentation in each script file

## 📞 Support

For issues, questions, or suggestions regarding development scripts:
1. Check existing documentation and help output
2. Review relevant user stories in the knowledge base
3. Create a new issue or user story if needed
4. Follow the project's contribution guidelines

---
*This documentation is part of the Code2Markdown project development infrastructure.*