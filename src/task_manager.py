"""
Core business logic for task management
"""

# Handle both direct execution and module execution
try:
    # Try relative imports first (when run as module)
    from .models.task import Task
    from .utils.validators import validate_task_title, validate_task_id
except ImportError:
    # Fall back to absolute imports (when run as script)
    from models.task import Task
    from utils.validators import validate_task_title, validate_task_id


class TaskManager:
    """
    Manages the collection of tasks in memory with operations to add, update, delete, and list tasks.
    """

    def __init__(self):
        """Initialize the task manager with an empty list of tasks and ID counter."""
        self.tasks = []
        self.next_id = 1

    def add_task(self, title, description=""):
        """
        Add a new task with a unique ID.

        Args:
            title (str): Task title (required, non-empty)
            description (str): Task description (optional)

        Returns:
            Task: The newly created task

        Raises:
            ValueError: If title is empty or None
        """
        # Validate title
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        # Create task with unique ID
        from datetime import datetime
        task = Task(self.next_id, title.strip(), description.strip() if description else "", False, datetime.now())

        # Add to collection and increment ID counter
        self.tasks.append(task)
        self.next_id += 1

        return task

    def list_tasks(self):
        """
        Get all tasks in the collection.

        Returns:
            list: List of all tasks
        """
        return self.tasks

    def get_task_by_id(self, task_id):
        """
        Find a task by its ID.

        Args:
            task_id (int): Task ID to search for

        Returns:
            Task: The task with the given ID, or None if not found
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id, title, description=""):
        """
        Update an existing task's title and description.

        Args:
            task_id (int): ID of the task to update
            title (str): New task title
            description (str): New task description (optional)

        Returns:
            Task: The updated task, or None if task doesn't exist

        Raises:
            ValueError: If title is empty or None
        """
        # Validate title
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        # Find the task
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        # Update the task
        task.title = title.strip()
        task.description = description.strip() if description else ""

        return task

    def mark_complete(self, task_id):
        """
        Mark a task as complete.

        Args:
            task_id (int): ID of the task to mark as complete

        Returns:
            bool: True if successful, False if task doesn't exist
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        task.completed = True
        return True

    def mark_incomplete(self, task_id):
        """
        Mark a task as incomplete.

        Args:
            task_id (int): ID of the task to mark as incomplete

        Returns:
            bool: True if successful, False if task doesn't exist
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        task.completed = False
        return True

    def delete_task(self, task_id):
        """
        Delete a task by its ID.

        Args:
            task_id (int): ID of the task to delete

        Returns:
            bool: True if successful, False if task doesn't exist
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        self.tasks.remove(task)
        return True