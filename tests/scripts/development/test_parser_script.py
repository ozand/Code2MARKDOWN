"""Comprehensive tests for scripts/development/parser_script.py."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scripts.development.parser_script import (
    DEFAULT_EXPECTED_FILENAMES,
    main,
    parse_documentation_blocks,
)


class TestParseDocumentationBlocks:
    """Test cases for parse_documentation_blocks function."""

    def test_parse_valid_documentation_blocks(self):
        """Test parsing valid documentation blocks."""
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

This document identifies gaps in the current implementation.
```

## Requirements (`requirements.md`)
```markdown
# Requirements

## Functional Requirements
- User authentication
- Data validation
```
"""

        expected_files = ["gap.md", "requirements.md"]
        result = parse_documentation_blocks(content, expected_files)

        assert len(result) == 2
        assert "gap.md" in result
        assert "requirements.md" in result
        assert "# Gap Analysis" in result["gap.md"]
        assert "# Requirements" in result["requirements.md"]

    def test_parse_with_title_format(self):
        """Test parsing with title format (Document Title (`filename.md`))."""
        content = """# Development Documentation

## Gap Analysis Document (`gap.md`)
```markdown
# Gap Analysis

This is the gap analysis content.
```

## Requirements Specification (`requirements.md`)
```markdown
# Requirements

This is the requirements content.
```
"""

        expected_files = ["gap.md", "requirements.md"]
        result = parse_documentation_blocks(content, expected_files)

        assert len(result) == 2
        assert "gap.md" in result
        assert "requirements.md" in result

    def test_parse_mixed_formats(self):
        """Test parsing with mixed title formats."""
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

Content from backtick format.
```

## Requirements Specification (`requirements.md`)
```markdown
# Requirements

Content from title format.
```
"""

        expected_files = ["gap.md", "requirements.md"]
        result = parse_documentation_blocks(content, expected_files)

        assert len(result) == 2
        assert "gap.md" in result
        assert "requirements.md" in result

    def test_parse_empty_content(self):
        """Test parsing blocks with empty content."""
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown

```
"""

        expected_files = ["gap.md"]
        result = parse_documentation_blocks(content, expected_files)

        # Empty content should be skipped
        assert len(result) == 0

    def test_parse_unexpected_filename(self):
        """Test parsing with unexpected filename."""
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

This is gap analysis content.
```

## Unexpected Document (`unexpected.md`)
```markdown
# Unexpected

This should be ignored.
```
"""

        expected_files = ["gap.md"]
        result = parse_documentation_blocks(content, expected_files)

        assert len(result) == 1
        assert "gap.md" in result
        assert "unexpected.md" not in result

    def test_parse_no_blocks_found(self):
        """Test parsing with no valid blocks."""
        content = """# Development Documentation

Some text without any code blocks.
"""

        expected_files = ["gap.md"]

        with pytest.raises(ValueError, match="No documentation blocks found"):
            parse_documentation_blocks(content, expected_files)

    def test_parse_no_expected_files_found(self):
        """Test parsing with no expected files found."""
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

This is gap analysis content.
```

## Unexpected Document (`unexpected.md`)
```markdown
# Unexpected

This should be ignored.
```
"""

        expected_files = ["missing.md"]

        with pytest.raises(ValueError, match="No valid documentation blocks found"):
            parse_documentation_blocks(content, expected_files)

    def test_parse_case_insensitive_markdown(self):
        """Test parsing with case-insensitive markdown blocks."""
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```MARKDOWN
# Gap Analysis

Content with uppercase MARKDOWN.
```

## Requirements (`requirements.md`)
```markdown
# Requirements

Content with lowercase markdown.
```
"""

        expected_files = ["gap.md", "requirements.md"]
        result = parse_documentation_blocks(content, expected_files)

        assert len(result) == 2
        assert "gap.md" in result
        assert "requirements.md" in result

    def test_parse_multiline_content(self):
        """Test parsing multiline content."""
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

## Section 1
Content for section 1.

## Section 2
Content for section 2.

### Subsection
More detailed content.
```
"""

        expected_files = ["gap.md"]
        result = parse_documentation_blocks(content, expected_files)

        assert len(result) == 1
        content = result["gap.md"]
        assert "# Gap Analysis" in content
        assert "## Section 1" in content
        assert "## Section 2" in content
        assert "### Subsection" in content

    def test_parse_with_code_examples(self):
        """Test parsing content that contains code examples."""
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

Here's some code:

```python
def hello():
    print("Hello, World!")
```

And more text.
```
"""

        expected_files = ["gap.md"]
        result = parse_documentation_blocks(content, expected_files)

        assert len(result) == 1
        content = result["gap.md"]
        assert "# Gap Analysis" in content
        assert "```python" in content
        assert 'print("Hello, World!")' in content

    def test_parse_with_special_characters(self):
        """Test parsing content with special characters."""
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

