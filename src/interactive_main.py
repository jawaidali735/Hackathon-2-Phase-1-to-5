#!/usr/bin/env python3
"""
Interactive Todo Console Application
Entry point for interactive CLI mode
"""

import sys
from datetime import datetime
from task_manager import TaskManager


def display_menu():
    """Display the main menu options."""
    print("\n" + "="*50)
    print("TODO APPLICATION - INTERACTIVE MODE")
    print("="*50)
    print("What would you like to do?")
    print("1. Add a new task")
    print("2. View all tasks")
    print("3. Update a task")
    print("4. Mark task as complete")
    print("5. Mark task as incomplete")
    print("6. Delete a task")
    print("7. Exit")
    print("="*50)


def get_user_choice():
    """Get and validate user choice from menu."""
    while True:
        try:
            choice = input("Enter your choice (1-7): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return choice
            else:
                print("[-] Invalid choice. Please enter a number between 1 and 7.")
        except KeyboardInterrupt:
            print("\n[+] Exiting application...")
            sys.exit(0)


def add_task_interactive(task_manager):
    """Interactive task addition."""
    print("\n--- ADD NEW TASK ---")
    title = input("Enter task title: ").strip()
    if not title:
        print("[-] Task title cannot be empty!")
        return

    description = input("Enter task description (optional, press Enter to skip): ").strip()

    try:
        task = task_manager.add_task(title, description)
        print(f"[+] Task #{task.id} created: {task.title}")
        print(f"    Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except ValueError as e:
        print(f"[-] Error: {e}")


def view_tasks_interactive(task_manager):
    """Interactive task viewing."""
    print("\n--- ALL TASKS ---")
    tasks = task_manager.list_tasks()

    if not tasks:
        print("No tasks found.")
        return

    print(f"{'ID':<4} {'Status':<12} {'Title':<30} {'Description':<30} {'Created'}")
    print("-" * 100)

    for task in tasks:
        status = "[x] Complete" if task.completed else "[ ] Incomplete"
        # Truncate long titles and descriptions
        title = task.title[:28] + ".." if len(task.title) > 30 else task.title
        desc = task.description[:28] + ".." if len(task.description) > 30 else task.description
        created_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Using current time as approximation
        print(f"{task.id:<4} {status:<12} {title:<30} {desc:<30} {created_time}")


def update_task_interactive(task_manager):
    """Interactive task update."""
    print("\n--- UPDATE TASK ---")
    try:
        task_id = int(input("Enter task ID to update: ").strip())
    except ValueError:
        print("[-] Invalid task ID. Please enter a number.")
        return

    # Check if task exists
    task = task_manager.get_task_by_id(task_id)
    if not task:
        print(f"[-] Task #{task_id} not found.")
        return

    print(f"Current task: {task.title}")
    new_title = input(f"Enter new title (current: '{task.title}', press Enter to keep current): ").strip()
    if new_title == "":
        new_title = task.title

    if not new_title.strip():
        print("[-] Task title cannot be empty!")
        return

    new_description = input(f"Enter new description (current: '{task.description}', press Enter to keep current): ").strip()
    if new_description == "":
        new_description = task.description

    try:
        updated_task = task_manager.update_task(task_id, new_title, new_description)
        if updated_task:
            print(f"[+] Task #{updated_task.id} updated successfully!")
        else:
            print(f"[-] Failed to update task #{task_id}")
    except ValueError as e:
        print(f"[-] Error: {e}")


def mark_complete_interactive(task_manager):
    """Interactive mark complete."""
    print("\n--- MARK TASK COMPLETE ---")
    try:
        task_id = int(input("Enter task ID to mark as complete: ").strip())
    except ValueError:
        print("[-] Invalid task ID. Please enter a number.")
        return

    success = task_manager.mark_complete(task_id)
    if success:
        print(f"[+] Task #{task_id} marked as complete!")
    else:
        print(f"[-] Task #{task_id} not found.")


def mark_incomplete_interactive(task_manager):
    """Interactive mark incomplete."""
    print("\n--- MARK TASK INCOMPLETE ---")
    try:
        task_id = int(input("Enter task ID to mark as incomplete: ").strip())
    except ValueError:
        print("[-] Invalid task ID. Please enter a number.")
        return

    success = task_manager.mark_incomplete(task_id)
    if success:
        print(f"[+] Task #{task_id} marked as incomplete!")
    else:
        print(f"[-] Task #{task_id} not found.")


def delete_task_interactive(task_manager):
    """Interactive task deletion."""
    print("\n--- DELETE TASK ---")
    try:
        task_id = int(input("Enter task ID to delete: ").strip())
    except ValueError:
        print("[-] Invalid task ID. Please enter a number.")
        return

    success = task_manager.delete_task(task_id)
    if success:
        print(f"[+] Task #{task_id} deleted!")
    else:
        print(f"[-] Task #{task_id} not found.")


def main():
    """Main interactive application loop."""
    print("Welcome to the Todo Application!")
    print("This application stores tasks in memory only (data is lost when application closes)")

    task_manager = TaskManager()

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == '1':
            add_task_interactive(task_manager)
        elif choice == '2':
            view_tasks_interactive(task_manager)
        elif choice == '3':
            update_task_interactive(task_manager)
        elif choice == '4':
            mark_complete_interactive(task_manager)
        elif choice == '5':
            mark_incomplete_interactive(task_manager)
        elif choice == '6':
            delete_task_interactive(task_manager)
        elif choice == '7':
            print("[+] Thank you for using the Todo Application. Goodbye!")
            break

        # Pause to let user see the result
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()