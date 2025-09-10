"""Shared test configurations and fixtures for development scripts testing."""

import shutil
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the project root to Python path so we can import scripts.development modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)


@pytest.fixture
def mock_logger() -> Generator[Mock, None, None]:
    """Provide a mock logger for testing."""
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger


@pytest.fixture
def sample_markdown_content() -> str:
    """Provide sample markdown content for testing."""
    return """# Sample Documentation

This is a sample markdown file with various content types.

## Code Examples

```python
def hello_world():
    print("Hello, World!")
```

## Links

Here are some links: [[existing-page]], [[another-page]]

## File References

Check out [[scripts/development/utils.py|`utils.py`]] for more information.

## Properties

type:: [[story]]
status:: [[TODO]]
priority:: [[high]]
"""


@pytest.fixture
def sample_raw_documentation() -> str:
    """Provide sample raw documentation content for parser testing."""
    return """# Development Documentation

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

## Non-functional Requirements
- Performance
- Security
```

## Roadmap (`roadmap.md`)
```markdown
# Development Roadmap

## Phase 1: Foundation
- Set up infrastructure
- Create core modules

## Phase 2: Features
- Implement user stories
- Add testing framework
```
"""


@pytest.fixture
def sample_log_content() -> str:
    """Provide sample log content for log analyzer testing."""
    return """2024-01-01 10:00:00 - INFO - Script started successfully
2024-01-01 10:00:01 - DEBUG - Processing file: test.txt
2024-01-01 10:00:02 - WARNING - File test.txt is empty
2024-01-01 10:00:03 - ERROR - Failed to process file: missing required field
2024-01-01 10:00:04 - CRITICAL - Database connection failed
2024-01-01 10:00:05 - INFO - Script completed with errors
2024-01-01 10:00:06 - SUCCESS - Backup created successfully
2024-01-01 10:00:07 - INFO - Execution finished
"""


@pytest.fixture
def sample_project_structure(temp_dir: Path) -> Path:
    """Create a sample project structure for testing."""
    # Create directories
    (temp_dir / "pages").mkdir()
    (temp_dir / "journals").mkdir()
    (temp_dir / ".roo" / "rules").mkdir(parents=True)
    (temp_dir / "src" / "code2markdown").mkdir(parents=True)
    (temp_dir / "tests").mkdir()

    # Create sample files
    (temp_dir / "pages" / "STORY-API-1.md").write_text("""---
type:: [[story]]
status:: [[TODO]]
priority:: [[high]]
assignee:: [[@developer]]
epic:: [[EPIC-DEV]]
related-reqs:: [[REQ-DEV-1]]
---

# Sample User Story

This is a sample user story for testing.
""")

    (temp_dir / "pages" / "REQ-DEV-1.md").write_text("""---
type:: [[requirement]]
status:: [[PLANNED]]
---

# Sample Requirement

This is a sample requirement for testing.
""")

    (temp_dir / "pages" / "rules.quality-guideline.md").write_text("""---
title:: Quality Guidelines
---

# Quality Guidelines

These are the quality guidelines for the project.
""")

    (temp_dir / "journals" / "2024_01_01.md").write_text("""# Daily Journal

## Tasks Completed
- Task 1
- Task 2
""")

    (
        temp_dir / ".roo" / "rules" / "quality-guideline.md"
    ).write_text("""# Quality Guidelines

These are the quality guidelines for the project.
""")

    (temp_dir / "README.md").write_text("""---
title:: Project README
---

# Project README

This is the main README file.
""")

    return temp_dir


@pytest.fixture
def mock_subprocess() -> Generator[Mock, None, None]:
    """Mock subprocess for testing command execution."""
    with patch("subprocess.Popen") as mock_popen:
        mock_process = Mock()
        mock_process.stdout = ["Line 1", "Line 2", "Line 3"]
        mock_process.wait.return_value = 0
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture
def sample_config_edn() -> str:
    """Provide sample Logseq config.edn content."""
    return """{:meta/version 1
 :meta/config {:repos ["/path/to/repo"]}
 :feature/enable-block-timestamps? true
 :feature/enable-journals? true
 :feature/enable-flashcards? false
 :hidden ["node_modules" ".git" ".venv" "tmp_cache"]
}
"""


@pytest.fixture
def sample_gitignore_content() -> str:
    """Provide sample .gitignore content."""
    return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.venv
