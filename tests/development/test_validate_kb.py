"""Comprehensive tests for scripts/development/validate_kb.py."""

from pathlib import Path
from unittest.mock import patch

from scripts.development.validate_kb import KBValidator, main


class TestKBValidator:
    """Test cases for KBValidator class."""

    def test_validator_initialization(self, temp_dir: Path):
        """Test validator initialization."""
        validator = KBValidator(temp_dir)

        assert validator.base_path == temp_dir.resolve()
        assert isinstance(validator.errors, list)
        assert isinstance(validator.warnings, list)
        assert len(validator.errors) == 0
        assert len(validator.warnings) == 0

    def test_load_gitignore_success(self, temp_dir: Path):
        """Test successful gitignore loading."""
        gitignore_content = """# Comment
*.pyc
__pycache__/
node_modules/
.env
"""
        gitignore_file = temp_dir / ".gitignore"
        gitignore_file.write_text(gitignore_content)

        validator = KBValidator(temp_dir)
        patterns = validator._load_gitignore()

        assert len(patterns) == 4
        assert "*.pyc" in patterns
        assert "__pycache__/" in patterns
        assert "node_modules/" in patterns
        assert ".env" in patterns

    def test_load_gitignore_not_found(self, temp_dir: Path):
        """Test gitignore loading when file doesn't exist."""
        validator = KBValidator(temp_dir)
        patterns = validator._load_gitignore()

        assert len(patterns) == 0

    def test_load_gitignore_with_errors(self, temp_dir: Path):
        """Test gitignore loading with read errors."""
        gitignore_file = temp_dir / ".gitignore"
        gitignore_file.write_text("content")
        gitignore_file.chmod(0o000)  # Make unreadable

        try:
            validator = KBValidator(temp_dir)
            patterns = validator._load_gitignore()

            assert len(patterns) == 0
            assert len(validator.warnings) == 1
            assert "Не удалось прочитать .gitignore" in validator.warnings[0]
        finally:
            gitignore_file.chmod(0o644)  # Restore permissions

    def test_is_ignored_with_patterns(self, temp_dir: Path):
        """Test file ignoring with gitignore patterns."""
        gitignore_file = temp_dir / ".gitignore"
        gitignore_file.write_text("*.pyc\n__pycache__/\n")

        validator = KBValidator(temp_dir)
        validator.gitignore_patterns = ["*.pyc", "__pycache__/"]

        # Test ignored files
        assert validator._is_ignored(temp_dir / "test.pyc") is True
        assert validator._is_ignored(temp_dir / "__pycache__" / "file.py") is True

        # Test non-ignored files
        assert validator._is_ignored(temp_dir / "test.py") is False
        assert validator._is_ignored(temp_dir / "README.md") is False

    def test_remove_code_blocks_basic(self, temp_dir: Path):
        """Test code block removal from markdown content."""
        validator = KBValidator(temp_dir)

        content = """# Document

Some text before code.

```python
def hello():
    print("Hello, World!")
```

More text after code.

`inline code` here.

Final text.
"""

        result = validator._remove_code_blocks(content)

        assert "```python" not in result
        assert "def hello():" not in result
        assert "`inline code`" not in result
        assert "# Document" in result
        assert "Some text before code." in result
        assert "More text after code." in result
        assert "Final text." in result

    def test_remove_code_blocks_fenced_only(self, temp_dir: Path):
        """Test removal of only fenced code blocks."""
        validator = KBValidator(temp_dir)

        content = """# Document

```python
code here
```

Regular text with `inline code` should remain.

```javascript
more code
```
"""

        result = validator._remove_code_blocks(content)

        assert "```python" not in result
        assert "```javascript" not in result
        assert "code here" not in result
        assert "more code" not in result
        assert "Regular text with `inline code` should remain." in result

    def test_find_markdown_files_basic(self, temp_dir: Path):
        """Test finding markdown files in knowledge base directories."""
        # Create test structure
        (temp_dir / "pages").mkdir()
        (temp_dir / "journals").mkdir()
        (temp_dir / ".roo" / "rules").mkdir(parents=True)

        # Create test files
        (temp_dir / "pages" / "story1.md").write_text("content")
        (temp_dir / "pages" / "story2.md").write_text("content")
        (temp_dir / "journals" / "2024_01_01.md").write_text("content")
        (temp_dir / ".roo" / "rules" / "rule1.md").write_text("content")

        validator = KBValidator(temp_dir)
        files = validator._find_markdown_files()

        assert len(files) == 4
        file_names = {f.name for f in files}
        assert "story1.md" in file_names
        assert "story2.md" in file_names
        assert "2024_01_01.md" in file_names
        assert "rule1.md" in file_names

    def test_find_markdown_files_missing_directories(self, temp_dir: Path):
        """Test finding markdown files when directories are missing."""
        validator = KBValidator(temp_dir)
        files = validator._find_markdown_files()

        # Should find no files but not crash
        assert len(files) == 0
        assert len(validator.warnings) == 2  # warnings for missing directories

    def test_get_all_page_names(self, temp_dir: Path):
        """Test getting all page names from markdown files."""
        validator = KBValidator(temp_dir)

        files = [
            temp_dir / "pages" / "STORY-API-1.md",
            temp_dir / "pages" / "REQ-DEV-1.md",
            temp_dir / "journals" / "2024_01_01.md",
        ]

        # Create files
        for file in files:
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("content")

        page_names = validator._get_all_page_names(files)

        expected_names = {"STORY-API-1", "REQ-DEV-1", "2024_01_01"}
        assert page_names == expected_names

    def test_validate_link_integrity_valid_links(self, temp_dir: Path):
        """Test link integrity validation with valid links."""
        # Create test files
        (temp_dir / "pages").mkdir()
        (temp_dir / "pages" / "existing-page.md").write_text("content")
        (temp_dir / "pages" / "another-page.md").write_text("content")

        # Create file with valid links
        test_file = temp_dir / "pages" / "test.md"
        test_file.write_text("""# Test Document

This document contains valid links: [[existing-page]], [[another-page]].

Some code:
```python
# This should not be checked: [[non-existent]]
```

Inline code: `[[also-not-checked]]`
""")

        validator = KBValidator(temp_dir)
        all_pages = {"existing-page", "another-page", "test"}

        validator.validate_link_integrity(test_file, all_pages)

        # Should have no errors
        assert len(validator.errors) == 0

    def test_validate_link_integrity_broken_links(self, temp_dir: Path):
        """Test link integrity validation with broken links."""
        # Create test files
        (temp_dir / "pages").mkdir()
        (temp_dir / "pages" / "existing-page.md").write_text("content")

        # Create file with broken links
        test_file = temp_dir / "pages" / "test.md"
        test_file.write_text("""# Test Document

This document contains broken links: [[existing-page]], [[broken-link]], [[missing-page]].
""")

        validator = KBValidator(temp_dir)
        all_pages = {"existing-page", "test"}

        validator.validate_link_integrity(test_file, all_pages)

        # Should have errors for broken links
        assert len(validator.errors) == 2
        error_messages = " ".join(validator.errors)
        assert "broken-link" in error_messages
        assert "missing-page" in error_messages

    def test_validate_link_integrity_ignored_links(self, temp_dir: Path):
        """Test that ignored links are not validated."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "test.md"
        test_file.write_text("""# Test Document

