#!/usr/bin/env python3
"""
Example Script with Log Analysis Integration

This script demonstrates how to integrate the mandatory log analysis protocol
into existing development scripts. It follows the patterns established in
other scripts in the repository and shows how to properly capture and analyze
logs after script execution.

Usage:
    python scripts/development/example_with_log_analysis.py --input data.txt --verbose
"""

import argparse
import logging
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
        safe_write_file,
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

    def safe_read_file(path, encoding="utf-8"):
        with open(path, encoding=encoding) as f:
            return f.read()

    def safe_write_file(
        path, content, encoding="utf-8", backup=True, backup_suffix=".backup"
    ):
        path = Path(path)
        if backup and path.exists():
            backup_path = path.with_suffix(path.suffix + backup_suffix)
            path.rename(backup_path)
        with open(path, "w", encoding=encoding) as f:
            f.write(content)

    def log_execution_summary(
        start_time, end_time, success=True, errors=None, logger=None
    ):
        if logger is None:
            logger = logging.getLogger()
        duration = end_time - start_time
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"Execution {status} - Duration: {duration}")


def process_data(input_file: str, output_file: str, logger: logging.Logger) -> bool:
    """
    Process data from input file and write to output file.

    Args:
        input_file: Path to input file
        output_file: Path to output file
        logger: Logger instance

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing data from {input_file}")

        # Read input file
        content = safe_read_file(input_file)
        logger.info(f"Read {len(content)} characters from input file")

        # Process data (simple example - convert to uppercase)
        processed_content = content.upper()
        logger.info("Data processing completed")

        # Write output file
        safe_write_file(output_file, processed_content)
        logger.info(f"Written processed data to {output_file}")

        # Simulate some warnings
        if len(content) < 10:
            logger.warning("Input file is very small, results may be limited")

        return True

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        return False
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return False


def main():
    """Main entry point for the example script."""
    start_time = datetime.now()

    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Example script demonstrating log analysis integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process data file
    python scripts/development/example_with_log_analysis.py --input data.txt --output result.txt
    
    # Process with verbose logging
    python scripts/development/example_with_log_analysis.py --input data.txt --verbose
        """,
    )

    parser.add_argument(
        "--input", "-i", type=str, required=True, help="Input file to process"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output.txt",
        help="Output file for processed data (default: output.txt)",
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
        logger.info("Example Script with Log Analysis Integration Started")
        logger.info("=" * 60)
        logger.info(f"Input file: {args.input}")
        logger.info(f"Output file: {args.output}")
        logger.info(f"Verbose: {args.verbose}")

        # Process data
        success = process_data(args.input, args.output, logger)

        if success:
            logger.info("Data processing completed successfully")
        else:
            logger.error("Data processing failed")

        logger.info("=" * 60)
        logger.info("Example Script with Log Analysis Integration Completed")
        logger.info("=" * 60)

        return 0 if success else 1

    except Exception as e:
        handle_script_error(
            e, "Script execution failed", logger=logger, exit_on_error=False
        )
        return 1

    finally:
        end_time = datetime.now()
        log_execution_summary(
            start_time,
            end_time,
            success=success if "success" in locals() else True,
            logger=logger,
        )


if __name__ == "__main__":
    sys.exit(main())