venv/
ENV/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
.tmp/
"""


@pytest.fixture
def sample_markdown_with_broken_links() -> str:
    """Provide markdown content with broken links for testing."""
    return """# Document with Broken Links

This document contains some broken links for testing.

## Valid Links
- [[existing-page]]
- [[another-valid-page]]

## Broken Links
- [[non-existent-page]]
- [[broken-link]]
- [[missing-page]]

## File References
- [[scripts/development/utils.py|`utils.py`]]
- [[non-existent-file.py|`missing.py`]]
"""


@pytest.fixture
def sample_markdown_with_invalid_formatting() -> str:
    """Provide markdown content with invalid link formatting."""
    return """# Document with Invalid Formatting

## Incorrect Alias Formatting
- [[scripts/development/utils.py|`wrongname.py`]]
- [[src/main.py|`incorrect.py`]]

## Correct Formatting
- [[scripts/development/utils.py|`utils.py`]]
- [[src/main.py|`main.py`]]
"""


@pytest.fixture
def sample_story_missing_properties() -> str:
    """Provide a user story with missing required properties."""
    return """---
type:: [[story]]
status:: [[TODO]]
# Missing priority, assignee, epic, related-reqs
---

# Incomplete User Story

This story is missing required properties.
"""


@pytest.fixture
def sample_requirement_missing_properties() -> str:
    """Provide a requirement with missing required properties."""
    return """---
type:: [[requirement]]
# Missing status
---

# Incomplete Requirement

This requirement is missing required properties.
"""


@pytest.fixture
def sample_readme_without_title() -> str:
    """Provide a README without title property."""
    return """# Project README

This README is missing the title property.
"""


@pytest.fixture
def sample_temporary_artifact() -> str:
    """Provide content for a temporary artifact file."""
    return """# Raw Command Output

This is raw output from a command execution.
It should not be saved in the pages directory.
"""


@pytest.fixture
def mock_user_input() -> Generator[Mock, None, None]:
    """Mock user input functions."""
    with patch("builtins.input") as mock_input:
        yield mock_input


@pytest.fixture
def mock_confirm_action() -> Generator[Mock, None, None]:
    """Mock confirm_action function."""
    with patch("scripts.development.utils.ScriptUtils.confirm_action") as mock_confirm:
        yield mock_confirm


@pytest.fixture
def mock_prompt_for_input() -> Generator[Mock, None, None]:
    """Mock prompt_for_input function."""
    with patch("scripts.development.utils.ScriptUtils.prompt_for_input") as mock_prompt:
        yield mock_prompt


@pytest.fixture
def mock_select_from_options() -> Generator[Mock, None, None]:
    """Mock select_from_options function."""
    with patch(
        "scripts.development.utils.ScriptUtils.select_from_options"
    ) as mock_select:
        yield mock_select


class TestHelpers:
    """Helper class for common test operations."""

    @staticmethod
    def create_test_file(path: Path, content: str = "test content") -> None:
        """Create a test file with the given content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    @staticmethod
    def create_test_directory(path: Path) -> None:
        """Create a test directory."""
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def assert_file_exists(path: Path) -> None:
        """Assert that a file exists."""
        assert path.exists(), f"File {path} should exist"

    @staticmethod
    def assert_file_contains(path: Path, content: str) -> None:
        """Assert that a file contains specific content."""
        assert path.exists(), f"File {path} should exist"
        file_content = path.read_text()
        assert content in file_content, f"File {path} should contain '{content}'"

    @staticmethod
    def assert_valid_markdown_file(path: Path) -> None:
        """Assert that a file is a valid markdown file."""
        assert path.exists(), f"Markdown file {path} should exist"
        assert path.suffix == ".md", f"File {path} should have .md extension"
        content = path.read_text()
        assert len(content.strip()) > 0, f"Markdown file {path} should not be empty"


@pytest.fixture
def test_helpers() -> TestHelpers:
    """Provide test helpers instance."""
    return TestHelpers()


# Configure pytest to show more detailed assertion errors
def pytest_assertrepr_compare(op, left, right):
    """Custom assertion representation for better error messages."""
    if isinstance(left, str) and isinstance(right, str) and op == "in":
        return [
            "String not found in content:",
            f"  Expected: {right!r}",
            f"  Actual content length: {len(left)}",
            f"  First 200 chars: {left[:200]!r}",
        ]
    return None