Special characters: !@#$%^&*()_+-=[]{}|;':",./<>?
Unicode: 你好世界 🌍 ñ é
```
"""

        expected_files = ["gap.md"]
        result = parse_documentation_blocks(content, expected_files)

        assert len(result) == 1
        content = result["gap.md"]
        assert "# Gap Analysis" in content
        assert "Special characters:" in content
        assert "Unicode:" in content

    def test_parse_multiple_blocks_same_filename(self):
        """Test parsing multiple blocks with the same filename."""
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# First Gap Analysis

This is the first block.
```

## Gap Analysis (`gap.md`)
```markdown
# Second Gap Analysis

This is the second block.
```
"""

        expected_files = ["gap.md"]
        result = parse_documentation_blocks(content, expected_files)

        # Should use the last matching block
        assert len(result) == 1
        content = result["gap.md"]
        assert "# Second Gap Analysis" in content
        assert "This is the second block." in content


class TestMainFunction:
    """Test cases for main function."""

    def test_main_success_basic(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with basic success case."""
        # Create input file
        input_file = temp_dir / "raw.md"
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

This is gap analysis content.
```
"""
        input_file.write_text(content)

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.parser_script.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.parser_script.get_logger", return_value=mock_logger
            ):
                with patch(
                    "sys.argv",
                    [
                        "parser_script.py",
                        "--input",
                        str(input_file),
                        "--output-dir",
                        str(temp_dir),
                    ],
                ):
                    result = main()

        assert result == 0

        # Check that files were created
        gap_file = temp_dir / "gap.md"
        assert gap_file.exists()
        assert "# Gap Analysis" in gap_file.read_text()

    def test_main_with_dry_run(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with dry run."""
        # Create input file
        input_file = temp_dir / "raw.md"
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

This is gap analysis content.
```
"""
        input_file.write_text(content)

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.parser_script.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.parser_script.get_logger", return_value=mock_logger
            ):
                with patch(
                    "sys.argv",
                    [
                        "parser_script.py",
                        "--input",
                        str(input_file),
                        "--output-dir",
                        str(temp_dir),
                        "--dry-run",
                    ],
                ):
                    result = main()

        assert result == 0

        # Check that files were NOT created (dry run)
        gap_file = temp_dir / "gap.md"
        assert not gap_file.exists()

    def test_main_with_custom_expected_files(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with custom expected files."""
        # Create input file
        input_file = temp_dir / "raw.md"
        content = """# Development Documentation

## Custom Doc (`custom.md`)
```markdown
# Custom Document

This is custom content.
```

## Another Doc (`another.md`)
```markdown
# Another Document

This is another content.
```
"""
        input_file.write_text(content)

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.parser_script.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.parser_script.get_logger", return_value=mock_logger
            ):
                with patch(
                    "sys.argv",
                    [
                        "parser_script.py",
                        "--input",
                        str(input_file),
                        "--output-dir",
                        str(temp_dir),
                        "--expected",
                        "custom.md",
                        "another.md",
                    ],
                ):
                    result = main()

        assert result == 0

        # Check that custom files were created
        custom_file = temp_dir / "custom.md"
        another_file = temp_dir / "another.md"
        assert custom_file.exists()
        assert another_file.exists()
        assert "# Custom Document" in custom_file.read_text()
        assert "# Another Document" in another_file.read_text()

    def test_main_input_file_not_found(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with non-existent input file."""
        input_file = temp_dir / "nonexistent.md"

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.parser_script.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.parser_script.get_logger", return_value=mock_logger
            ):
                with patch("sys.argv", ["parser_script.py", "--input", str(input_file)]):
                    with patch(
                        "scripts.development.parser_script.handle_script_error"
                    ) as mock_handle_error:
                        result = main()

        assert result == 1
        mock_handle_error.assert_called_once()

    def test_main_no_documentation_blocks(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with no documentation blocks."""
        # Create input file with no valid blocks
        input_file = temp_dir / "raw.md"
        content = """# Development Documentation

Some text without any code blocks.
"""
        input_file.write_text(content)

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.parser_script.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.parser_script.get_logger", return_value=mock_logger
            ):
                with patch("sys.argv", ["parser_script.py", "--input", str(input_file)]):
                    with patch(
                        "scripts.development.parser_script.handle_script_error"
                    ) as mock_handle_error:
                        result = main()

        assert result == 1
        mock_handle_error.assert_called_once()

    def test_main_with_verbose_logging(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with verbose logging."""
        # Create input file
        input_file = temp_dir / "raw.md"
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

This is gap analysis content.
```
"""
        input_file.write_text(content)

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.parser_script.setup_logging"
        ) as mock_setup_logging:
            with patch(
                "scripts.development.parser_script.get_logger", return_value=mock_logger
            ):
                with patch(
                    "sys.argv",
                    [
                        "parser_script.py",
                        "--input",
                        str(input_file),
                        "--output-dir",
                        str(temp_dir),
                        "--verbose",
                    ],
                ):
                    result = main()

        assert result == 0

        # Verify verbose logging was used
        mock_setup_logging.assert_called_once_with(level="DEBUG")

    def test_main_write_file_error(self, temp_dir: Path, mock_logger: Mock):
        """Test main function with file write error."""
        # Create input file
        input_file = temp_dir / "raw.md"
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

