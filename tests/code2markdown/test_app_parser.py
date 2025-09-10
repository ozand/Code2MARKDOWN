"""
Tests for the chat parser UI components in app.py.
"""

import pytest


def test_chat_parser_page_exists():
    """Test that the chat parser page option exists in the navigation."""
    # This test would check that "Парсер спецификаций" is one of the options
    # in the sidebar radio button, but we can't easily test the Streamlit UI
    # components directly in a unit test.
    pass


def test_chat_parser_imports():
    """Test that the chat parser module can be imported."""
    try:
        from code2markdown.domain.chat_parser import ChatParser, parse_chat_content

        assert ChatParser is not None
        assert parse_chat_content is not None
    except ImportError:
        pytest.fail("Failed to import chat parser module")


def test_parsed_document_class():
    """Test that the ParsedDocument class can be imported and instantiated."""
    try:
        from code2markdown.domain.chat_parser import ParsedDocument

        doc = ParsedDocument(filename="test.md", content="# Test", title="Test")
        assert doc.filename == "test.md"
        assert doc.content == "# Test"
        assert doc.title == "Test"
    except ImportError:
        pytest.fail("Failed to import ParsedDocument class")
