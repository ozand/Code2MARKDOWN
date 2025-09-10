"""Comprehensive tests for scripts/development/log_analyzer.py."""

from pathlib import Path
from unittest.mock import Mock, patch

from scripts.development.log_analyzer import (
    LogAnalyzer,
    execute_and_log,
    main,
)


class TestLogAnalyzer:
    """Test cases for LogAnalyzer class."""

    def test_analyzer_initialization(self, mock_logger: Mock):
        """Test analyzer initialization."""
        analyzer = LogAnalyzer(mock_logger)

        assert analyzer.logger == mock_logger
        assert isinstance(analyzer.errors, list)
        assert isinstance(analyzer.warnings, list)
        assert isinstance(analyzer.successes, list)
        assert isinstance(analyzer.info_messages, list)
        assert len(analyzer.errors) == 0
        assert len(analyzer.warnings) == 0
        assert len(analyzer.successes) == 0
        assert len(analyzer.info_messages) == 0

    def test_analyze_log_content_basic(self, mock_logger: Mock):
        """Test basic log content analysis."""
        analyzer = LogAnalyzer(mock_logger)

        content = """2024-01-01 10:00:00 - INFO - Script started
2024-01-01 10:00:01 - ERROR - Something went wrong
2024-01-01 10:00:02 - WARNING - This is a warning
2024-01-01 10:00:03 - SUCCESS - Operation completed
2024-01-01 10:00:04 - DEBUG - Debug information
"""

        result = analyzer.analyze_log_content(content)

        assert len(result["errors"]) == 1
        assert "ERROR - Something went wrong" in result["errors"][0]

        assert len(result["warnings"]) == 1
        assert "WARNING - This is a warning" in result["warnings"][0]

        assert len(result["successes"]) == 1
        assert "SUCCESS - Operation completed" in result["successes"][0]

        assert len(result["info"]) == 2
        info_text = " ".join(result["info"])
        assert "INFO - Script started" in info_text
        assert "DEBUG - Debug information" in info_text

    def test_analyze_log_content_case_insensitive(self, mock_logger: Mock):
        """Test log analysis with case-insensitive matching."""
        analyzer = LogAnalyzer(mock_logger)

        content = """2024-01-01 10:00:00 - info - Lowercase info
2024-01-01 10:00:01 - ERROR - Uppercase error
2024-01-01 10:00:02 - warning - Lowercase warning
2024-01-01 10:00:03 - Success - Mixed case success
"""

        result = analyzer.analyze_log_content(content)

        assert len(result["errors"]) == 1
        assert len(result["warnings"]) == 1
        assert len(result["successes"]) == 1
        assert len(result["info"]) == 1

    def test_analyze_log_content_multiple_matches(self, mock_logger: Mock):
        """Test log analysis with multiple matches of each type."""
        analyzer = LogAnalyzer(mock_logger)

        content = """2024-01-01 10:00:00 - ERROR - First error
2024-01-01 10:00:01 - CRITICAL - Critical error
2024-01-01 10:00:02 - err: - Error with colon
2024-01-01 10:00:03 - error: - Error with colon and lowercase
2024-01-01 10:00:04 - WARNING - First warning
2024-01-01 10:00:05 - warn: - Warning with colon
2024-01-01 10:00:06 - SUCCESS - First success
2024-01-01 10:00:07 - COMPLETED - Completed success
2024-01-01 10:00:08 - ok: - OK success
2024-01-01 10:00:09 - success: - Success with colon
"""

        result = analyzer.analyze_log_content(content)

        assert len(result["errors"]) == 4
        assert len(result["warnings"]) == 2
        assert len(result["successes"]) == 4
        assert len(result["info"]) == 0

    def test_analyze_log_content_empty_lines(self, mock_logger: Mock):
        """Test log analysis with empty lines."""
        analyzer = LogAnalyzer(mock_logger)

        content = """2024-01-01 10:00:00 - INFO - First line

2024-01-01 10:00:01 - ERROR - Error line


2024-01-01 10:00:02 - WARNING - Warning line
"""

        result = analyzer.analyze_log_content(content)

        # Should ignore empty lines
        assert len(result["errors"]) == 1
        assert len(result["warnings"]) == 1
        assert len(result["info"]) == 1

    def test_analyze_log_content_complex_patterns(self, mock_logger: Mock):
        """Test log analysis with complex patterns and edge cases."""
        analyzer = LogAnalyzer(mock_logger)

        content = """2024-01-01 10:00:00 - Starting process with error handling
2024-01-01 10:00:01 - Process failed with exception: ValueError
2024-01-01 10:00:02 - Traceback information follows
2024-01-01 10:00:03 - File "/path/to/file.py", line 42, in function
2024-01-01 10:00:04 - WARNING: deprecated function used
2024-01-01 10:00:05 - CAUTION: low disk space
2024-01-01 10:00:06 - SUCCESS: backup created successfully
2024-01-01 10:00:07 - PASSED: all tests passed
2024-01-01 10:00:08 - OK: operation completed
2024-01-01 10:00:09 - Regular info message
"""

        result = analyzer.analyze_log_content(content)

        # Should catch error-related terms
        assert len(result["errors"]) >= 2  # "error" and "exception"

        # Should catch warning-related terms
        assert len(result["warnings"]) >= 2  # "WARNING" and "CAUTION"

        # Should catch success-related terms
        assert len(result["successes"]) >= 3  # "SUCCESS", "PASSED", "OK"

        # Regular info should not be categorized
        assert len(result["info"]) >= 1

    def test_generate_report_no_issues(self, mock_logger: Mock):
        """Test report generation with no issues."""
        analyzer = LogAnalyzer(mock_logger)

        # Analyze content with no errors or warnings
        content = """2024-01-01 10:00:00 - INFO - Script started
2024-01-01 10:00:01 - SUCCESS - Operation completed
2024-01-01 10:00:02 - INFO - Script finished
"""
        analyzer.analyze_log_content(content)

        report = analyzer.generate_report()

        assert "LOG ANALYSIS REPORT" in report
        assert "SUMMARY" in report
        assert "Errors:     0" in report
        assert "Warnings:   0" in report
        assert "Successes:  1" in report
        assert "✅ No critical issues detected" in report

    def test_generate_report_with_errors(self, mock_logger: Mock):
        """Test report generation with errors."""
        analyzer = LogAnalyzer(mock_logger)

        content = """2024-01-01 10:00:00 - ERROR - Critical error occurred
2024-01-01 10:00:01 - WARNING - This is a warning
2024-01-01 10:00:02 - SUCCESS - Some operation succeeded
"""
        analyzer.analyze_log_content(content)

        report = analyzer.generate_report()

        assert "LOG ANALYSIS REPORT" in report
        assert "SUMMARY" in report
        assert "Errors:     1" in report
        assert "Warnings:   1" in report
        assert "Successes:  1" in report
        assert "ERRORS DETECTED" in report
        assert "WARNINGS DETECTED" in report
        assert "SUCCESS MESSAGES" in report
        assert "❌ Critical errors detected" in report

    def test_generate_report_with_warnings_only(self, mock_logger: Mock):
        """Test report generation with warnings only."""
        analyzer = LogAnalyzer(mock_logger)

        content = """2024-01-01 10:00:00 - WARNING - This is a warning
2024-01-01 10:00:01 - SUCCESS - Operation completed
"""
        analyzer.analyze_log_content(content)

        report = analyzer.generate_report()

        assert "Warnings:   1" in report
        assert "Successes:  1" in report
        assert "ERRORS DETECTED" not in report
        assert "WARNINGS DETECTED" in report
        assert "⚠️  Warnings detected" in report

    def test_should_ask_next_steps(self, mock_logger: Mock):
        """Test next steps recommendation logic."""
        analyzer = LogAnalyzer(mock_logger)

        # No issues - should not ask
        content = "2024-01-01 10:00:00 - INFO - Everything is fine"
        analyzer.analyze_log_content(content)
        assert analyzer.should_ask_next_steps() is False

        # With warnings - should ask
        content = "2024-01-01 10:00:00 - WARNING - Something to check"
        analyzer.analyze_log_content(content)
        assert analyzer.should_ask_next_steps() is True

        # With errors - should ask
        content = "2024-01-01 10:00:00 - ERROR - Something went wrong"
        analyzer.analyze_log_content(content)
        assert analyzer.should_ask_next_steps() is True


