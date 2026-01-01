"""
Input validation utilities
"""


def validate_task_title(title):
    """
    Validate that a task title is not empty.

    Args:
        title (str): Task title to validate

    Returns:
        bool: True if valid, False otherwise

    Raises:
        ValueError: If title is invalid
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    return True


def validate_task_id(task_id):
    """
    Validate that a task ID is a positive integer.

    Args:
        task_id (int): Task ID to validate

    Returns:
        bool: True if valid, False otherwise

    Raises:
        ValueError: If ID is invalid
    """
    if not isinstance(task_id, int) or task_id <= 0:
        raise ValueError("Task ID must be a positive integer")
    return True


def validate_task_exists(task_list, task_id):
    """
    Validate that a task with the given ID exists in the task list.

    Args:
        task_list (list): List of tasks to search
        task_id (int): Task ID to validate

    Returns:
        bool: True if task exists, False otherwise

    Raises:
        ValueError: If task doesn't exist
    """
    for task in task_list:
        if task.id == task_id:
            return True
    raise ValueError(f"Task with ID {task_id} does not exist")