This is gap analysis content.
```
"""
        input_file.write_text(content)

        # Make output directory read-only to cause write error
        temp_dir.chmod(0o444)

        try:
            # Mock setup_logging and get_logger
            with patch(
                "scripts.development.parser_script.setup_logging"
            ) as mock_setup_logging:
                with patch(
                    "scripts.development.parser_script.get_logger",
                    return_value=mock_logger,
                ):
                    with patch(
                        "sys.argv",
                        [
                            "parser_script.py",
                            "--input",
                            str(input_file),
                            "--output-dir",
                            str(temp_dir),
                        ],
                    ):
                        result = main()

            # Should handle the error gracefully
            assert result == 0  # Script continues despite individual file errors

        finally:
            # Restore permissions for cleanup
            temp_dir.chmod(0o755)


class TestDefaultExpectedFilenames:
    """Test cases for default expected filenames."""

    def test_default_expected_filenames(self):
        """Test that default expected filenames are correctly defined."""
        expected_files = [
            "gap.md",
            "requirements.md",
            "backlog.md",
            "roadmap.md",
            "sprint-plan.md",
            "documentation-maintenance.md",
        ]

        assert DEFAULT_EXPECTED_FILENAMES == expected_files

    def test_default_filenames_are_valid(self):
        """Test that all default filenames have .md extension."""
        for filename in DEFAULT_EXPECTED_FILENAMES:
            assert filename.endswith(".md")
            assert len(filename) > 3  # At least "x.md"


class TestIntegration:
    """Integration tests for the parser script."""

    def test_end_to_end_parsing_and_file_creation(self, temp_dir: Path):
        """Test complete end-to-end parsing and file creation."""
        # Create comprehensive input file
        input_file = temp_dir / "raw.md"
        content = """# Development Documentation

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

## Current State
The project currently has basic functionality.

## Identified Gaps
1. Missing authentication
2. Incomplete error handling
3. No logging framework

## Recommendations
Implement the missing components in phases.
```

## Requirements (`requirements.md`)
```markdown
# Requirements

## Functional Requirements
- User registration and login
- Data validation and sanitization
- Error handling and logging
- File upload and processing

## Non-functional Requirements
- Performance: < 2s response time
- Security: OWASP compliance
- Scalability: Support 1000+ concurrent users
```

