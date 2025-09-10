#!/usr/bin/env python3
"""
Log Analysis Script

This script provides comprehensive log analysis capabilities for development scripts.
It captures and analyzes both stdout and stderr logs, summarizes key outcomes,
and provides actionable insights. Following the mandatory log analysis protocol
defined in rules.02-scripts_structure.md.

Usage:
    python scripts/development/log_analyzer.py --log-file script.log --analyze
    python scripts/development/log_analyzer.py --command "python my_script.py" --output script.log
"""

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Import project utilities
try:
    from scripts.development.utils import (
        get_logger,
        handle_script_error,
        log_execution_summary,
        safe_read_file,
        setup_logging,
    )
except ImportError:
    # Fallback for when utils is not available
    def setup_logging(level="INFO", **kwargs):
        logging.basicConfig(level=getattr(logging, level.upper()))
        return logging.getLogger()

    def get_logger(name):
        return logging.getLogger(name)

    def handle_script_error(error, context="", logger=None, exit_on_error=True):
        if logger:
            logger.error(f"{context}: {error}" if context else str(error))
        else:
            print(f"Error: {error}", file=sys.stderr)
        if exit_on_error:
            sys.exit(1)

    def log_execution_summary(
        start_time, end_time, success=True, errors=None, logger=None
    ):
        """Fallback implementation of log_execution_summary."""
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


class LogAnalyzer:
    """Comprehensive log analyzer for development scripts."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or get_logger(__name__)
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.successes: list[str] = []
        self.info_messages: list[str] = []

    def analyze_log_content(self, content: str) -> dict[str, list[str]]:
        """
        Analyze log content and categorize messages.

        Args:
            content: Log content to analyze

        Returns:
            Dictionary with categorized log messages
        """
        lines = content.splitlines()

        # Reset collections
        self.errors = []
        self.warnings = []
        self.successes = []
        self.info_messages = []

        # Common patterns for different log levels
        error_indicators = [
            "error",
            "exception",
            "traceback",
            "failed",
            "failure",
            "critical",
            "fatal",
            "err:",
            "error:",
        ]

        warning_indicators = ["warning", "warn:", "caution", "deprecated", "obsolete"]

        success_indicators = [
            "success",
            "completed",
            "finished",
            "done",
            "passed",
            "ok:",
            "success:",
        ]

        for line in lines:
            line_lower = line.lower().strip()

            # Skip empty lines
            if not line_lower:
                continue

            # Check for errors
            if any(indicator in line_lower for indicator in error_indicators):
                self.errors.append(line)
            # Check for warnings
            elif any(indicator in line_lower for indicator in warning_indicators):
                self.warnings.append(line)
            # Check for successes
            elif any(indicator in line_lower for indicator in success_indicators):
                self.successes.append(line)
            # Everything else is info
            else:
                self.info_messages.append(line)

        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "successes": self.successes,
            "info": self.info_messages,
        }

    def generate_report(self) -> str:
        """
        Generate a comprehensive analysis report.

        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("LOG ANALYSIS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(
            f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")

        # Summary
        report_lines.append("SUMMARY")
        report_lines.append("-" * 20)
        report_lines.append(f"Errors:     {len(self.errors)}")
        report_lines.append(f"Warnings:   {len(self.warnings)}")
        report_lines.append(f"Successes:  {len(self.successes)}")
        report_lines.append(f"Info:       {len(self.info_messages)}")
        report_lines.append("")

        # Detailed sections
        if self.errors:
            report_lines.append("ERRORS DETECTED")
            report_lines.append("-" * 20)
            for i, error in enumerate(self.errors, 1):
                report_lines.append(f"{i}. {error}")
            report_lines.append("")

        if self.warnings:
            report_lines.append("WARNINGS DETECTED")
            report_lines.append("-" * 20)
            for i, warning in enumerate(self.warnings, 1):
                report_lines.append(f"{i}. {warning}")
            report_lines.append("")

        if self.successes:
            report_lines.append("SUCCESS MESSAGES")
            report_lines.append("-" * 20)
            for i, success in enumerate(self.successes, 1):
                report_lines.append(f"{i}. {success}")
            report_lines.append("")

        # Recommendations
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 20)
        if self.errors:
            report_lines.append(
                "❌ Critical errors detected. Please address these issues before proceeding."
            )
        elif self.warnings:
            report_lines.append(
                "⚠️  Warnings detected. Please review and address if necessary."
            )
        else:
            report_lines.append(
                "✅ No critical issues detected. Script execution appears successful."
            )

        report_lines.append("=" * 60)

        return "\n".join(report_lines)

    def should_ask_next_steps(self) -> bool:
        """
        Determine if user should be prompted for next steps based on log analysis.

        Returns:
            True if user input is needed, False otherwise
        """
        return bool(self.errors or self.warnings)


