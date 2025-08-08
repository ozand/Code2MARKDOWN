from dataclasses import dataclass
from datetime import datetime

from .filters import FilterSettings


@dataclass
class GenerationRequest:
    """Entity representing a documentation generation request."""

    id: int | None
    project_path: str
    project_name: str
    template_name: str
    markdown_content: str
    filter_settings: FilterSettings
    file_count: int
    processed_at: datetime
    reference_url: str | None = None