## Roadmap (`roadmap.md`)
```markdown
# Development Roadmap

## Phase 1: Foundation (Q1 2024)
- Set up CI/CD pipeline
- Implement basic authentication
- Create logging framework
- Set up monitoring

## Phase 2: Core Features (Q2 2024)
- Implement user management
- Add file processing capabilities
- Create admin dashboard
- Add basic analytics

## Phase 3: Advanced Features (Q3 2024)
- Implement advanced search
- Add real-time notifications
- Create mobile app
- Add machine learning features
```
"""
        input_file.write_text(content)

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.parser_script.setup_logging"
        ) as mock_setup_logging:
            with patch("scripts.development.parser_script.get_logger"):
                with patch(
                    "sys.argv",
                    [
                        "parser_script.py",
                        "--input",
                        str(input_file),
                        "--output-dir",
                        str(temp_dir),
                    ],
                ):
                    result = main()

        assert result == 0

        # Verify all files were created
        gap_file = temp_dir / "gap.md"
        requirements_file = temp_dir / "requirements.md"
        roadmap_file = temp_dir / "roadmap.md"

        assert gap_file.exists()
        assert requirements_file.exists()
        assert roadmap_file.exists()

        # Verify content
        gap_content = gap_file.read_text()
        assert "# Gap Analysis" in gap_content
        assert "## Current State" in gap_content
        assert "## Identified Gaps" in gap_content
        assert "## Recommendations" in gap_content

        requirements_content = requirements_file.read_text()
        assert "# Requirements" in requirements_content
        assert "## Functional Requirements" in requirements_content
        assert "## Non-functional Requirements" in requirements_content

        roadmap_content = roadmap_file.read_text()
        assert "# Development Roadmap" in roadmap_content
        assert "## Phase 1: Foundation" in roadmap_content
        assert "## Phase 2: Core Features" in roadmap_content
        assert "## Phase 3: Advanced Features" in roadmap_content

    def test_parser_with_real_world_content(self, temp_dir: Path):
        """Test parser with realistic content structure."""
        input_file = temp_dir / "raw.md"
        content = """# Development Documentation

This document contains comprehensive development documentation extracted from various sources.

## Gap Analysis (`gap.md`)
```markdown
# Gap Analysis

### Executive Summary
After thorough analysis of the current system, several critical gaps have been identified that need immediate attention.

### Technical Gaps
1. **Security**: No input validation or sanitization
2. **Performance**: No caching mechanism implemented
3. **Monitoring**: Lack of comprehensive logging and monitoring

### Business Gaps
1. **User Experience**: Complex onboarding process
2. **Documentation**: Outdated user guides and API documentation
3. **Support**: No automated error reporting system

### Recommendations
- Implement comprehensive security measures
- Add performance monitoring and optimization
- Create user-friendly documentation
- Establish automated testing and deployment
```

## Requirements Specification (`requirements.md`)
```markdown
# Requirements Specification

## Version 1.0
Date: January 2024

### 1. Functional Requirements

#### 1.1 User Management
- FR-001: User registration with email verification
- FR-002: Secure login with password reset functionality
- FR-003: User profile management
- FR-004: Role-based access control

#### 1.2 File Processing
- FR-005: Upload files up to 100MB
- FR-006: Support multiple file formats (PDF, DOCX, TXT)
- FR-007: Automatic file validation and error handling

### 2. Non-Functional Requirements

#### 2.1 Performance
- NFR-001: Page load time < 2 seconds
- NFR-002: API response time < 500ms
- NFR-003: Support 1000 concurrent users

#### 2.2 Security
- NFR-004: OWASP Top 10 compliance
- NFR-005: Data encryption in transit and at rest
- NFR-006: Regular security audits

### 3. System Requirements
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Docker and Kubernetes
```
"""
        input_file.write_text(content)

        # Mock setup_logging and get_logger
        with patch(
            "scripts.development.parser_script.setup_logging"
        ) as mock_setup_logging:
            with patch("scripts.development.parser_script.get_logger"):
                with patch(
                    "sys.argv",
                    [
                        "parser_script.py",
                        "--input",
                        str(input_file),
                        "--output-dir",
                        str(temp_dir),
                    ],
                ):
                    result = main()

        assert result == 0

        # Verify files were created with correct content
        gap_file = temp_dir / "gap.md"
        requirements_file = temp_dir / "requirements.md"

        assert gap_file.exists()
        assert requirements_file.exists()

        gap_content = gap_file.read_text()
        assert "### Executive Summary" in gap_content
        assert "### Technical Gaps" in gap_content
        assert "### Business Gaps" in gap_content
        assert "### Recommendations" in gap_content

        requirements_content = requirements_file.read_text()
        assert "# Requirements Specification" in requirements_content
        assert "## Version 1.0" in requirements_content
        assert "### 1. Functional Requirements" in requirements_content
        assert "### 2. Non-Functional Requirements" in requirements_content
        assert "### 3. System Requirements" in requirements_content
