"""Comprehensive unit tests for scripts/development/utils.py."""

import logging
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scripts.development.utils import (
    ScriptUtils,
    check_python_version,
    confirm_action,
    ensure_directory,
    find_files_by_pattern,
    format_file_size,
    get_file_info,
    get_logger,
    handle_script_error,
    log_execution_summary,
    prompt_for_input,
    safe_read_file,
    safe_write_file,
    select_from_options,
    setup_logging,
    validate_required_tools,
)


class TestScriptUtils:
    """Test cases for ScriptUtils class."""

    def test_setup_logging_basic(self, temp_dir: Path):
        """Test basic logging setup."""
        log_file = temp_dir / "test.log"
        logger = ScriptUtils.setup_logging(
            level="INFO", file_path=log_file, console=False
        )

        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO
        assert log_file.exists()

    def test_setup_logging_with_custom_format(self, temp_dir: Path):
        """Test logging setup with custom format."""
        log_file = temp_dir / "test.log"
        custom_format = "%(levelname)s - %(message)s"

        logger = ScriptUtils.setup_logging(
            level="DEBUG", format_string=custom_format, file_path=log_file, console=False
        )

        assert logger.level == logging.DEBUG
        assert log_file.exists()

    def test_setup_logging_console_only(self):
        """Test logging setup with console only."""
        logger = ScriptUtils.setup_logging(level="WARNING", console=True, file_path=None)

        assert logger.level == logging.WARNING
        assert len(logger.handlers) == 1  # Only console handler

    def test_get_logger(self):
        """Test get_logger function."""
        logger = ScriptUtils.get_logger("test.module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_log_execution_summary_success(self, mock_logger: Mock):
        """Test successful execution summary logging."""
        start_time = datetime(2024, 1, 1, 10, 0, 0)
        end_time = datetime(2024, 1, 1, 10, 5, 30)

        ScriptUtils.log_execution_summary(
            start_time=start_time,
            end_time=end_time,
            success=True,
            errors=None,
            logger=mock_logger,
        )

        # Verify log calls
        mock_logger.info.assert_any_call("=" * 50)
        mock_logger.info.assert_any_call("EXECUTION SUMMARY")
        mock_logger.info.assert_any_call("=" * 50)
        mock_logger.info.assert_any_call("Status: SUCCESS")
        mock_logger.info.assert_any_call("Start Time: 2024-01-01 10:00:00")
        mock_logger.info.assert_any_call("End Time: 2024-01-01 10:05:30")
        mock_logger.info.assert_any_call("Duration: 0:05:30")

    def test_log_execution_summary_with_errors(self, mock_logger: Mock):
        """Test execution summary with errors."""
        start_time = datetime(2024, 1, 1, 10, 0, 0)
        end_time = datetime(2024, 1, 1, 10, 1, 0)
        errors = ["Error 1", "Error 2"]

        ScriptUtils.log_execution_summary(
            start_time=start_time,
            end_time=end_time,
            success=False,
            errors=errors,
            logger=mock_logger,
        )

        # Verify error logging
        mock_logger.error.assert_any_call("Errors encountered: 2")
        mock_logger.error.assert_any_call("  - Error 1")
        mock_logger.error.assert_any_call("  - Error 2")

    def test_safe_read_file_success(self, temp_dir: Path):
        """Test successful file reading."""
        test_file = temp_dir / "test.txt"
        content = "Test content\nwith multiple lines"
        test_file.write_text(content)

        result = ScriptUtils.safe_read_file(test_file)
        assert result == content

    def test_safe_read_file_not_found(self, temp_dir: Path):
        """Test reading non-existent file."""
        test_file = temp_dir / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            ScriptUtils.safe_read_file(test_file)

    def test_safe_read_file_io_error(self, temp_dir: Path):
        """Test reading file with IO error."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        # Make file unreadable
        os.chmod(test_file, 0o000)
        try:
            with pytest.raises(IOError):
                ScriptUtils.safe_read_file(test_file)
        finally:
            # Restore permissions for cleanup
            os.chmod(test_file, 0o644)

    def test_safe_write_file_basic(self, temp_dir: Path):
        """Test basic file writing."""
        test_file = temp_dir / "output.txt"
        content = "Test content"

        ScriptUtils.safe_write_file(test_file, content)

        assert test_file.exists()
        assert test_file.read_text() == content

    def test_safe_write_file_with_backup(self, temp_dir: Path):
        """Test file writing with backup."""
        test_file = temp_dir / "output.txt"
        original_content = "Original content"
        new_content = "New content"

        # Create original file
        test_file.write_text(original_content)

        # Write with backup
        ScriptUtils.safe_write_file(test_file, new_content, backup=True)

        # Check both file and backup exist
        assert test_file.exists()
        assert test_file.read_text() == new_content

        backup_file = test_file.with_suffix(test_file.suffix + ".backup")
        assert backup_file.exists()
        assert backup_file.read_text() == original_content

    def test_safe_write_file_creates_directory(self, temp_dir: Path):
        """Test that safe_write_file creates parent directories."""
        test_file = temp_dir / "subdir" / "nested" / "output.txt"
        content = "Test content"

        ScriptUtils.safe_write_file(test_file, content)

        assert test_file.exists()
        assert test_file.read_text() == content

    def test_ensure_directory(self, temp_dir: Path):
        """Test directory creation."""
        test_dir = temp_dir / "new_directory"

        result = ScriptUtils.ensure_directory(test_dir)

        assert result == test_dir
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_ensure_directory_existing(self, temp_dir: Path):
        """Test ensuring existing directory."""
        test_dir = temp_dir / "existing_directory"
        test_dir.mkdir()

        result = ScriptUtils.ensure_directory(test_dir)

        assert result == test_dir
        assert test_dir.exists()

    def test_find_files_by_pattern_basic(self, temp_dir: Path):
        """Test basic file finding by pattern."""
        # Create test files
        (temp_dir / "test1.py").write_text("content")
        (temp_dir / "test2.py").write_text("content")
        (temp_dir / "subdir" / "test3.py").mkdir(parents=True)
        (temp_dir / "subdir" / "test3.py").write_text("content")
        (temp_dir / "readme.md").write_text("content")

        results = ScriptUtils.find_files_by_pattern("*.py", temp_dir)

        assert len(results) == 3
        assert all(f.suffix == ".py" for f in results)

    def test_find_files_by_pattern_recursive_false(self, temp_dir: Path):
        """Test non-recursive file finding."""
        # Create test files
        (temp_dir / "test1.py").write_text("content")
        (temp_dir / "subdir" / "test2.py").mkdir(parents=True)
        (temp_dir / "subdir" / "test2.py").write_text("content")

        results = ScriptUtils.find_files_by_pattern("*.py", temp_dir, recursive=False)

        assert len(results) == 1
        assert results[0].name == "test1.py"

    def test_find_files_by_pattern_glob(self, temp_dir: Path):
        """Test glob pattern matching."""
        # Create test files
        (temp_dir / "test_1.py").write_text("content")
        (temp_dir / "test_2.py").write_text("content")
        (temp_dir / "other.py").write_text("content")

        results = ScriptUtils.find_files_by_pattern(
            "test_*.py", temp_dir, recursive=False
        )

        assert len(results) == 2
        assert all("test_" in f.name for f in results)

    def test_confirm_action_yes(self, mock_user_input: Mock):
        """Test confirm_action with yes response."""
        mock_user_input.return_value = "y"

        result = ScriptUtils.confirm_action("Continue?")

        assert result is True
        mock_user_input.assert_called_once_with("Continue? [y/N]: ")

    def test_confirm_action_no(self, mock_user_input: Mock):
        """Test confirm_action with no response."""
        mock_user_input.return_value = "n"

        result = ScriptUtils.confirm_action("Continue?")

        assert result is False

    def test_confirm_action_default_yes(self, mock_user_input: Mock):
        """Test confirm_action with default yes."""
        mock_user_input.return_value = ""

        result = ScriptUtils.confirm_action("Continue?", default=True)

        assert result is True
        mock_user_input.assert_called_once_with("Continue? [Y/n]: ")

    def test_confirm_action_default_no(self, mock_user_input: Mock):
        """Test confirm_action with default no."""
        mock_user_input.return_value = ""

        result = ScriptUtils.confirm_action("Continue?", default=False)

        assert result is False

    def test_prompt_for_input_basic(self, mock_user_input: Mock):
        """Test basic input prompting."""
        mock_user_input.return_value = "test input"

        result = ScriptUtils.prompt_for_input("Enter value")

        assert result == "test input"
        mock_user_input.assert_called_once_with("Enter value: ")

    def test_prompt_for_input_with_default(self, mock_user_input: Mock):
        """Test input prompting with default value."""
        mock_user_input.return_value = ""

        result = ScriptUtils.prompt_for_input("Enter value", default="default")

        assert result == "default"
        mock_user_input.assert_called_once_with("Enter value [default]: ")

    def test_prompt_for_input_with_validator(self, mock_user_input: Mock):
        """Test input prompting with validator."""
        # First input is invalid, second is valid
        mock_user_input.side_effect = ["invalid", "123", "valid"]

        result = ScriptUtils.prompt_for_input("Enter number", validator=str.isdigit)

        assert result == "123"
        assert mock_user_input.call_count == 2

    def test_prompt_for_input_allow_empty(self, mock_user_input: Mock):
        """Test input prompting allowing empty input."""
        mock_user_input.return_value = ""

        result = ScriptUtils.prompt_for_input("Enter value", allow_empty=True)

        assert result == ""

    def test_select_from_options_single(self, mock_user_input: Mock):
        """Test single option selection."""
        mock_user_input.return_value = "2"

        options = ["Option A", "Option B", "Option C"]
        result = ScriptUtils.select_from_options(options)

        assert result == "Option B"

    def test_select_from_options_multiple(self, mock_user_input: Mock):
        """Test multiple option selection."""
        mock_user_input.return_value = "1,3"

        options = ["Option A", "Option B", "Option C"]
        result = ScriptUtils.select_from_options(options, allow_multiple=True)

        assert result == ["Option A", "Option C"]

    def test_select_from_options_invalid_selection(self, mock_user_input: Mock):
        """Test invalid option selection."""
        mock_user_input.side_effect = ["invalid", "5", "2"]

        options = ["Option A", "Option B", "Option C"]
        result = ScriptUtils.select_from_options(options)

        assert result == "Option B"
        assert mock_user_input.call_count == 3

    def test_select_from_options_empty_list(self):
        """Test selection with empty options list."""
        with pytest.raises(ValueError, match="Options list cannot be empty"):
            ScriptUtils.select_from_options([])

    def test_handle_script_error_with_exit(self, mock_logger: Mock):
        """Test error handling with exit."""
        error = ValueError("Test error")

        with pytest.raises(SystemExit) as exc_info:
            ScriptUtils.handle_script_error(
                error=error,
                context="Test context",
                logger=mock_logger,
                exit_on_error=True,
            )

        assert exc_info.value.code == 1
        mock_logger.error.assert_called_once_with("Test context - Error: Test error")
        mock_logger.debug.assert_called_once_with("Exception details:", exc_info=True)

    def test_handle_script_error_without_exit(self, mock_logger: Mock):
        """Test error handling without exit."""
        error = ValueError("Test error")

        ScriptUtils.handle_script_error(
            error=error, context="Test context", logger=mock_logger, exit_on_error=False
        )

        mock_logger.error.assert_called_once_with("Test context - Error: Test error")
        mock_logger.debug.assert_called_once_with("Exception details:", exc_info=True)

    def test_validate_required_tools_all_available(self):
        """Test tool validation when all tools are available."""
        # Mock shutil.which to return a path for all tools
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/tool"

            result = ScriptUtils.validate_required_tools(["git", "python", "node"])

            assert result is True
            assert mock_which.call_count == 3

    def test_validate_required_tools_missing_tools(self, mock_logger: Mock):
        """Test tool validation with missing tools."""

        # Mock shutil.which to return None for missing tools
        def mock_which_side_effect(tool):
            if tool == "missing-tool":
                return None
            return f"/usr/bin/{tool}"

        with patch("shutil.which", side_effect=mock_which_side_effect):
            with patch("logging.getLogger", return_value=mock_logger):
                result = ScriptUtils.validate_required_tools(
                    ["git", "missing-tool", "python"]
                )

                assert result is False
                mock_logger.error.assert_called_once_with(
                    "Missing required tools: missing-tool"
                )

    def test_check_python_version_compatible(self):
        """Test Python version check with compatible version."""
        with patch("sys.version_info", (3, 9, 0)):
            result = ScriptUtils.check_python_version("3.8")
            assert result is True

    def test_check_python_version_incompatible(self, mock_logger: Mock):
        """Test Python version check with incompatible version."""
        with patch("sys.version_info", (3, 7, 0)):
            with patch("logging.getLogger", return_value=mock_logger):
                result = ScriptUtils.check_python_version("3.8")

                assert result is False
                mock_logger.error.assert_called_once_with(
                    "Python 3.8 or higher is required. Current version: 3.7"
                )

    def test_format_file_size_bytes(self):
        """Test file size formatting for bytes."""
        result = ScriptUtils.format_file_size(512)
        assert result == "512.0 B"

    def test_format_file_size_kilobytes(self):
        """Test file size formatting for kilobytes."""
        result = ScriptUtils.format_file_size(1024)
        assert result == "1.0 KB"

    def test_format_file_size_megabytes(self):
        """Test file size formatting for megabytes."""
        result = ScriptUtils.format_file_size(1048576)  # 1 MB
        assert result == "1.0 MB"

    def test_format_file_size_gigabytes(self):
        """Test file size formatting for gigabytes."""
        result = ScriptUtils.format_file_size(1073741824)  # 1 GB
        assert result == "1.0 GB"

    def test_format_file_size_terabytes(self):
        """Test file size formatting for terabytes."""
        result = ScriptUtils.format_file_size(1099511627776)  # 1 TB
        assert result == "1.0 TB"

    def test_format_file_size_petabytes(self):
        """Test file size formatting for petabytes."""
        result = ScriptUtils.format_file_size(1125899906842624)  # 1 PB
        assert result == "1.0 PB"

    def test_get_file_info_file(self, temp_dir: Path):
        """Test getting file information."""
        test_file = temp_dir / "test.txt"
        content = "Test content for file info"
        test_file.write_text(content)

        info = ScriptUtils.get_file_info(test_file)

        assert info["path"] == str(test_file.absolute())
        assert info["size"] == len(content)
        assert info["size_formatted"] == f"{len(content)}.0 B"
        assert info["is_file"] is True
        assert info["is_dir"] is False
        assert info["extension"] == ".txt"
        assert info["name"] == "test.txt"
        assert info["stem"] == "test"
        assert isinstance(info["modified"], datetime)
        assert isinstance(info["created"], datetime)

    def test_get_file_info_directory(self, temp_dir: Path):
        """Test getting directory information."""
        test_dir = temp_dir / "test_directory"
        test_dir.mkdir()

        info = ScriptUtils.get_file_info(test_dir)

        assert info["path"] == str(test_dir.absolute())
        assert info["is_file"] is False
        assert info["is_dir"] is True
        assert info["extension"] == ""
        assert info["name"] == "test_directory"
        assert info["stem"] == "test_directory"

    def test_get_file_info_nonexistent(self, temp_dir: Path):
        """Test getting info for non-existent file."""
        test_file = temp_dir / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            ScriptUtils.get_file_info(test_file)


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    def test_setup_logging_convenience(self):
        """Test setup_logging convenience function."""
        logger = setup_logging(level="INFO")
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO

    def test_get_logger_convenience(self):
        """Test get_logger convenience function."""
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_log_execution_summary_convenience(self, mock_logger: Mock):
        """Test log_execution_summary convenience function."""
        start_time = datetime.now()
        end_time = datetime.now()

        # Should not raise any exceptions
        log_execution_summary(start_time, end_time, success=True, logger=mock_logger)

    def test_safe_read_file_convenience(self, temp_dir: Path):
        """Test safe_read_file convenience function."""
        test_file = temp_dir / "test.txt"
        content = "Test content"
        test_file.write_text(content)

        result = safe_read_file(test_file)
        assert result == content

    def test_safe_write_file_convenience(self, temp_dir: Path):
        """Test safe_write_file convenience function."""
        test_file = temp_dir / "output.txt"
        content = "Test content"

        safe_write_file(test_file, content)

        assert test_file.exists()
        assert test_file.read_text() == content

    def test_ensure_directory_convenience(self, temp_dir: Path):
        """Test ensure_directory convenience function."""
        test_dir = temp_dir / "new_directory"

        result = ensure_directory(test_dir)

        assert result == test_dir
        assert test_dir.exists()

    def test_find_files_by_pattern_convenience(self, temp_dir: Path):
        """Test find_files_by_pattern convenience function."""
        # Create test files
        (temp_dir / "test1.py").write_text("content")
        (temp_dir / "test2.py").write_text("content")

        results = find_files_by_pattern("*.py", temp_dir, recursive=False)

        assert len(results) == 2
        assert all(f.suffix == ".py" for f in results)

    def test_confirm_action_convenience(self, mock_user_input: Mock):
        """Test confirm_action convenience function."""
        mock_user_input.return_value = "y"

        result = confirm_action("Continue?")

        assert result is True

    def test_prompt_for_input_convenience(self, mock_user_input: Mock):
        """Test prompt_for_input convenience function."""
        mock_user_input.return_value = "test input"

        result = prompt_for_input("Enter value")

        assert result == "test input"

    def test_select_from_options_convenience(self, mock_user_input: Mock):
        """Test select_from_options convenience function."""
        mock_user_input.return_value = "1"

        options = ["Option A", "Option B"]
        result = select_from_options(options)

        assert result == "Option A"

    def test_handle_script_error_convenience(self, mock_logger: Mock):
        """Test handle_script_error convenience function."""
        error = ValueError("Test error")

        with pytest.raises(SystemExit):
            handle_script_error(error, logger=mock_logger)

    def test_validate_required_tools_convenience(self):
        """Test validate_required_tools convenience function."""
        with patch("shutil.which", return_value="/usr/bin/tool"):
            result = validate_required_tools(["git", "python"])
            assert result is True

    def test_check_python_version_convenience(self):
        """Test check_python_version convenience function."""
        with patch("sys.version_info", (3, 9, 0)):
            result = check_python_version("3.8")
            assert result is True

    def test_format_file_size_convenience(self):
        """Test format_file_size convenience function."""
        result = format_file_size(1024)
        assert result == "1.0 KB"

    def test_get_file_info_convenience(self, temp_dir: Path):
        """Test get_file_info convenience function."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        info = get_file_info(test_file)

        assert info["name"] == "test.txt"
        assert info["extension"] == ".txt"