class TestExecuteAndLog:
    """Test cases for execute_and_log function."""

    def test_execute_and_log_success(self, mock_logger: Mock):
        """Test successful command execution and logging."""
        with patch("subprocess.Popen") as mock_popen:
            # Mock process
            mock_process = Mock()
            mock_process.stdout = ["Line 1", "Line 2", "Line 3"]
            mock_process.wait.return_value = 0
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            result = execute_and_log("echo 'test command'", None)

            assert result == 0
            mock_popen.assert_called_once()

            # Verify logging calls
            mock_logger.info.assert_any_call("Executing command: echo 'test command'")
            mock_logger.info.assert_any_call("Line 1")
            mock_logger.info.assert_any_call("Line 2")
            mock_logger.info.assert_any_call("Line 3")
            mock_logger.info.assert_any_call("Command completed with exit code: 0")

    def test_execute_and_log_with_log_file(self, temp_dir: Path, mock_logger: Mock):
        """Test command execution with log file output."""
        log_file = temp_dir / "test.log"

        with patch("subprocess.Popen") as mock_popen:
            # Mock process
            mock_process = Mock()
            mock_process.stdout = ["Test output line"]
            mock_process.wait.return_value = 0
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            result = execute_and_log("echo 'test'", str(log_file))

            assert result == 0
            assert log_file.exists()

            # Check log file content
            log_content = log_file.read_text()
            assert "Test output line" in log_content

    def test_execute_and_log_failure(self, mock_logger: Mock):
        """Test command execution failure."""
        with patch("subprocess.Popen") as mock_popen:
            # Mock process that fails
            mock_process = Mock()
            mock_process.stdout = ["Error line 1", "Error line 2"]
            mock_process.wait.return_value = 1
            mock_process.returncode = 1
            mock_popen.return_value = mock_process

            result = execute_and_log("false", None)

            assert result == 1
            mock_logger.info.assert_any_call("Command completed with exit code: 1")

    def test_execute_and_log_exception(self, mock_logger: Mock):
        """Test command execution with exception."""
        with patch("subprocess.Popen") as mock_popen:
            # Mock process that raises exception
            mock_popen.side_effect = Exception("Command not found")

            with patch(
                "scripts.development.log_analyzer.handle_script_error"
            ) as mock_handle_error:
                result = execute_and_log("nonexistent-command", None)

                assert result == 1
                mock_handle_error.assert_called_once()


