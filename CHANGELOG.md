# Changelog

All notable changes to Code2MARKDOWN will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-07-22

### Added
- **Interactive File Selection**: Visual file tree with checkboxes for selecting specific files/folders
- **Advanced Filter Settings**: Customizable include/exclude patterns and file size limits
- **Project Structure Preview**: Shows file tree with up to 3 levels of nesting 
- **Smart Selection Tools**: Quick buttons for "Select All", "Code Files Only", and "Clear Selection"
- **Real-time File Count**: Display of selected files count
- **GitIngest-style UI**: Inspired by GitIngest's filtering interface

### Changed  
- **Enhanced UI Layout**: Added expandable sections for filter settings and file selection
- **Improved File Processing**: Uses user-selected files instead of hardcoded filters
- **Dynamic Project Structure**: Builds structure based on selected files only
- **Better User Control**: More granular control over what gets included in documentation

### Technical Improvements
- New functions: `get_file_tree_structure()`, `render_file_tree_ui()`, `get_filtered_files_interactive()`
- Enhanced `generate_markdown()` with custom filter parameters
- Session state management for filter settings and file selection
- Support for custom include/exclude patterns

## [1.1.1] - 2025-06-10

### Removed
- **Redundant dependency files**: Cleaned up requirements_minimal.txt and requirements_new.txt
- **System-wide dependencies**: Removed 362 unnecessary packages from requirements_new.txt

### Changed
- **Streamlined dependencies**: Kept only 5 core packages in requirements.txt
- **Virtual environment**: Rebuilt for clean state
- **Setup process**: Verified all dependencies are actually used in code

### Dependencies verified
- `streamlit>=1.38.0` - Main UI framework
- `pybars3>=0.9.7` - Handlebars template engine
- `pathspec>=0.12.1` - File filtering and exclusion
- `pyperclip>=1.9.0` - Clipboard operations
- `pandas>=2.2.3` - Data handling and processing

## [1.1.0] - 2025-06-10

### Added
- **Multi-format download functionality**: Support for TXT, MD, and XML formats
- **Enhanced history management**: Format selector and download options for historical records
- **XML export with metadata**: Includes project name, generation timestamp, and generator info
- **Improved user interface**: 3-column action layout (Copy | Download | Delete)
- **Comprehensive documentation**: Download guide and usage instructions
- **Test coverage**: Unit tests for all download functions

### Changed
- **UI layout**: Expanded action buttons section with download options
- **History page**: Enhanced with format selection and download capabilities
- **File naming**: Automatic project-based naming for downloaded files

### Technical
- Added XML conversion using ElementTree with pretty formatting
- Implemented format-specific MIME types for proper browser handling
- Enhanced error handling for download operations
- Maintained backward compatibility with existing features

## [1.0.1] - 2025-06-10

### Fixed
- **Dependency issue**: Added missing `pybars3` package to requirements.txt
- **Path resolution**: Fixed start.bat script path references
- **Installation**: Improved setup.bat with better error handling

### Changed
- **Requirements**: Simplified requirements.txt to core dependencies only
- **Documentation**: Enhanced troubleshooting section in README

## [1.0.0] - 2025-06-10

### Added
- **Initial release**: Complete Streamlit-based application
- **Template system**: 15+ Handlebars templates for different use cases
- **Smart filtering**: .gitignore pattern matching and common exclusions
- **History management**: SQLite-based storage with pagination
- **Clipboard integration**: One-click copying with pyperclip
- **Project analysis**: Automatic directory tree generation
- **Batch scripts**: Automated setup and launch for Windows
