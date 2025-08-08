from abc import ABC, abstractmethod

from ..domain.request import GenerationRequest


class IHistoryRepository(ABC):
    """Interface for history repository operations."""

    @abstractmethod
    def save(self, request: GenerationRequest) -> None:
        """Save a generation request to the repository."""
        pass

    @abstractmethod
    def get_all(self) -> list[GenerationRequest]:
        """Retrieve all generation requests from the repository."""
        pass

    @abstractmethod
    def delete(self, request_id: int) -> None:
        """Delete a generation request by ID."""
        pass