Links that should be ignored: [[TODO]], [[DOING]], [[DONE]], [[high]], [[medium]], [[low]].
""")

        validator = KBValidator(temp_dir)
        all_pages = {"test"}

        validator.validate_link_integrity(test_file, all_pages)

        # Should have no errors for ignored links
        assert len(validator.errors) == 0

    def test_validate_link_integrity_file_links_ignored(self, temp_dir: Path):
        """Test that file links are ignored in link integrity check."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "test.md"
        test_file.write_text("""# Test Document

File links should be ignored: [[path/to/file.py]], [[scripts/utils.py|`utils.py`]].
""")

        validator = KBValidator(temp_dir)
        all_pages = {"test"}

        validator.validate_link_integrity(test_file, all_pages)

        # Should have no errors for file links
        assert len(validator.errors) == 0

    def test_validate_correct_link_formatting_valid(self, temp_dir: Path):
        """Test correct link formatting validation with valid links."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "test.md"
        test_file.write_text("""# Test Document

Valid file links: [[scripts/development/utils.py|`utils.py`]], [[src/main.py|`main.py`]].
""")

        # Create referenced files
        (temp_dir / "scripts" / "development").mkdir(parents=True)
        (temp_dir / "src").mkdir()
        (temp_dir / "scripts" / "development" / "utils.py").write_text("content")
        (temp_dir / "src" / "main.py").write_text("content")

        validator = KBValidator(temp_dir)

        validator.validate_correct_link_formatting(test_file)

        # Should have no errors
        assert len(validator.errors) == 0

    def test_validate_correct_link_formatting_invalid_alias(self, temp_dir: Path):
        """Test correct link formatting validation with invalid aliases."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "test.md"
        test_file.write_text("""# Test Document

Invalid alias: [[scripts/development/utils.py|`wrongname.py`]].
""")

        # Create referenced file
        (temp_dir / "scripts" / "development").mkdir(parents=True)
        (temp_dir / "scripts" / "development" / "utils.py").write_text("content")

        validator = KBValidator(temp_dir)

        validator.validate_correct_link_formatting(test_file)

        # Should have error for incorrect alias
        assert len(validator.errors) == 1
        assert "Incorrect alias format" in validator.errors[0]
        assert (
            "should be [[scripts/development/utils.py|`utils.py`]]" in validator.errors[0]
        )

    def test_validate_correct_link_formatting_nonexistent_file(self, temp_dir: Path):
        """Test correct link formatting validation with non-existent files."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "test.md"
        test_file.write_text("""# Test Document

