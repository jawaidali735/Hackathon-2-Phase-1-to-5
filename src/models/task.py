"""
Task data model definition
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    """
    Represents a user-defined task with unique numeric ID, title, optional description, and completion status.
    """
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = None

    def __post_init__(self):
        """
        Validate the task after initialization.
        """
        # Validate ID
        if not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("ID must be a positive integer")

        # Validate title
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Title must be a non-empty string")

        # Validate description
        if not isinstance(self.description, str):
            raise ValueError("Description must be a string")

        # Validate completed status
        if not isinstance(self.completed, bool):
            raise ValueError("Completed status must be a boolean")

        # Set created_at if not provided
        if self.created_at is None:
            self.created_at = datetime.now()