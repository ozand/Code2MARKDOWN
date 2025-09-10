import json
import os
import sqlite3
from datetime import datetime

from code2markdown.application.repository import IHistoryRepository
from code2markdown.domain.filters import FileSize, FilterSettings
from code2markdown.domain.request import GenerationRequest


class SqliteHistoryRepository(IHistoryRepository):
    """Implementation of history repository using SQLite database."""

    def __init__(self, db_path: str = "code2markdown.db"):
        self._db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database and create required tables and columns."""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
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

        # Add new columns if they don't exist (backward compatibility)
        try:
            cursor.execute("ALTER TABLE requests ADD COLUMN file_count INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE requests ADD COLUMN filter_settings TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE requests ADD COLUMN project_name TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists

        conn.commit()
        conn.close()

    def save(self, request: GenerationRequest) -> None:
        """Save a generation request to the database."""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        try:
            # Convert FilterSettings to JSON for storage
            filter_settings_json = json.dumps(
                {
                    "include_patterns": request.filter_settings.include_patterns,
                    "exclude_patterns": request.filter_settings.exclude_patterns,
                    "max_file_size": request.filter_settings.max_file_size.kb,
                    "show_excluded": request.filter_settings.show_excluded,
                }
            )

            cursor.execute(
                """
                INSERT INTO requests
                (project_path, project_name, template_name, markdown_content, reference_url, processed_at, file_count, filter_settings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    request.project_path,
                    request.project_name,
                    request.template_name,
                    request.markdown_content,
                    request.reference_url,
                    request.processed_at.isoformat(),
                    request.file_count,
                    filter_settings_json,
                ),
            )

            # Update the request ID with the auto-generated value
            request.id = cursor.lastrowid

            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_all(self) -> list[GenerationRequest]:
        """Retrieve all generation requests from the database."""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM requests ORDER BY processed_at DESC")
            rows = cursor.fetchall()

            requests = []
            for row in rows:
                # Extract filter settings and parse JSON
                filter_settings_data = row[7]  # filter_settings column
                filter_settings = None
                if filter_settings_data:
                    try:
                        data = json.loads(filter_settings_data)
                        # Reconstruct FilterSettings object
                        filter_settings = FilterSettings(
                            include_patterns=data.get("include_patterns", []),
                            exclude_patterns=data.get("exclude_patterns", []),
                            max_file_size=FileSize(kb=data.get("max_file_size", 50)),
                            show_excluded=data.get("show_excluded", False),
                        )
                    except (json.JSONDecodeError, ValueError):
                        # Handle legacy format or corrupted data
                        pass

                # Handle legacy data where project_name might be missing
                project_name = (
                    row[8]
                    if len(row) > 8
                    else os.path.basename(row[1])
                    if row[1] != "N/A"
                    else "Unknown"
                )

                request = GenerationRequest(
                    id=row[0],
                    project_path=row[1],
                    project_name=project_name,
                    template_name=row[2],
                    markdown_content=row[3],
                    reference_url=row[4],
                    processed_at=datetime.fromisoformat(row[5]),
                    file_count=row[6],
                    filter_settings=filter_settings
                    or FilterSettings(),  # Use default if parsing failed
                )
                requests.append(request)

            return requests
        finally:
            conn.close()

    def delete(self, request_id: int) -> None:
        """Delete a generation request by ID."""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM requests WHERE id = ?", (request_id,))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