Link to non-existent file: [[nonexistent/file.py|`file.py`]].
""")

        validator = KBValidator(temp_dir)

        validator.validate_correct_link_formatting(test_file)

        # Should have error for non-existent file
        assert len(validator.errors) == 1
        assert "Link to non-existent file" in validator.errors[0]

    def test_validate_file_structure_user_story(self, temp_dir: Path):
        """Test file structure validation for user stories."""
        (temp_dir / "pages").mkdir()

        # Valid user story filename
        valid_file = temp_dir / "pages" / "STORY-API-1.md"
        valid_file.write_text("content")

        # Invalid user story filename
        invalid_file = temp_dir / "pages" / "STORY-INVALID.md"
        invalid_file.write_text("content")

        validator = KBValidator(temp_dir)

        validator.validate_file_structure(valid_file)
        validator.validate_file_structure(invalid_file)

        # Should have error for invalid filename
        assert len(validator.errors) == 1
        assert "Неправильное имя файла User Story" in validator.errors[0]

    def test_validate_file_structure_requirement(self, temp_dir: Path):
        """Test file structure validation for requirements."""
        (temp_dir / "pages").mkdir()

        # Valid requirement filename
        valid_file = temp_dir / "pages" / "REQ-DEV-1.md"
        valid_file.write_text("content")

        # Invalid requirement filename
        invalid_file = temp_dir / "pages" / "REQ-INVALID.md"
        invalid_file.write_text("content")

        validator = KBValidator(temp_dir)

        validator.validate_file_structure(valid_file)
        validator.validate_file_structure(invalid_file)

        # Should have error for invalid filename
        assert len(validator.errors) == 1
        assert "Неправильное имя файла Requirement" in validator.errors[0]

    def test_validate_file_structure_rules(self, temp_dir: Path):
        """Test file structure validation for rules."""
        (temp_dir / ".roo" / "rules").mkdir(parents=True)

        # Valid rule file (directly in rules directory)
        valid_file = temp_dir / ".roo" / "rules" / "quality-guideline.md"
        valid_file.write_text("content")

        # Invalid rule file (in subdirectory)
        (temp_dir / ".roo" / "rules" / "subdir").mkdir()
        invalid_file = temp_dir / ".roo" / "rules" / "subdir" / "rule.md"
        invalid_file.write_text("content")

        validator = KBValidator(temp_dir)

        validator.validate_file_structure(valid_file)
        validator.validate_file_structure(invalid_file)

        # Should have error for rule in subdirectory
        assert len(validator.errors) == 1
        assert (
            "Файл правила должен находиться непосредственно в .roo/rules/"
            in validator.errors[0]
        )

    def test_validate_properties_schema_user_story_complete(self, temp_dir: Path):
        """Test properties schema validation for complete user story."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "STORY-API-1.md"
        test_file.write_text("""---
type:: [[story]]
status:: [[TODO]]
priority:: [[high]]
assignee:: [[@developer]]
epic:: [[EPIC-DEV]]
related-reqs:: [[REQ-DEV-1]]
---

# User Story

Complete user story with all properties.
""")

        validator = KBValidator(temp_dir)

        validator.validate_properties_schema(test_file)

        # Should have no errors
        assert len(validator.errors) == 0

    def test_validate_properties_schema_user_story_missing_properties(
        self, temp_dir: Path
    ):
        """Test properties schema validation for user story with missing properties."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "STORY-API-1.md"
        test_file.write_text("""---
