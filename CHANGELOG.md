# Changelog

All notable changes to Code2MARKDOWN will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
