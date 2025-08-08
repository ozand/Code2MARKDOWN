from datetime import datetime

import pytest

from code2markdown.domain.filters import FileSize, FilterSettings
from code2markdown.domain.request import GenerationRequest


class TestGenerationRequest:
    """Test suite for GenerationRequest entity."""

    @pytest.fixture
    def sample_request_data(self):
        """Fixture providing sample data for GenerationRequest."""
        return {
            "id": None,
            "project_path": "/path/to/project",
            "project_name": "test-project",
            "template_name": "default_template.hbs",
            "markdown_content": "# Test Project\nThis is a test.",
            "filter_settings": FilterSettings(
                include_patterns=[".py", ".txt"],
                exclude_patterns=["node_modules", ".git"],
                max_file_size=FileSize(kb=50),
                show_excluded=True,
            ),
            "file_count": 10,
            "processed_at": datetime(2025, 1, 1, 12, 0, 0),
            "reference_url": "https://example.com",
        }

    def test_creation_with_minimal_required_fields(self):
        """Test creating a GenerationRequest with minimal required fields."""
        request = GenerationRequest(
            id=None,
            project_path="/path/to/project",
            project_name="test-project",
            template_name="default_template.hbs",
            markdown_content="# Test",
            filter_settings=FilterSettings(),
            file_count=1,
            processed_at=datetime.now(),
        )

        assert request.project_path == "/path/to/project"
        assert request.project_name == "test-project"
        assert request.template_name == "default_template.hbs"
        assert request.markdown_content == "# Test"
        assert isinstance(request.filter_settings, FilterSettings)
        assert request.file_count == 1
        assert isinstance(request.processed_at, datetime)
        assert request.reference_url is None

    def test_creation_with_all_fields(self, sample_request_data):
        """Test creating a GenerationRequest with all fields."""
        request = GenerationRequest(**sample_request_data)

        assert request.id is None
        assert request.project_path == sample_request_data["project_path"]
        assert request.project_name == sample_request_data["project_name"]
        assert request.template_name == sample_request_data["template_name"]
        assert request.markdown_content == sample_request_data["markdown_content"]
        assert request.filter_settings == sample_request_data["filter_settings"]
        assert request.file_count == sample_request_data["file_count"]
        assert request.processed_at == sample_request_data["processed_at"]
        assert request.reference_url == sample_request_data["reference_url"]

    def test_creation_with_optional_reference_url(self):
        """Test creating a GenerationRequest with optional reference_url."""
        request = GenerationRequest(
            id=None,
            project_path="/path/to/project",
            project_name="test-project",
            template_name="default_template.hbs",
            markdown_content="# Test",
            filter_settings=FilterSettings(),
            file_count=1,
            processed_at=datetime.now(),
            reference_url="https://example.com",
        )

        assert request.reference_url == "https://example.com"

    def test_creation_without_reference_url(self):
        """Test creating a GenerationRequest without reference_url (should default to None)."""
        request = GenerationRequest(
            id=None,
            project_path="/path/to/project",
            project_name="test-project",
            template_name="default_template.hbs",
            markdown_content="# Test",
            filter_settings=FilterSettings(),
            file_count=1,
            processed_at=datetime.now(),
        )

        assert request.reference_url is None

    def test_equality_comparison(self):
        """Test equality comparison between GenerationRequest instances."""
        now = datetime.now()
        filter_settings = FilterSettings(include_patterns=[".py"])

        request1 = GenerationRequest(
            id=1,
            project_path="/path/to/project",
            project_name="test-project",
            template_name="default_template.hbs",
            markdown_content="# Test",
            filter_settings=filter_settings,
            file_count=1,
            processed_at=now,
        )

        request2 = GenerationRequest(
            id=1,
            project_path="/path/to/project",
            project_name="test-project",
            template_name="default_template.hbs",
            markdown_content="# Test",
            filter_settings=filter_settings,
            file_count=1,
            processed_at=now,
        )

        assert request1 == request2

    def test_inequality_comparison_different_id(self):
        """Test inequality when IDs are different."""
        now = datetime.now()
        filter_settings = FilterSettings(include_patterns=[".py"])

        request1 = GenerationRequest(
            id=1,
            project_path="/path/to/project",
            project_name="test-project",
            template_name="default_template.hbs",
            markdown_content="# Test",
            filter_settings=filter_settings,
            file_count=1,
            processed_at=now,
        )

        request2 = GenerationRequest(
            id=2,
            project_path="/path/to/project",
            project_name="test-project",
            template_name="default_template.hbs",
            markdown_content="# Test",
            filter_settings=filter_settings,
            file_count=1,
            processed_at=now,
        )

        assert request1 != request2

    def test_inequality_comparison_different_project_path(self):
        """Test inequality when project paths are different."""
        now = datetime.now()
        filter_settings = FilterSettings(include_patterns=[".py"])

        request1 = GenerationRequest(
            id=1,
            project_path="/path/to/project1",
            project_name="test-project",
            template_name="default_template.hbs",
            markdown_content="# Test",
            filter_settings=filter_settings,
            file_count=1,
            processed_at=now,
        )

        request2 = GenerationRequest(
            id=1,
            project_path="/path/to/project2",
            project_name="test-project",
            template_name="default_template.hbs",
            markdown_content="# Test",
            filter_settings=filter_settings,
            file_count=1,
            processed_at=now,
        )

        assert request1 != request2