class TestMainFunction:
    """Test cases for main function."""

    def test_main_analyze_existing_log_file(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with existing log file analysis."""
        # Create log file
        log_file = temp_dir / "test.log"
        log_content = """2024-01-01 10:00:00 - INFO - Script started
2024-01-01 10:00:01 - ERROR - Something went wrong
2024-01-01 10:00:02 - WARNING - This is a warning
2024-01-01 10:00:03 - SUCCESS - Operation completed
"""
        log_file.write_text(log_content)

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.log_analyzer.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.log_analyzer.get_logger", return_value=mock_logger
            ):
                with patch("sys.argv", ["log_analyzer.py", "--log-file", str(log_file)]):
                    with patch("builtins.print") as mock_print:
                        result = main()

        assert result == 0

        # Verify report was printed
        mock_print.assert_called()
        printed_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "LOG ANALYSIS REPORT" in printed_output
        assert "Errors:     1" in printed_output
        assert "Warnings:   1" in printed_output

    def test_main_execute_command(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with command execution."""
        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.log_analyzer.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.log_analyzer.get_logger", return_value=mock_logger
            ):
                with patch(
                    "scripts.development.log_analyzer.execute_and_log", return_value=0
                ) as mock_execute:
                    with patch(
                        "sys.argv", ["log_analyzer.py", "--command", 'echo "test"']
                    ):
                        with patch("builtins.print") as mock_print:
                            result = main()

        assert result == 0
        mock_execute.assert_called_once_with('echo "test"', None)

    def test_main_execute_command_with_output(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with command execution and output file."""
        output_file = temp_dir / "output.log"

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.log_analyzer.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.log_analyzer.get_logger", return_value=mock_logger
            ):
                with patch(
                    "scripts.development.log_analyzer.execute_and_log", return_value=0
                ) as mock_execute:
                    with patch(
                        "sys.argv",
                        [
                            "log_analyzer.py",
                            "--command",
                            'echo "test"',
                            "--output",
                            str(output_file),
                        ],
                    ):
                        with patch("builtins.print") as mock_print:
                            result = main()

        assert result == 0
        mock_execute.assert_called_once_with('echo "test"', str(output_file))

    def test_main_no_arguments(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with no arguments."""
        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.log_analyzer.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.log_analyzer.get_logger", return_value=mock_logger
            ):
                with patch("sys.argv", ["log_analyzer.py"]):
                    with patch("builtins.print") as mock_print:
                        result = main()

        assert result == 1
        mock_logger.error.assert_called_once_with(
            "Either --log-file or --command must be specified"
        )

    def test_main_log_file_not_found(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with non-existent log file."""
        nonexistent_file = temp_dir / "nonexistent.log"

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.log_analyzer.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.log_analyzer.get_logger", return_value=mock_logger
            ):
                with patch(
                    "sys.argv", ["log_analyzer.py", "--log-file", str(nonexistent_file)]
                ):
                    with patch("builtins.print") as mock_print:
                        result = main()

        assert result == 1
        mock_logger.error.assert_called_once_with(
            f"Log file not found: {nonexistent_file}"
        )

    def test_main_with_verbose_logging(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with verbose logging."""
        log_file = temp_dir / "test.log"
        log_file.write_text("INFO - Test log")

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.log_analyzer.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.log_analyzer.get_logger", return_value=mock_logger
            ):
                with patch(
                    "sys.argv",
                    ["log_analyzer.py", "--log-file", str(log_file), "--verbose"],
                ):
                    with patch("builtins.print") as mock_print:
                        result = main()

        assert result == 0
        mock_setup_logging.assert_called_once_with(level="DEBUG")