type:: [[story]]
status:: [[TODO]]
# Missing priority, assignee, epic, related-reqs
---

# User Story

Incomplete user story missing required properties.
""")

        validator = KBValidator(temp_dir)

        validator.validate_properties_schema(test_file)

        # Should have errors for missing properties
        assert len(validator.errors) == 1
        assert "отсутствуют обязательные свойства" in validator.errors[0]
        assert "priority::" in validator.errors[0]
        assert "assignee::" in validator.errors[0]
        assert "epic::" in validator.errors[0]
        assert "related-reqs::" in validator.errors[0]

    def test_validate_properties_schema_requirement_complete(self, temp_dir: Path):
        """Test properties schema validation for complete requirement."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "REQ-DEV-1.md"
        test_file.write_text("""---
type:: [[requirement]]
status:: [[PLANNED]]
---

# Requirement

Complete requirement with all properties.
""")

        validator = KBValidator(temp_dir)

        validator.validate_properties_schema(test_file)

        # Should have no errors
        assert len(validator.errors) == 0

    def test_validate_properties_schema_requirement_missing_properties(
        self, temp_dir: Path
    ):
        """Test properties schema validation for requirement with missing properties."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "REQ-DEV-1.md"
        test_file.write_text("""---
type:: [[requirement]]
# Missing status
---

# Requirement

Incomplete requirement missing required properties.
""")

        validator = KBValidator(temp_dir)

        validator.validate_properties_schema(test_file)

        # Should have errors for missing properties
        assert len(validator.errors) == 1
        assert "отсутствуют обязательные свойства" in validator.errors[0]
        assert "status::" in validator.errors[0]

    def test_validate_status_correctness_user_story_valid(self, temp_dir: Path):
        """Test status correctness validation for user story with valid status."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "STORY-API-1.md"
        test_file.write_text("""---
type:: [[story]]
status:: [[TODO]]
---

# User Story

User story with valid status.
""")

        validator = KBValidator(temp_dir)

        validator.validate_status_correctness(test_file)

        # Should have no errors
        assert len(validator.errors) == 0

    def test_validate_status_correctness_user_story_invalid(self, temp_dir: Path):
        """Test status correctness validation for user story with invalid status."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "STORY-API-1.md"
        test_file.write_text("""---
type:: [[story]]
status:: [[INVALID]]
---

# User Story

User story with invalid status.
""")

        validator = KBValidator(temp_dir)

        validator.validate_status_correctness(test_file)

        # Should have error for invalid status
        assert len(validator.errors) == 1
        assert "имеет недопустимый статус" in validator.errors[0]
        assert "[[INVALID]]" in validator.errors[0]
        assert "[[TODO]], [[DOING]], [[DONE]]" in validator.errors[0]

    def test_validate_status_correctness_requirement_valid(self, temp_dir: Path):
        """Test status correctness validation for requirement with valid status."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "REQ-DEV-1.md"
        test_file.write_text("""---
type:: [[requirement]]
status:: [[PLANNED]]
---

# Requirement

Requirement with valid status.
""")

        validator = KBValidator(temp_dir)

        validator.validate_status_correctness(test_file)

        # Should have no errors
        assert len(validator.errors) == 0

    def test_validate_status_correctness_requirement_invalid(self, temp_dir: Path):
        """Test status correctness validation for requirement with invalid status."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "REQ-DEV-1.md"
        test_file.write_text("""---
type:: [[requirement]]
status:: [[INVALID]]
---

# Requirement

Requirement with invalid status.
""")

        validator = KBValidator(temp_dir)

        validator.validate_status_correctness(test_file)

        # Should have error for invalid status
        assert len(validator.errors) == 1
        assert "имеет недопустимый статус" in validator.errors[0]
        assert "[[INVALID]]" in validator.errors[0]
        assert "[[PLANNED]], [[IMPLEMENTED]], [[PARTIAL]]" in validator.errors[0]

    def test_validate_readme_title_with_title(self, temp_dir: Path):
        """Test README title validation with title property."""
        test_file = temp_dir / "README.md"
        test_file.write_text("""---
title:: Project README
---

# Project README

