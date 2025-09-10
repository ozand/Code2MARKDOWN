import os
import sqlite3
from datetime import datetime

import pytest

from code2markdown.domain.filters import FileSize, FilterSettings
from code2markdown.domain.request import GenerationRequest
from code2markdown.infrastructure.database import SqliteHistoryRepository


class TestSqliteHistoryRepository:
    """Test suite for SqliteHistoryRepository."""

    @pytest.fixture
    def db_path(self):
        """Fixture providing a temporary database path."""
        return "test_code2markdown.db"

    @pytest.fixture
    def repository(self, db_path):
        """Fixture providing a SqliteHistoryRepository instance."""
        # Ensure clean state
        if os.path.exists(db_path):
            os.remove(db_path)
        repo = SqliteHistoryRepository(db_path=db_path)
        yield repo
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.fixture
    def sample_request(self):
        """Fixture providing a sample GenerationRequest."""
        return GenerationRequest(
            id=None,
            project_path="/path/to/project",
            project_name="test-project",
            template_name="default_template.hbs",
            markdown_content="# Test Project\nThis is a test.",
            filter_settings=FilterSettings(
                include_patterns=[".py", ".txt"],
                exclude_patterns=["node_modules", ".git"],
                max_file_size=FileSize(kb=50),
                show_excluded=True,
            ),
            file_count=5,
            processed_at=datetime(2025, 1, 1, 12, 0, 0),
            reference_url="https://example.com",
        )

    def test_save_and_get_all(self, repository, sample_request):
        """Test saving a request and retrieving it."""
        # Save the request
        repository.save(sample_request)

        # Verify ID was assigned
        assert sample_request.id is not None

        # Retrieve all requests
        requests = repository.get_all()

        # Verify we got one request
        assert len(requests) == 1

        # Verify the retrieved request matches the saved one
        retrieved = requests[0]
        assert retrieved.id == sample_request.id
        assert retrieved.project_path == sample_request.project_path
        assert retrieved.project_name == sample_request.project_name
        assert retrieved.template_name == sample_request.template_name
        assert retrieved.markdown_content == sample_request.markdown_content
        assert retrieved.filter_settings == sample_request.filter_settings
        assert retrieved.file_count == sample_request.file_count
        assert retrieved.processed_at == sample_request.processed_at
        assert retrieved.reference_url == sample_request.reference_url

    def test_save_multiple_requests(self, repository, sample_request):
        """Test saving multiple requests."""
        # Modify the sample request for multiple saves
        request1 = sample_request
        request2 = GenerationRequest(
            **{
                **sample_request.__dict__,
                "id": None,
                "project_path": "/path/to/another/project",
                "processed_at": datetime(2025, 1, 2, 12, 0, 0),
            }
        )

        # Save both requests
        repository.save(request1)
        repository.save(request2)

        # Retrieve all requests
        requests = repository.get_all()

        # Verify we got two requests
        assert len(requests) == 2

        # Verify both requests are present and correct
        assert (
            requests[0].project_path == request2.project_path
        )  # Should be ordered by processed_at DESC
        assert requests[1].project_path == request1.project_path

    def test_get_all_empty_database(self, repository):
        """Test getting all requests from an empty database."""
        requests = repository.get_all()
        assert len(requests) == 0

    def test_delete_request(self, repository, sample_request):
        """Test deleting a request."""
        # Save a request
        repository.save(sample_request)

        # Verify it was saved
        requests = repository.get_all()
        assert len(requests) == 1

        # Delete the request
        repository.delete(sample_request.id)

        # Verify it was deleted
        requests = repository.get_all()
        assert len(requests) == 0

    def test_delete_nonexistent_request(self, repository):
        """Test deleting a non-existent request (should not raise exception)."""
        # Try to delete a request that doesn't exist
        repository.delete(999)  # Should not raise an exception

        # Verify database is still empty
        requests = repository.get_all()
        assert len(requests) == 0

    def test_filter_settings_serialization(self, repository, sample_request):
        """Test that filter settings are properly serialized and deserialized."""
        # Save the request
        repository.save(sample_request)

        # Retrieve it
        requests = repository.get_all()
        retrieved = requests[0]

        # Verify filter settings were preserved
        assert (
            retrieved.filter_settings.include_patterns
            == sample_request.filter_settings.include_patterns
        )
        assert (
            retrieved.filter_settings.exclude_patterns
            == sample_request.filter_settings.exclude_patterns
        )
        assert (
            retrieved.filter_settings.max_file_size.kb
            == sample_request.filter_settings.max_file_size.kb
        )
        assert (
            retrieved.filter_settings.show_excluded
            == sample_request.filter_settings.show_excluded
        )

    def test_backward_compatibility_with_legacy_data(self, db_path):
        """Test that the repository can handle legacy data format."""
        # Create database with legacy data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table and insert legacy data (without proper JSON structure)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_path TEXT NOT NULL,
                template_name TEXT NOT NULL,
                markdown_content TEXT NOT NULL,
                reference_url TEXT,
                processed_at DATETIME NOT NULL,
                file_count INTEGER DEFAULT 0,
                filter_settings TEXT,
                project_name TEXT
            )
        """)

        # Insert legacy data (filter_settings as raw string)
        cursor.execute(
            """
            INSERT INTO requests 
            (project_path, project_name, template_name, markdown_content, reference_url, processed_at, file_count, filter_settings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "/legacy/path",
                "legacy-project",
                "default_template.hbs",
                "# Legacy Project",
                "https://legacy.com",
                "2024-01-01 12:00:00",
                3,
                '{"include_patterns": [".py"], "exclude_patterns": ["node_modules"], "max_file_size": 50, "show_excluded": false}',  # Proper JSON
            ),
        )

        # Insert malformed JSON data to test error handling
        cursor.execute(
            """
            INSERT INTO requests 
            (project_path, project_name, template_name, markdown_content, reference_url, processed_at, file_count, filter_settings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "/malformed/path",
                "malformed-project",
                "default_template.hbs",
                "# Malformed Project",
                "https://malformed.com",
                "2024-01-02 12:00:00",
                2,
                "this is not valid json",  # Malformed JSON
            ),
        )

        conn.commit()
        conn.close()

        # Create repository and test
        repo = SqliteHistoryRepository(db_path=db_path)
        requests = repo.get_all()

        # Should handle both cases gracefully
        assert len(requests) == 2

        # First request should have proper filter settings
        # Find the request with the legacy path
        legacy_request = next(
            req for req in requests if req.project_path == "/legacy/path"
        )
        assert legacy_request.filter_settings.include_patterns == [".py"]
        assert legacy_request.filter_settings.exclude_patterns == ["node_modules"]
        assert legacy_request.filter_settings.max_file_size.kb == 50
        assert legacy_request.filter_settings.show_excluded is False
        # Second request should have default filter settings due to malformed JSON
        malformed_request = next(
            req for req in requests if req.project_path == "/malformed/path"
        )
        assert isinstance(malformed_request.filter_settings, FilterSettings)

        # Second request should have default filter settings due to malformed JSON
        # Find the request with the malformed path
        malformed_request = next(
            req for req in requests if req.project_path == "/malformed/path"
        )
        assert isinstance(malformed_request.filter_settings, FilterSettings)
        assert isinstance(
            requests[1].filter_settings, FilterSettings
        )  # Should be default settings

    def test_error_handling_on_save(self, repository, sample_request):
        """Test error handling when saving fails."""
        # Creating repository with invalid path should raise OperationalError
        with pytest.raises(sqlite3.OperationalError):
            SqliteHistoryRepository(db_path="/invalid/path/db.db")

    def test_error_handling_on_delete(self, repository):
        """Test error handling when deletion fails."""
        # Creating repository with invalid path should raise OperationalError
        with pytest.raises(sqlite3.OperationalError):
            SqliteHistoryRepository(db_path="/invalid/path/db.db")
