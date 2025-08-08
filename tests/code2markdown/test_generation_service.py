import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from code2markdown.application.repository import IHistoryRepository
from code2markdown.application.services import GenerationService
from code2markdown.domain.filters import FileSize, FilterSettings
from code2markdown.domain.request import GenerationRequest


class TestGenerationService:
    """Test suite for GenerationService class."""

    @pytest.fixture
    def mock_repo(self):
        """Fixture providing a mocked repository."""
        return Mock(spec=IHistoryRepository)

    @pytest.fixture
    def template_dir(self):
        """Fixture providing a temporary directory for templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def service(self, mock_repo, template_dir):
        """Fixture providing a GenerationService instance with mocked repository."""
        return GenerationService(history_repo=mock_repo, templates_dir=template_dir)

    @pytest.fixture
    def sample_filters(self):
        """Fixture providing sample filter settings."""
        return FilterSettings(
            include_patterns=[".py", ".md"],
            exclude_patterns=["__pycache__", ".git"],
            max_file_size=FileSize(kb=100),
            show_excluded=False,
        )

    def test_initialization(self, mock_repo, template_dir):
        """Test that GenerationService initializes correctly with repository."""
        service = GenerationService(history_repo=mock_repo, templates_dir=template_dir)
        assert service._history_repo == mock_repo

    @patch.object(GenerationService, "_load_template")
    def test_generate_and_save_documentation_success(
        self, mock_load_template, service, mock_repo, sample_filters
    ):
        """Test successful documentation generation and saving."""
        # Arrange
        template_name = "test_template.hbs"
        reference_url = "https://example.com"

        # Configure the mock
        mock_template = Mock()
        mock_template.return_value = "# Generated Documentation\nContent here"
        mock_load_template.return_value = mock_template

        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            os.makedirs(os.path.join(temp_dir, "src"))
            os.makedirs(os.path.join(temp_dir, "docs"))

            # Create test files
            with open(os.path.join(temp_dir, "src", "main.py"), "w") as f:
                f.write("# Main Python file\nprint('Hello')")

            with open(os.path.join(temp_dir, "docs", "README.md"), "w") as f:
                f.write("# Project Documentation\nThis is a test.")

            # Act
            result = service.generate_and_save_documentation(
                project_path=temp_dir,
                template_name=template_name,
                filters=sample_filters,
                reference_url=reference_url,
            )

            # Assert that the result contains expected content
            assert "Generated Documentation" in result
            assert "Content here" in result

            # Check that repository save was called with correct request
            assert mock_repo.save.called
            saved_request = mock_repo.save.call_args[0][0]
            assert isinstance(saved_request, GenerationRequest)
            assert saved_request.project_path == temp_dir
            assert saved_request.template_name == template_name
            assert saved_request.reference_url == reference_url
            assert saved_request.filter_settings == sample_filters
            assert saved_request.file_count == 2  # Two files were processed
            assert "Generated Documentation" in saved_request.markdown_content
            assert isinstance(saved_request.processed_at, datetime)

    @patch.object(GenerationService, "_load_template")
    def test_generate_and_save_documentation_with_selected_files(
        self, mock_load_template, service, mock_repo, sample_filters
    ):
        """Test generation with explicitly selected files."""
        # Arrange
        template_name = "test_template.hbs"

        # Configure the mock
        mock_template = Mock()
        mock_template.return_value = "# Generated Documentation\nContent here"
        mock_load_template.return_value = mock_template

        # Create selected files list
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            os.makedirs(os.path.join(temp_dir, "src"))
            os.makedirs(os.path.join(temp_dir, "docs"))
            os.makedirs(os.path.join(temp_dir, "tests"))

            # Create test files
            with open(os.path.join(temp_dir, "src", "main.py"), "w") as f:
                f.write("# Main Python file\nprint('Hello')")

            with open(os.path.join(temp_dir, "docs", "README.md"), "w") as f:
                f.write("# Project Documentation\nThis is a test.")

            with open(os.path.join(temp_dir, "tests", "test_main.py"), "w") as f:
                f.write("# Test file\nassert True")

            # Create filters with selected files
            selected_files = [
                os.path.join(temp_dir, "src", "main.py"),
                os.path.join(temp_dir, "docs", "README.md"),
            ]
            filters_with_selection = FilterSettings(
                include_patterns=[".py", ".md"],
                exclude_patterns=["__pycache__", ".git"],
                max_file_size=FileSize(kb=100),
                show_excluded=False,
                selected_files=set(selected_files),
            )

            # Act
            result = service.generate_and_save_documentation(
                project_path=temp_dir,
                template_name=template_name,
                filters=filters_with_selection,
            )

            # Assert that the result contains expected content
            assert "Generated Documentation" in result
            assert "Content here" in result

            # Check that repository save was called
            assert mock_repo.save.called
            saved_request = mock_repo.save.call_args[0][0]
            assert saved_request.file_count == 2  # Only selected files processed

    def test_generate_and_save_documentation_invalid_path(
        self, service, mock_repo, sample_filters
    ):
        """Test that invalid project path raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Project path must be a valid directory"):
            service.generate_and_save_documentation(
                project_path="/invalid/path",
                template_name="test_template.hbs",
                filters=sample_filters,
            )

        # Verify repository was not called
        assert not mock_repo.save.called

    def test_generate_and_save_documentation_template_not_found(
        self, service, mock_repo, sample_filters
    ):
        """Test that missing template raises ValueError."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Act & Assert
            with pytest.raises(ValueError, match="Template test_template.hbs not found."):
                service.generate_and_save_documentation(
                    project_path=temp_dir,
                    template_name="test_template.hbs",
                    filters=sample_filters,
                )

            # Verify repository was not called
            assert not mock_repo.save.called

    @patch.object(GenerationService, "_load_template")
    def test_generate_and_save_documentation_save_error(
        self, mock_load_template, service, mock_repo, sample_filters
    ):
        """Test that repository save errors are propagated."""
        # Arrange
        # Configure the mock
        mock_template = Mock()
        mock_template.return_value = "# Generated Documentation\nContent here"
        mock_load_template.return_value = mock_template

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            with open(os.path.join(temp_dir, "test.py"), "w") as f:
                f.write("# Test file")

            # Mock repository to raise an exception
            mock_repo.save.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(
                Exception, match="Error saving request to database: Database error"
            ):
                service.generate_and_save_documentation(
                    project_path=temp_dir,
                    template_name="default_template.hbs",
                    filters=sample_filters,
                )

    @patch.object(GenerationService, "_load_template")
    def test_generate_and_save_documentation_binary_file_exclusion(
        self, mock_load_template, service, mock_repo, sample_filters
    ):
        """Test that binary files are excluded from processing."""
        # Arrange
        # Configure the mock
        mock_template = Mock()
        mock_template.return_value = "# Generated Documentation\nContent here"
        mock_load_template.return_value = mock_template

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a text file and a binary file
            with open(os.path.join(temp_dir, "test.py"), "w") as f:
                f.write("# Test Python file")

            # Create a binary file (simulated)
            with open(os.path.join(temp_dir, "test.pyc"), "wb") as f:
                f.write(b"\x00\x01\x02\x03")

            # Act
            result = service.generate_and_save_documentation(
                project_path=temp_dir,
                template_name="default_template.hbs",
                filters=sample_filters,
            )

            # Assert that the result contains expected content
            assert "Generated Documentation" in result
            assert "Content here" in result

            saved_request = mock_repo.save.call_args[0][0]
            assert saved_request.file_count == 1  # Only the .py file was processed

    @patch.object(GenerationService, "_load_template")
    def test_generate_and_save_documentation_fallback_behavior(
        self, mock_load_template, service, mock_repo, sample_filters
    ):
        """Test fallback behavior when no files are explicitly selected."""
        # Arrange
        # Configure the mock
        mock_template = Mock()
        mock_template.return_value = "# Generated Documentation\nContent here"
        mock_load_template.return_value = mock_template

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            with open(os.path.join(temp_dir, "test.py"), "w") as f:
                f.write("# Test Python file")

            # Create filters without selected_files
            filters_without_selection = FilterSettings(
                include_patterns=[".py"],
                exclude_patterns=["__pycache__", ".git"],
                max_file_size=FileSize(kb=100),
                show_excluded=False,
            )

            # Act
            result = service.generate_and_save_documentation(
                project_path=temp_dir,
                template_name="default_template.hbs",
                filters=filters_without_selection,
            )

            # Assert that the result contains expected content
            assert "Generated Documentation" in result
            assert "Content here" in result

            saved_request = mock_repo.save.call_args[0][0]
            assert saved_request.file_count == 1