README with title property.
""")

        validator = KBValidator(temp_dir)

        validator.validate_readme_title(test_file)

        # Should have no errors
        assert len(validator.errors) == 0

    def test_validate_readme_title_without_title(self, temp_dir: Path):
        """Test README title validation without title property."""
        test_file = temp_dir / "README.md"
        test_file.write_text("""# Project README

README without title property.
""")

        validator = KBValidator(temp_dir)

        validator.validate_readme_title(test_file)

        # Should have error for missing title
        assert len(validator.errors) == 1
        assert "не имеет свойства 'title::'" in validator.errors[0]

    def test_validate_temporary_artifacts_valid(self, temp_dir: Path):
        """Test temporary artifacts validation with valid files."""
        (temp_dir / "pages").mkdir()
        test_file = temp_dir / "pages" / "normal.md"
        test_file.write_text("content")

        validator = KBValidator(temp_dir)

        validator.validate_temporary_artifacts(test_file)

        # Should have no errors
        assert len(validator.errors) == 0

    def test_validate_temporary_artifacts_invalid(self, temp_dir: Path):
        """Test temporary artifacts validation with invalid files."""
        (temp_dir / "pages").mkdir()

        # Test raw.md
        raw_file = temp_dir / "pages" / "raw.md"
        raw_file.write_text("raw command output")

        # Test error.errors
        error_file = temp_dir / "pages" / "error.errors"
        error_file.write_text("error output")

        validator = KBValidator(temp_dir)

        validator.validate_temporary_artifacts(raw_file)
        validator.validate_temporary_artifacts(error_file)

        # Should have errors for temporary artifacts
        assert len(validator.errors) == 2
        assert any("raw.md" in error for error in validator.errors)
        assert any("error.errors" in error for error in validator.errors)
        assert all("является временным артефактом" in error for error in validator.errors)

    def test_validate_misplaced_files_valid(self, temp_dir: Path):
        """Test misplaced files validation with valid file locations."""
        # Create valid structure
        (temp_dir / "pages").mkdir()
        (temp_dir / "journals").mkdir()
        (temp_dir / ".roo" / "rules").mkdir(parents=True)

        # Create valid files
        (temp_dir / "pages" / "story.md").write_text("content")
        (temp_dir / "journals" / "2024_01_01.md").write_text("content")
        (temp_dir / ".roo" / "rules" / "rule.md").write_text("content")
        (temp_dir / "README.md").write_text("content")

        validator = KBValidator(temp_dir)

        validator.validate_misplaced_files()

        # Should have no errors
        assert len(validator.errors) == 0

    def test_validate_misplaced_files_invalid(self, temp_dir: Path):
        """Test misplaced files validation with invalid file locations."""
        # Create invalid file outside allowed directories
        invalid_file = temp_dir / "invalid.md"
        invalid_file.write_text("content")

        validator = KBValidator(temp_dir)

        validator.validate_misplaced_files()

        # Should have error for misplaced file
        assert len(validator.errors) == 1
        assert "находится вне разрешенных директорий" in validator.errors[0]
        assert "invalid.md" in validator.errors[0]

    def test_run_validation_complete_success(self, temp_dir: Path):
        """Test complete validation run with all checks passing."""
        # Create complete valid structure
        (temp_dir / "pages").mkdir()
        (temp_dir / "journals").mkdir()
        (temp_dir / ".roo" / "rules").mkdir(parents=True)

        # Create valid files
        story_file = temp_dir / "pages" / "STORY-API-1.md"
        story_file.write_text("""---
type:: [[story]]
status:: [[TODO]]
priority:: [[high]]
assignee:: [[@developer]]
epic:: [[EPIC-DEV]]
related-reqs:: [[REQ-DEV-1]]
---

# User Story

Valid user story with all properties.
""")

        req_file = temp_dir / "pages" / "REQ-DEV-1.md"
        req_file.write_text("""---
type:: [[requirement]]
status:: [[PLANNED]]
---

# Requirement

Valid requirement with all properties.
""")

        journal_file = temp_dir / "journals" / "2024_01_01.md"
        journal_file.write_text("""# Journal Entry

Valid journal entry.
""")

        rule_file = temp_dir / ".roo" / "rules" / "quality-guideline.md"
        rule_file.write_text("""# Quality Guidelines

Valid rule file.
""")

        readme_file = temp_dir / "README.md"
        readme_file.write_text("""---
