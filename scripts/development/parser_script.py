#!/usr/bin/env python3
"""
Documentation Parser Script

This script parses raw markdown files containing documentation blocks and extracts
them into separate files. It follows the project guidelines for development scripts
with proper CLI interfaces, logging, and error handling.

Usage:
    python scripts/development/parser_script.py --input raw.md --output-dir doc/dev
    uv run python scripts/development/parser_script.py --input raw.md --verbose
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

# Import project utilities
try:
    from scripts.development.utils import (
        ensure_directory,
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


# Expected documentation filenames
DEFAULT_EXPECTED_FILENAMES = [
    "gap.md",
    "requirements.md",
    "backlog.md",
    "roadmap.md",
    "sprint-plan.md",
    "documentation-maintenance.md",
]


def parse_documentation_blocks(content: str, expected_filenames: list) -> dict:
    """
    Parse markdown documentation blocks from content.

    Args:
        content: Raw markdown content to parse
        expected_filenames: List of expected filenames to extract

    Returns:
        Dictionary mapping filenames to their content

    Raises:
        ValueError: If parsing fails or no valid blocks found
    """
    logger = get_logger(__name__)

    # Pattern to match documentation blocks with filenames
    # Matches: `filename.md` or Document Title (`filename.md`) followed by ```markdown block
    pattern = re.compile(
        r"(`([a-z-]+.md)`|([A-Z][a-zA-Z\s_`]+\(`([a-z-]+.md)`\)))"
        r".*?"
        r"```[Mm]arkdown\n"
        r"(.*?)\n"
        r"```",
        re.DOTALL,
    )

    matches = pattern.findall(content)
    logger.info(f"Found {len(matches)} potential documentation blocks")

    if not matches:
        raise ValueError("No documentation blocks found in format ```markdown...```")

    extracted_files = {}

    for i, match in enumerate(matches):
        logger.debug(f"Processing match {i+1}: {match}")

        # Extract filename from the match
        filename = next(
            (name for name in [match[1], match[3]] if name and name.endswith(".md")), None
        )

        if not filename:
            logger.warning(f"Could not extract filename from match {i+1}")
            continue

        logger.debug(f"Extracted filename: {filename}")

        # Only process expected filenames
        if filename in expected_filenames:
            file_content = match[4].strip()

            if not file_content:
                logger.warning(f"Empty content for {filename}, skipping")
                continue

            logger.info(f"Found documentation for: {filename}")
            logger.debug(f"Content preview (first 100 chars): {file_content[:100]}...")

            extracted_files[filename] = file_content
        else:
            logger.debug(f"Filename '{filename}' not in expected list, skipping")

    if not extracted_files:
        raise ValueError("No valid documentation blocks found for expected filenames")

    return extracted_files


def main():
    """Main entry point for the documentation parser script."""
    start_time = datetime.now()

    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Parse raw markdown documentation into separate files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Parse default raw.md file
    python scripts/development/parser_script.py
    
    # Parse specific file with verbose output
    python scripts/development/parser_script.py --input my_docs.md --verbose
    
    # Parse to specific output directory
    python scripts/development/parser_script.py --input raw.md --output-dir docs/
    
    # Parse with custom expected filenames
    python scripts/development/parser_script.py --input raw.md --expected gap.md roadmap.md
        """,
    )

    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="raw.md",
        help="Input markdown file to parse (default: raw.md)",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=".",
        help="Output directory for extracted files (default: current directory)",
    )

    parser.add_argument(
        "--expected",
        "-e",
        nargs="+",
        default=DEFAULT_EXPECTED_FILENAMES,
        help="Expected filenames to extract (default: standard documentation files)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Perform a dry run without creating files"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(level=log_level)
    logger = get_logger(__name__)

    try:
        logger.info("=" * 60)
        logger.info("Documentation Parser Script Started")
        logger.info("=" * 60)
        logger.info(f"Input file: {args.input}")
        logger.info(f"Output directory: {args.output_dir}")
        logger.info(f"Expected filenames: {args.expected}")
        logger.info(f"Dry run: {args.dry_run}")
        logger.info(f"Verbose: {args.verbose}")

        # Validate input file
        input_path = Path(args.input)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file '{args.input}' not found")

        # Ensure output directory exists
        output_dir = ensure_directory(args.output_dir)
        logger.info(f"Output directory ensured: {output_dir}")

        # Read input file
        logger.info(f"Reading input file: {input_path}")
        content = safe_read_file(input_path)
        logger.info(f"Successfully read {len(content)} characters")

        # Parse documentation blocks
        logger.info("Parsing documentation blocks...")
        extracted_files = parse_documentation_blocks(content, args.expected)
        logger.info(f"Found {len(extracted_files)} valid documentation blocks")

        if not extracted_files:
            logger.warning("No documentation blocks were extracted")
            return 0

        # Write extracted files
        created_count = 0
        for filename, file_content in extracted_files.items():
            output_path = output_dir / filename

            if args.dry_run:
                logger.info(f"[DRY RUN] Would create: {output_path}")
                logger.debug(f"Content length: {len(file_content)} characters")
                created_count += 1
            else:
                try:
                    safe_write_file(output_path, file_content, backup=False)
                    logger.info(f"Created file: {output_path}")
                    created_count += 1
                except Exception as e:
                    logger.error(f"Failed to create {output_path}: {e}")

        # Summary
        logger.info("=" * 60)
        logger.info("Documentation Parser Script Completed")
        logger.info("=" * 60)
        logger.info(f"Total files processed: {len(extracted_files)}")
        logger.info(f"Files created: {created_count}")
        logger.info(f"Files skipped: {len(extracted_files) - created_count}")

        if args.dry_run:
            logger.info("DRY RUN completed - no files were actually created")

        return 0

    except Exception as e:
        handle_script_error(
            e, "Documentation parser failed", logger=logger, exit_on_error=False
        )
        return 1

    finally:
        end_time = datetime.now()
        success = True  # We'll consider it successful if we get here
        log_execution_summary(start_time, end_time, success=success, logger=logger)


if __name__ == "__main__":
    sys.exit(main())
