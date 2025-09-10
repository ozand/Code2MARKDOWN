#!/usr/bin/env python3
"""
Shared utilities for development scripts.

This module provides common functionality used across multiple development scripts,
including logging setup, file operations, user interaction, and error handling.
Following the DRY principle to eliminate code duplication and ensure consistency.
"""

import logging
import shutil
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path


class ScriptUtils:
    """Collection of utility functions for development scripts."""

    @staticmethod
    def setup_logging(
        level: str = "INFO",
        format_string: str | None = None,
        file_path: str | Path | None = None,
        console: bool = True,
    ) -> logging.Logger:
        """
        Configure logging with project standards.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format_string: Custom format string, uses default if None
            file_path: Optional file path for file logging
            console: Whether to log to console

        Returns:
            Configured logger instance

        Example:
            >>> logger = setup_logging(level="DEBUG", file_path="script.log")
            >>> logger.info("Script started")
        """
        if format_string is None:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Create formatter
        formatter = logging.Formatter(format_string)

        # Get root logger
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, level.upper()))

        # Clear existing handlers
        logger.handlers.clear()

        # Console handler
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # File handler
        if file_path:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(file_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a properly configured logger instance.

        Args:
            name: Logger name (typically __name__)

        Returns:
            Logger instance

        Example:
            >>> logger = get_logger(__name__)
            >>> logger.info("Processing files...")
        """
        return logging.getLogger(name)

    @staticmethod
    def log_execution_summary(
        start_time: datetime,
        end_time: datetime,
        success: bool = True,
        errors: list[str] = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Log a standardized execution summary.

        Args:
            start_time: Script start time
            end_time: Script end time
            success: Whether execution was successful
            errors: List of error messages
            logger: Logger instance (uses root if None)

        Example:
            >>> start = datetime.now()
            >>> # ... script execution ...
            >>> end = datetime.now()
            >>> log_execution_summary(start, end, success=True)
        """
        if logger is None:
            logger = logging.getLogger()

        duration = end_time - start_time
        status = "SUCCESS" if success else "FAILED"

        logger.info("=" * 50)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Status: {status}")
        logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duration: {duration}")

        if errors:
            logger.error(f"Errors encountered: {len(errors)}")
            for error in errors:
                logger.error(f"  - {error}")

        logger.info("=" * 50)

    @staticmethod
    def safe_read_file(path: str | Path, encoding: str = "utf-8") -> str:
        """
        Read file with comprehensive error handling.

        Args:
            path: File path
            encoding: File encoding

        Returns:
            File contents

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read

        Example:
            >>> content = safe_read_file("config.yaml")
            >>> print(content)
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            return path.read_text(encoding=encoding)
        except Exception as e:
            raise OSError(f"Failed to read file {path}: {e}")

    @staticmethod
    def safe_write_file(
        path: str | Path,
        content: str,
        encoding: str = "utf-8",
        backup: bool = True,
        backup_suffix: str = ".backup",
    ) -> None:
        """
        Write file with safety features including optional backup.

        Args:
            path: File path
            content: Content to write
            encoding: File encoding
            backup: Whether to create backup
            backup_suffix: Suffix for backup file

        Example:
            >>> safe_write_file("output.txt", "Hello World", backup=True)
        """
        path = Path(path)

        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup if requested and file exists
        if backup and path.exists():
            backup_path = path.with_suffix(path.suffix + backup_suffix)
            shutil.copy2(path, backup_path)

        # Write file
        try:
            path.write_text(content, encoding=encoding)
        except Exception as e:
            raise OSError(f"Failed to write file {path}: {e}")

    @staticmethod
    def ensure_directory(path: str | Path) -> Path:
        """
        Create directory if it doesn't exist.

        Args:
            path: Directory path

        Returns:
            Path object for the directory

        Example:
            >>> config_dir = ensure_directory("config/settings")
            >>> print(config_dir)
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def find_files_by_pattern(
        pattern: str, root_dir: str | Path = ".", recursive: bool = True
    ) -> list[Path]:
        """
        Find files using glob patterns.

        Args:
            pattern: Glob pattern (e.g., "*.py", "**/*.md")
            root_dir: Root directory to search
            recursive: Whether to search recursively

        Returns:
            List of matching file paths

        Example:
            >>> md_files = find_files_by_pattern("**/*.md", "docs")
            >>> py_files = find_files_by_pattern("*.py", "src")
        """
        root_path = Path(root_dir)

        if recursive and not pattern.startswith("**"):
            pattern = f"**/{pattern}"

        return list(root_path.glob(pattern))

    @staticmethod
    def confirm_action(message: str, default: bool = False) -> bool:
        """
        Get user confirmation with consistent formatting.

        Args:
            message: Confirmation message
            default: Default response if user just presses Enter

        Returns:
            True if user confirms, False otherwise

        Example:
            >>> if confirm_action("Delete all temporary files?"):
            >>>     delete_temp_files()
        """
        choices = " [Y/n]" if default else " [y/N]"
        response = input(f"{message}{choices}: ").strip().lower()

        if not response:
            return default

        return response.startswith("y")

    @staticmethod
    def prompt_for_input(
        message: str,
        validator: Callable[[str], bool] | None = None,
        default: str | None = None,
        allow_empty: bool = False,
    ) -> str:
        """
        Get user input with optional validation.

        Args:
            message: Input prompt
            validator: Optional validation function
            default: Default value if user enters nothing
            allow_empty: Whether to allow empty input

        Returns:
            User input string

        Example:
            >>> name = prompt_for_input("Enter your name: ")
            >>> age = prompt_for_input("Enter your age: ", validator=str.isdigit)
        """
        prompt_message = f"{message}"
        if default is not None:
            prompt_message += f" [{default}]"
        prompt_message += ": "

        while True:
            response = input(prompt_message).strip()

            # Handle default
            if not response and default is not None:
                return default

            # Handle empty input
            if not response and not allow_empty:
                print("Input cannot be empty. Please try again.")
                continue

            # Validate if validator provided
            if validator and not validator(response):
                print("Invalid input. Please try again.")
                continue

            return response

    @staticmethod
    def select_from_options(
        options: list[str],
        message: str = "Select an option:",
        allow_multiple: bool = False,
    ) -> str | list[str]:
        """
        Present selection menu to user.

        Args:
            options: List of available options
            message: Selection prompt
            allow_multiple: Whether to allow multiple selections

        Returns:
            Selected option(s)

        Example:
            >>> options = ["Option A", "Option B", "Option C"]
            >>> choice = select_from_options(options)
            >>> print(f"You selected: {choice}")
        """
        if not options:
            raise ValueError("Options list cannot be empty")

        print(message)
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        if allow_multiple:
            print("Enter numbers separated by commas for multiple selections")

        while True:
            try:
                response = input("Enter your choice: ").strip()

                if allow_multiple:
                    indices = [int(x.strip()) - 1 for x in response.split(",")]
                    if all(0 <= i < len(options) for i in indices):
                        return [options[i] for i in indices]
                else:
                    index = int(response) - 1
                    if 0 <= index < len(options):
                        return options[index]

                print("Invalid selection. Please try again.")

            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def handle_script_error(
        error: Exception,
        context: str = "",
        logger: logging.Logger | None = None,
        exit_on_error: bool = True,
    ) -> None:
        """
        Standard error handling and reporting for scripts.

        Args:
            error: The exception that occurred
            context: Additional context about the error
            logger: Logger instance (uses root if None)
            exit_on_error: Whether to exit the script after handling

        Example:
            >>> try:
            >>>     risky_operation()
            >>> except Exception as e:
            >>>     handle_script_error(e, "Failed to process files")
        """
        if logger is None:
            logger = logging.getLogger()

        error_message = f"Error: {error}"
        if context:
            error_message = f"{context} - {error_message}"

        logger.error(error_message)
        logger.debug("Exception details:", exc_info=True)

        if exit_on_error:
            sys.exit(1)

    @staticmethod
    def validate_required_tools(tools_list: list[str]) -> bool:
        """
        Check for required system tools.

        Args:
            tools_list: List of tool names to check

        Returns:
            True if all tools are available, False otherwise

        Example:
            >>> if validate_required_tools(["git", "python", "node"]):
            >>>     print("All tools are available")
        """
        missing_tools = []

        for tool in tools_list:
            if shutil.which(tool) is None:
                missing_tools.append(tool)

        if missing_tools:
            logger = logging.getLogger()
            logger.error(f"Missing required tools: {', '.join(missing_tools)}")
            return False

        return True

    @staticmethod
    def check_python_version(min_version: str = "3.8") -> bool:
        """
        Validate Python version compatibility.

        Args:
            min_version: Minimum required version (e.g., "3.8", "3.9")

        Returns:
            True if version is compatible, False otherwise

        Example:
            >>> if check_python_version("3.9"):
            >>>     print("Python version is compatible")
        """
        current_version = sys.version_info
        required_version = tuple(map(int, min_version.split(".")))

        if current_version >= required_version:
            return True

        logger = logging.getLogger()
        logger.error(
            f"Python {min_version} or higher is required. "
            f"Current version: {current_version.major}.{current_version.minor}"
        )
        return False

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string

        Example:
            >>> print(format_file_size(1024))  # "1.0 KB"
            >>> print(format_file_size(1048576))  # "1.0 MB"
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.1f} PB"

    @staticmethod
    def get_file_info(file_path: str | Path) -> dict:
        """
        Get comprehensive file information.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information

        Example:
            >>> info = get_file_info("example.txt")
            >>> print(f"Size: {info['size']}")
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        stat = path.stat()

        return {
            "path": str(path.absolute()),
            "size": stat.st_size,
            "size_formatted": ScriptUtils.format_file_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "extension": path.suffix,
            "name": path.name,
            "stem": path.stem,
        }


# Convenience functions for backward compatibility and easy importing
def setup_logging(level="INFO", format_string=None, file_path=None, console=True):
    """Convenience function for setup_logging."""
    return ScriptUtils.setup_logging(level, format_string, file_path, console)


def get_logger(name):
    """Convenience function for get_logger."""
    return ScriptUtils.get_logger(name)


def log_execution_summary(start_time, end_time, success=True, errors=None, logger=None):
    """Convenience function for log_execution_summary."""
    return ScriptUtils.log_execution_summary(
        start_time, end_time, success, errors, logger
    )


def safe_read_file(path, encoding="utf-8"):
    """Convenience function for safe_read_file."""
    return ScriptUtils.safe_read_file(path, encoding)


def safe_write_file(
    path, content, encoding="utf-8", backup=True, backup_suffix=".backup"
):
    """Convenience function for safe_write_file."""
    return ScriptUtils.safe_write_file(path, content, encoding, backup, backup_suffix)


def ensure_directory(path):
    """Convenience function for ensure_directory."""
    return ScriptUtils.ensure_directory(path)


def find_files_by_pattern(pattern, root_dir=".", recursive=True):
    """Convenience function for find_files_by_pattern."""
    return ScriptUtils.find_files_by_pattern(pattern, root_dir, recursive)


def confirm_action(message, default=False):
    """Convenience function for confirm_action."""
    return ScriptUtils.confirm_action(message, default)


def prompt_for_input(message, validator=None, default=None, allow_empty=False):
    """Convenience function for prompt_for_input."""
    return ScriptUtils.prompt_for_input(message, validator, default, allow_empty)


def select_from_options(options, message="Select an option:", allow_multiple=False):
    """Convenience function for select_from_options."""
    return ScriptUtils.select_from_options(options, message, allow_multiple)


def handle_script_error(error, context="", logger=None, exit_on_error=True):
    """Convenience function for handle_script_error."""
    return ScriptUtils.handle_script_error(error, context, logger, exit_on_error)


def validate_required_tools(tools_list):
    """Convenience function for validate_required_tools."""
    return ScriptUtils.validate_required_tools(tools_list)


def check_python_version(min_version="3.8"):
    """Convenience function for check_python_version."""
    return ScriptUtils.check_python_version(min_version)


def format_file_size(size_bytes):
    """Convenience function for format_file_size."""
    return ScriptUtils.format_file_size(size_bytes)


def get_file_info(file_path):
    """Convenience function for get_file_info."""
    return ScriptUtils.get_file_info(file_path)


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logger = setup_logging(level="DEBUG")
    logger.info("Utils module loaded successfully")

    # Test some functions
    start_time = datetime.now()

    try:
        # Test file operations
        test_file = "test_output.txt"
        safe_write_file(test_file, "Test content", backup=False)
        content = safe_read_file(test_file)
        logger.info(f"Read content: {content}")

        # Test user interaction (commented out for non-interactive use)
        # choice = confirm_action("Continue with test?")
        # logger.info(f"User choice: {choice}")

        # Test file info
        info = get_file_info(test_file)
        logger.info(f"File info: {info}")

        # Cleanup
        Path(test_file).unlink()

    except Exception as e:
        handle_script_error(e, "Test execution failed", exit_on_error=False)

    finally:
        end_time = datetime.now()
        log_execution_summary(start_time, end_time, success=True)