title:: Project README
---

# Project README

Valid README with title.
""")

        validator = KBValidator(temp_dir)

        # Mock print to avoid output during testing
        with patch("builtins.print"):
            validator.run_validation()

        # Should have no errors
        assert len(validator.errors) == 0

    def test_run_validation_with_errors(self, temp_dir: Path):
        """Test complete validation run with various errors."""
        # Create structure with errors
        (temp_dir / "pages").mkdir()

        # Create file with broken link
        broken_link_file = temp_dir / "pages" / "broken-links.md"
        broken_link_file.write_text("""# Document with Broken Links

This has broken links: [[non-existent-page]], [[another-missing-page]].
""")

        # Create file with invalid alias
        invalid_alias_file = temp_dir / "pages" / "invalid-alias.md"
        invalid_alias_file.write_text("""# Document with Invalid Alias

Invalid alias: [[scripts/development/utils.py|`wrongname.py]].
""")

        # Create misplaced file
        misplaced_file = temp_dir / "misplaced.md"
        misplaced_file.write_text("content")

        validator = KBValidator(temp_dir)

        # Mock print to avoid output during testing
        with patch("builtins.print"):
            validator.run_validation()

        # Should have errors
        assert len(validator.errors) > 0

        error_messages = " ".join(validator.errors)
        assert "Broken link" in error_messages
        assert "Incorrect alias format" in error_messages
        assert "находится вне разрешенных директорий" in error_messages

    def test_print_report_no_issues(self, temp_dir: Path):
        """Test report printing when there are no issues."""
        validator = KBValidator(temp_dir)

        # Mock print to capture output
        with patch("builtins.print") as mock_print:
            validator.print_report()

        # Should print success message
        mock_print.assert_any_call(
            "\n✅ Все проверки успешно пройдены! Ошибок не найдено."
        )

    def test_print_report_with_warnings(self, temp_dir: Path):
        """Test report printing with warnings."""
        validator = KBValidator(temp_dir)
        validator.warnings = ["Warning 1", "Warning 2"]

        # Mock print to capture output
        with patch("builtins.print") as mock_print:
            validator.print_report()

        # Should print warnings
        mock_print.assert_any_call("\n⚠️  Найдено предупреждений: 2")
        mock_print.assert_any_call("  - Warning 1")
        mock_print.assert_any_call("  - Warning 2")

    def test_print_report_with_errors(self, temp_dir: Path):
        """Test report printing with errors."""
        validator = KBValidator(temp_dir)
        validator.errors = ["Error 1", "Error 2"]

        # Mock print to capture output
        with patch("builtins.print") as mock_print:
            validator.print_report()

        # Should print errors
        mock_print.assert_any_call("\n❌ Найдено ошибок: 2")
        mock_print.assert_any_call("  - Error 1")
        mock_print.assert_any_call("  - Error 2")


class TestMainFunction:
    """Test cases for main function."""

    def test_main_success(self, temp_dir: Path):
        """Test main function with successful validation."""
        # Create valid structure
        (temp_dir / "pages").mkdir()
        (temp_dir / "pages" / "STORY-API-1.md").write_text("""---
type:: [[story]]
status:: [[TODO]]
priority:: [[high]]
assignee:: [[@developer]]
epic:: [[EPIC-DEV]]
related-reqs:: [[REQ-DEV-1]]
---

# User Story

Valid user story.
""")

        with patch("sys.argv", ["validate_kb.py", "--project-root", str(temp_dir)]):
            result = main()

        # Should exit successfully
        assert result == 0

    def test_main_with_errors(self, temp_dir: Path):
        """Test main function with validation errors."""
        # Create structure with errors
        (temp_dir / "pages").mkdir()
        (temp_dir / "pages" / "test.md").write_text("""# Document

Broken link: [[non-existent-page]].
""")

        with patch("sys.argv", ["validate_kb.py", "--project-root", str(temp_dir)]):
            result = main()

        # Should exit with error code
        assert result == 1

    def test_main_with_custom_project_root(self, temp_dir: Path):
        """Test main function with custom project root."""
        # Create valid structure
        (temp_dir / "pages").mkdir()
        (temp_dir / "pages" / "valid.md").write_text("content")

        with patch("sys.argv", ["validate_kb.py", "--project-root", str(temp_dir)]):
            result = main()

        # Should exit successfully
        assert result == 0


class TestIntegration:
    """Integration tests for the validator."""

    def test_complete_validation_workflow(self, temp_dir: Path):
        """Test complete validation workflow with various scenarios."""
        # Create comprehensive test structure
        (temp_dir / "pages").mkdir()
        (temp_dir / "journals").mkdir()
        (temp_dir / ".roo" / "rules").mkdir(parents=True)

        # Valid files
        (temp_dir / "pages" / "STORY-API-1.md").write_text("""---
type:: [[story]]
status:: [[TODO]]
priority:: [[high]]
assignee:: [[@developer]]
epic:: [[EPIC-DEV]]
related-reqs:: [[REQ-DEV-1]]
---

# Valid User Story

This story links to [[REQ-DEV-1]] and [[STORY-API-2]].
""")

        (temp_dir / "pages" / "STORY-API-2.md").write_text("""---
type:: [[story]]
status:: [[DOING]]
priority:: [[medium]]
assignee:: [[@developer]]
epic:: [[EPIC-DEV]]
related-reqs:: 
---

# Another Valid Story

This story is referenced by the first one.
""")

        (temp_dir / "pages" / "REQ-DEV-1.md").write_text("""---
type:: [[requirement]]
status:: [[PLANNED]]
---

# Valid Requirement

This requirement is linked from the user story.
""")

        (temp_dir / "journals" / "2024_01_01.md").write_text("""# Daily Journal

Today's work log.
""")

        (
            temp_dir / ".roo" / "rules" / "quality-guideline.md"
        ).write_text("""# Quality Guidelines

Project quality guidelines.
""")

        (temp_dir / "README.md").write_text("""---
title:: Project README
---

# Project README

Main project documentation.
""")

        # Invalid files
        (
            temp_dir / "pages" / "broken-links.md"
        ).write_text("""# Document with Broken Links

This has broken links: [[non-existent-story]], [[missing-requirement]].
""")

        (
            temp_dir / "pages" / "invalid-alias.md"
        ).write_text("""# Document with Invalid Alias

Invalid alias: [[scripts/development/utils.py|`wrongname.py]].
""")

        (temp_dir / "pages" / "incomplete-story.md").write_text("""---