def execute_and_log(command: str, log_file: str | None = None) -> int:
    """
    Execute a command and log its output.

    Args:
        command: Command to execute
        log_file: Optional file to log output to

    Returns:
        Exit code of the command
    """
    logger = get_logger(__name__)

    try:
        # Execute command
        logger.info(f"Executing command: {command}")

        # Open log file if specified
        log_fh = None
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_fh = open(log_path, "w", encoding="utf-8")
            logger.info(f"Logging output to: {log_path}")

        # Run the command
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Capture and log output in real-time
        output_lines = []
        for line in process.stdout:
            line = line.rstrip()
            logger.info(line)
            output_lines.append(line)

            # Also write to file if specified
            if log_fh:
                log_fh.write(line + "\n")
                log_fh.flush()

        # Wait for process to complete
        process.wait()

        # Close log file if opened
        if log_fh:
            log_fh.close()

        # Log execution summary
        logger.info(f"Command completed with exit code: {process.returncode}")
        return process.returncode

    except Exception as e:
        handle_script_error(e, "Failed to execute command", logger=logger)
        return 1


def main():
    """Main entry point for the log analyzer script."""
    start_time = datetime.now()

    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Analyze logs from development script executions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Analyze an existing log file
    python scripts/development/log_analyzer.py --log-file script.log
    
    # Execute a command and analyze its output
    python scripts/development/log_analyzer.py --command "python my_script.py"
    
    # Execute a command, save output to file, and analyze
    python scripts/development/log_analyzer.py --command "python my_script.py" --output script.log
        """,
    )

    parser.add_argument("--log-file", "-l", type=str, help="Path to log file to analyze")

    parser.add_argument(
        "--command", "-c", type=str, help="Command to execute and analyze"
    )

    parser.add_argument(
        "--output", "-o", type=str, help="Output file for command execution logs"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)
    logger = get_logger(__name__)

    try:
        logger.info("=" * 60)
        logger.info("Log Analysis Script Started")
        logger.info("=" * 60)

        # Validate arguments
        if not args.log_file and not args.command:
            logger.error("Either --log-file or --command must be specified")
            return 1

        if args.log_file and args.command:
            logger.warning(
                "Both --log-file and --command specified. Analyzing log file after command execution."
            )

        # Execute command if specified
        if args.command:
            exit_code = execute_and_log(args.command, args.output)
            if exit_code != 0:
                logger.warning(f"Command exited with non-zero code: {exit_code}")

        # Analyze log file if specified
        if args.log_file:
            log_path = Path(args.log_file)
            if not log_path.exists():
                logger.error(f"Log file not found: {log_path}")
                return 1

            logger.info(f"Analyzing log file: {log_path}")
            content = safe_read_file(log_path)

            # Analyze the content
            analyzer = LogAnalyzer(logger)
            analyzer.analyze_log_content(content)

            # Generate and print report
            report = analyzer.generate_report()
            print(report)

            # Ask for next steps if needed
            if analyzer.should_ask_next_steps():
                logger.info(
                    "Issues detected in log analysis. Consider reviewing and addressing them."
                )

        logger.info("=" * 60)
        logger.info("Log Analysis Script Completed")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        handle_script_error(e, "Log analysis failed", logger=logger, exit_on_error=False)
        return 1

    finally:
        end_time = datetime.now()
        success = True  # We'll consider it successful if we get here
        log_execution_summary(start_time, end_time, success=success, logger=logger)


if __name__ == "__main__":
    sys.exit(main())