class TestIntegration:
    """Integration tests for the log analyzer."""

    def test_end_to_end_log_analysis(self, temp_dir: Path):
        """Test complete end-to-end log analysis workflow."""
        # Create comprehensive log file
        log_file = temp_dir / "comprehensive.log"
        log_content = """2024-01-01 10:00:00 - INFO - Development script started
2024-01-01 10:00:01 - DEBUG - Initializing components
2024-01-01 10:00:02 - WARNING - Configuration file not found, using defaults
2024-01-01 10:00:03 - ERROR - Failed to connect to database: Connection refused
2024-01-01 10:00:04 - CRITICAL - Database connection critical failure
2024-01-01 10:00:05 - INFO - Attempting to recover from database error
2024-01-01 10:00:06 - SUCCESS - Successfully connected to backup database
2024-01-01 10:00:07 - INFO - Processing 150 files
2024-01-01 10:00:08 - WARNING - File 'document.pdf' is corrupted, skipping
2024-01-01 10:00:09 - ERROR - Failed to process file 'data.xlsx': Invalid format
2024-01-01 10:00:10 - SUCCESS - Processed 148 files successfully
2024-01-01 10:00:11 - INFO - Script execution completed
2024-01-01 10:00:12 - SUCCESS - All operations finished successfully
"""
        log_file.write_text(log_content)

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.log_analyzer.setup_logging"
        ) as mock_setup_logging:
            with patch("scripts.development.log_analyzer.get_logger"):
                with patch("sys.argv", ["log_analyzer.py", "--log-file", str(log_file)]):
                    with patch("builtins.print") as mock_print:
                        result = main()

        assert result == 0

        # Verify comprehensive report was generated
        mock_print.assert_called()
        printed_output = " ".join(str(call) for call in mock_print.call_args_list)

        # Check summary counts
        assert "Errors:     2" in printed_output
        assert "Warnings:   2" in printed_output
        assert "Successes:  3" in printed_output
        assert "Info:       5" in printed_output

        # Check detailed sections
        assert "ERRORS DETECTED" in printed_output
        assert "WARNINGS DETECTED" in printed_output
        assert "SUCCESS MESSAGES" in printed_output

        # Check recommendations
        assert "❌ Critical errors detected" in printed_output

    def test_command_execution_and_analysis(self, temp_dir: Path):
        """Test command execution followed by log analysis."""
        output_file = temp_dir / "command_output.log"

        # Mock successful command execution
        with patch("scripts.development.log_analyzer.execute_and_log") as mock_execute:

            def mock_execute_side_effect(command, output_path):
                # Simulate command output
                if output_path:
                    Path(
                        output_path
                    ).write_text("""2024-01-01 10:00:00 - INFO - Command executed
2024-01-01 10:00:01 - SUCCESS - Operation completed successfully
2024-01-01 10:00:02 - INFO - Command finished
""")
                return 0

            mock_execute.side_effect = mock_execute_side_effect

            # Mock setup_logging and get_logger
            with patch("scripts.development.log_analyzer.setup_logging"):
                with patch("scripts.development.log_analyzer.get_logger"):
                    with patch(
                        "sys.argv",
                        [
                            "log_analyzer.py",
                            "--command",
                            'echo "test"',
                            "--output",
                            str(output_file),
                        ],
                    ):
                        with patch("builtins.print") as mock_print:
                            result = main()

        assert result == 0
        mock_execute.assert_called_once_with('echo "test"', str(output_file))

        # Verify analysis was performed on the output
        mock_print.assert_called()
        printed_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "LOG ANALYSIS REPORT" in printed_output
        assert "Successes:  1" in printed_output

    def test_performance_with_large_log_file(self, temp_dir: Path):
        """Test performance with a large log file."""
        log_file = temp_dir / "large.log"

        # Generate large log file (1000 lines)
        log_lines = []
        for i in range(1000):
            if i % 10 == 0:
                log_lines.append(f"2024-01-01 10:00:{i:02d} - ERROR - Error {i}")
            elif i % 5 == 0:
                log_lines.append(f"2024-01-01 10:00:{i:02d} - WARNING - Warning {i}")
            elif i % 3 == 0:
                log_lines.append(f"2024-01-01 10:00:{i:02d} - SUCCESS - Success {i}")
            else:
                log_lines.append(f"2024-01-01 10:00:{i:02d} - INFO - Info message {i}")

        log_file.write_text("\n".join(log_lines))

        # Mock setup_logging and get_logger
        with patch("scripts.development.log_analyzer.setup_logging"):
            with patch("scripts.development.log_analyzer.get_logger"):
                with patch("sys.argv", ["log_analyzer.py", "--log-file", str(log_file)]):
                    with patch("builtins.print") as mock_print:
                        # Measure execution time
                        import time

                        start_time = time.time()
                        result = main()
                        end_time = time.time()
                        execution_time = end_time - start_time

        assert result == 0

        # Should complete in reasonable time (< 2 seconds for 1000 lines)
        assert execution_time < 2.0

        # Verify analysis results
        mock_print.assert_called()
        printed_output = " ".join(str(call) for call in mock_print.call_args_list)

        # Check approximate counts (should be around 100 errors, 200 warnings, 333 successes, 567 info)
        assert "Errors:     100" in printed_output or "Errors:     101" in printed_output
        assert "Warnings:   200" in printed_output or "Warnings:   201" in printed_output
        assert "Successes:  333" in printed_output or "Successes:  334" in printed_output