type:: [[story]]
status:: [[TODO]]
# Missing other required properties
---

# Incomplete User Story

This story is missing required properties.
""")

        (temp_dir / "pages" / "raw.md").write_text("""# Raw Command Output

This is a temporary artifact that should not be here.
""")

        # Create referenced file for invalid alias test
        (temp_dir / "scripts" / "development").mkdir(parents=True)
        (temp_dir / "scripts" / "development" / "utils.py").write_text("content")

        validator = KBValidator(temp_dir)

        # Run complete validation
        with patch("builtins.print"):
            validator.run_validation()

        # Verify various types of errors were found
        error_messages = " ".join(validator.errors)

        # Link integrity errors
        assert "Broken link" in error_messages
        assert "non-existent-story" in error_messages
        assert "missing-requirement" in error_messages

        # Alias formatting errors
        assert "Incorrect alias format" in error_messages

        # Properties schema errors
        assert "отсутствуют обязательные свойства" in error_messages

        # Temporary artifacts errors
        assert "является временным артефактом" in error_messages

        # Should have multiple errors
        assert len(validator.errors) >= 4

    def test_validator_performance_with_large_structure(self, temp_dir: Path):
        """Test validator performance with a large number of files."""
        # Create large structure
        (temp_dir / "pages").mkdir()
        (temp_dir / "journals").mkdir()

        # Create many files
        for i in range(50):
            (temp_dir / "pages" / f"STORY-API-{i}.md").write_text(f"""---
type:: [[story]]
status:: [[TODO]]
priority:: [[high]]
assignee:: [[@developer]]
epic:: [[EPIC-DEV]]
related-reqs:: 
---

# User Story {i}

Valid user story content.
""")

        for i in range(20):
            (
                temp_dir / "journals" / f"2024_01_{i:02d}.md"
            ).write_text(f"""# Journal Entry {i}

Valid journal content.
""")

        validator = KBValidator(temp_dir)

        # Run validation and measure performance
        import time

        start_time = time.time()

        with patch("builtins.print"):
            validator.run_validation()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete in reasonable time (< 5 seconds for 70 files)
        assert execution_time < 5.0

        # Should have no errors for valid structure
        assert len(validator.errors) == 0
