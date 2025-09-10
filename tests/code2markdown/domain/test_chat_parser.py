"""
Tests for the chat parser module.
"""

import os
import tempfile
import zipfile

from code2markdown.domain.chat_parser import (
    ChatParser,
    ParsedDocument,
    parse_chat_content,
)


def test_filename_to_title():
    """Test the filename to title conversion."""
    parser = ChatParser()

    # Test basic conversion
    assert parser._filename_to_title("gap.md") == "Gap"
    assert parser._filename_to_title("requirements.md") == "Requirements"
    assert parser._filename_to_title("sprint-plan.md") == "Sprint Plan"
    assert (
        parser._filename_to_title("documentation-maintenance.md")
        == "Documentation Maintenance"
    )


def test_extract_filename_from_parentheses():
    """Test extracting filename from parentheses."""
    parser = ChatParser()

    # Test valid cases
    assert parser._extract_filename_from_parentheses("Some text (gap.md)") == "gap.md"
    assert (
        parser._extract_filename_from_parentheses("Another (requirements.md) here")
        == "requirements.md"
    )

    # Test invalid cases
    assert (
        parser._extract_filename_from_parentheses("Some text without parentheses") is None
    )
    assert parser._extract_filename_from_parentheses("Text (invalid.txt)") is None
    assert parser._extract_filename_from_parentheses("Text (unexpected.md)") is None


def test_extract_filename_from_title():
    """Test extracting filename from title keywords."""
    parser = ChatParser()

    # Test valid cases
    assert parser._extract_filename_from_title("# Gap Analysis: Project") == "gap.md"
    assert (
        parser._extract_filename_from_title("# Требования проекта") == "requirements.md"
    )
    assert parser._extract_filename_from_title("# Бэклог проекта") == "backlog.md"
    assert (
        parser._extract_filename_from_title("# Roadmap for the project") == "roadmap.md"
    )
    assert (
        parser._extract_filename_from_title("# Sprint Plan Details") == "sprint-plan.md"
    )
    assert (
        parser._extract_filename_from_title("# Документации maintenance")
        == "documentation-maintenance.md"
    )

    # Test invalid cases
    assert parser._extract_filename_from_title("# Unknown document type") is None


def test_parse_chat_file_with_valid_content():
    """Test parsing chat file with valid content."""
    content = """
Some text before
```markdown
# Test Gap Document (gap.md)

This is a test gap document.
```
Some text in between
```markdown
# Test Requirements Document (requirements.md)

This is a test requirements document.
```
Some text after
"""

    documents, log = parse_chat_content(content)

    # Check that we have the expected number of documents
    assert len(documents) == 2

    # Check the first document
    assert documents[0].filename == "gap.md"
    assert documents[0].title == "Gap"
    assert "# Test Gap Document" in documents[0].content

    # Check the second document
    assert documents[1].filename == "requirements.md"
    assert documents[1].title == "Requirements"
    assert "# Test Requirements Document" in documents[1].content

    # Check that we have log entries
    assert len(log) > 0
    assert "Starting chat file parsing..." in log
    assert "Found 2 documents with valid filenames" in log


def test_parse_chat_file_with_new_format():
    """Test parsing chat file with new title-based format."""
    content = """
Some text before
```Markdown
# Gap Analysis: Project Title

This is a test gap document with new format.
```
Some text in between
```Markdown
# Требования проекта (Requirements)

This is a test requirements document with new format.
```
Some text after
"""

    documents, log = parse_chat_content(content)

    # Check that we have the expected number of documents
    assert len(documents) == 2

    # Check the first document
    assert documents[0].filename == "gap.md"
    assert documents[0].title == "Gap"
    assert "# Gap Analysis: Project Title" in documents[0].content

    # Check the second document
    assert documents[1].filename == "requirements.md"
    assert documents[1].title == "Requirements"
    assert "# Требования проекта (Requirements)" in documents[1].content

    # Check that we have log entries
    assert len(log) > 0
    assert "Starting chat file parsing..." in log
    assert "Found 2 documents with valid filenames" in log


def test_parse_chat_file_with_no_matches():
    """Test parsing chat file with no valid matches."""
    content = """
This is just some text with no markdown blocks.
"""

    documents, log = parse_chat_content(content)

    # Check that we have no documents
    assert len(documents) == 0

    # Check that we have log entries including error
    assert len(log) > 0
    assert "Starting chat file parsing..." in log
    assert "ERROR: No markdown code blocks found in the format ```markdown...```" in log


def test_parse_chat_file_with_unexpected_filename():
    """Test parsing chat file with unexpected filenames."""
    content = """
`unexpected.md`
```markdown
# Unexpected Document

This document should be skipped.
```
"""

    documents, log = parse_chat_content(content)

    # Check that we have no documents (unexpected filename)
    assert len(documents) == 0

    # Check that we have log entries
    assert len(log) > 0
    assert (
        "Skipping block: no filename found in first line '# Unexpected Document'" in log
    )


def test_parse_chat_file_with_actual_export_format():
    """Test parsing chat file with actual export format from user's file."""
    content = """
Some text before
```markdown
# Gap Analysis: Frontend "AI Knowledge Hub" (Astro)

This is a test gap document with actual export format.
```
Some text in between
```markdown
# Формальные требования проекта "AI Knowledge Hub" (Frontend-фокус)

This is a test requirements document with actual export format.
```
Some text after
"""

    documents, log = parse_chat_content(content)

    # Check that we have the expected number of documents
    assert len(documents) == 2

    # Check the first document
    assert documents[0].filename == "gap.md"
    assert documents[0].title == "Gap"
    assert '# Gap Analysis: Frontend "AI Knowledge Hub" (Astro)' in documents[0].content

    # Check the second document
    assert documents[1].filename == "requirements.md"
    assert documents[1].title == "Requirements"
    assert (
        '# Формальные требования проекта "AI Knowledge Hub" (Frontend-фокус)'
        in documents[1].content
    )

    # Check that we have log entries
    assert len(log) > 0
    assert "Starting chat file parsing..." in log
    assert "Found 2 documents with valid filenames" in log


def test_create_zip_archive():
    """Test creating a zip archive from parsed documents."""
    # Create some test documents
    documents = [
        ParsedDocument(
            filename="test1.md",
            content="# Test 1\n\nThis is test document 1.",
            title="Test 1",
        ),
        ParsedDocument(
            filename="test2.md",
            content="# Test 2\n\nThis is test document 2.",
            title="Test 2",
        ),
    ]

    # Create a temporary file for the zip archive
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        zip_path = tmp_file.name

    try:
        # Create the zip archive
        parser = ChatParser()
        result_path = parser.create_zip_archive(documents, zip_path)

        # Check that the zip file was created
        assert result_path == zip_path
        assert os.path.exists(zip_path)

        # Check the contents of the zip file
        with zipfile.ZipFile(zip_path, "r") as zipf:
            # Check that both files are in the zip
            assert "test1.md" in zipf.namelist()
            assert "test2.md" in zipf.namelist()

            # Check the contents of the files
            with zipf.open("test1.md") as f:
                content1 = f.read().decode("utf-8")
                assert "# Test 1" in content1

            with zipf.open("test2.md") as f:
                content2 = f.read().decode("utf-8")
                assert "# Test 2" in content2
    finally:
        # Clean up the temporary file
        if os.path.exists(zip_path):
            os.unlink(zip_path)
