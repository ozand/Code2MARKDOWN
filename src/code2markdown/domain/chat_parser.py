"""
Chat Parser Module

This module provides functionality to parse chat files and extract structured information
to generate specification documents.
"""

import re
import zipfile
from dataclasses import dataclass


@dataclass
class ParsedDocument:
    """Represents a parsed document from chat content."""

    filename: str
    content: str
    title: str


class ChatParser:
    """Main class for parsing chat files and generating specification documents."""

    # Expected filenames that we want to extract from chat
    EXPECTED_FILENAMES = [
        "gap.md",
        "requirements.md",
        "backlog.md",
        "roadmap.md",
        "sprint-plan.md",
        "documentation-maintenance.md",
    ]

    # Mapping of title keywords to filenames for new format
    TITLE_TO_FILENAME_MAP = {
        "gap analysis": "gap.md",
        "требования": "requirements.md",
        "бэклог": "backlog.md",
        "backlog": "backlog.md",
        "дорожная карта": "roadmap.md",
        "roadmap": "roadmap.md",
        "sprint-plan": "sprint-plan.md",
        "sprint plan": "sprint-plan.md",
        "документации": "documentation-maintenance.md",
        "documentation": "documentation-maintenance.md",
    }

    def __init__(self):
        """Initialize the ChatParser."""
        pass

    def parse_chat_file(
        self, file_content: str
    ) -> tuple[list[ParsedDocument], list[str]]:
        """
        Parse a chat file and extract structured documents.

        Args:
            file_content: Content of the chat file to parse

        Returns:
            Tuple of (parsed_documents, processing_log)
        """
        log = []
        log.append("Starting chat file parsing...")

        # Pattern to match markdown code blocks and extract filename from content
        pattern = re.compile(
            r"```markdown\n" r"(.*?)\n" r"```",
            re.DOTALL | re.IGNORECASE,
        )

        # First find all markdown code blocks
        markdown_blocks = pattern.findall(file_content)
        log.append(f"Found {len(markdown_blocks)} markdown code blocks")

        if not markdown_blocks:
            log.append(
                "ERROR: No markdown code blocks found in the format ```markdown...```"
            )
            return [], log

        # Now process each block to extract filename from first line
        matches = []
        for block in markdown_blocks:
            # Extract first line to get filename
            first_line = block.split("\n", 1)[0].strip()

            # Try to extract filename from parentheses (old format)
            filename = self._extract_filename_from_parentheses(first_line)

            # If that fails, try to match title to filename (new format)
            if not filename:
                filename = self._extract_filename_from_title(first_line)

            if filename:
                matches.append((filename, block))
                log.append(f"Found document block for {filename}")
            else:
                log.append(
                    f"Skipping block: no filename found in first line '{first_line}'"
                )

        log.append(f"Found {len(matches)} documents with valid filenames")

        parsed_documents = []
        found_count = 0

        for i, match in enumerate(matches):
            log.append(f"Processing match {i+1}")

            filename, file_content_text = match
            log.append(f"Processing document: {filename}")

            if filename in self.EXPECTED_FILENAMES:
                file_content_text = file_content_text.strip()
                log.append(f"Content length: {len(file_content_text)} characters")

                # Create title from filename
                title = self._filename_to_title(filename)
                log.append(f"Generated title: {title}")

                document = ParsedDocument(
                    filename=filename, content=file_content_text, title=title
                )
                parsed_documents.append(document)
                found_count += 1
                log.append(f"Successfully parsed document: {filename}")
            else:
                log.append(f"Skipping file '{filename}' - not in expected filenames list")

        log.append(f"Completed parsing. Successfully extracted {found_count} documents.")
        return parsed_documents, log

    def _filename_to_title(self, filename: str) -> str:
        """
        Convert filename to a human-readable title.

        Args:
            filename: Name of the file

        Returns:
            Human-readable title
        """
        # Remove extension
        name_without_ext = filename.replace(".md", "")

        # Convert hyphens to spaces and capitalize words
        title = name_without_ext.replace("-", " ").title()

        return title

    def create_zip_archive(
        self, documents: list[ParsedDocument], output_path: str
    ) -> str:
        """
        Create a zip archive containing all parsed documents.

        Args:
            documents: List of parsed documents
            output_path: Path where to save the zip archive

        Returns:
            Path to the created zip file
        """
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for doc in documents:
                zipf.writestr(doc.filename, doc.content)

        return output_path

    def _extract_filename_from_parentheses(self, first_line: str) -> str | None:
        """
        Extract filename from parentheses in the first line (old format).

        Args:
            first_line: First line of the markdown block

        Returns:
            Filename if found, None otherwise
        """
        filename_match = re.search(r"\(([a-zA-Z-]+\.md)\)", first_line)
        if filename_match:
            filename = filename_match.group(1)
            if filename in self.EXPECTED_FILENAMES:
                return filename
        return None

    def _extract_filename_from_title(self, first_line: str) -> str | None:
        """
        Extract filename by matching title keywords (new format).

        Args:
            first_line: First line of the markdown block

        Returns:
            Filename if found, None otherwise
        """
        # Convert to lowercase for case-insensitive matching
        lower_first_line = first_line.lower()

        # Check each title keyword mapping
        for title_keyword, filename in self.TITLE_TO_FILENAME_MAP.items():
            if title_keyword in lower_first_line:
                return filename
        return None


def parse_chat_content(content: str) -> tuple[list[ParsedDocument], list[str]]:
    """
    Convenience function to parse chat content.

    Args:
        content: Content of the chat file to parse

    Returns:
        Tuple of (parsed_documents, processing_log)
    """
    parser = ChatParser()
    return parser.parse_chat_file(content)
