#!/usr/bin/env python3
"""
Todo In-Memory Console Application
Entry point and CLI interface
"""

import sys
import argparse

# Handle both direct execution and module execution
try:
    # Try relative import first (when run as module)
    from .task_manager import TaskManager
except ImportError:
    # Fall back to absolute import (when run as script)
    from task_manager import TaskManager


def create_parser():
    """Create and configure the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Todo In-Memory Console Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add "Buy groceries" "Milk, bread, eggs"
  %(prog)s list
  %(prog)s update 1 "Buy groceries" "Milk, bread, eggs, fruits"
  %(prog)s complete 1
  %(prog)s incomplete 1
  %(prog)s delete 1
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('description', nargs='?', default='', help='Task description (optional)')

    # List command
    list_parser = subparsers.add_parser('list', help='List all tasks')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('id', type=int, help='Task ID')
    update_parser.add_argument('title', help='New task title')
    update_parser.add_argument('description', nargs='?', default='', help='New task description (optional)')

    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark task as complete')
    complete_parser.add_argument('id', type=int, help='Task ID')

    # Incomplete command
    incomplete_parser = subparsers.add_parser('incomplete', help='Mark task as incomplete')
    incomplete_parser.add_argument('id', type=int, help='Task ID')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', type=int, help='Task ID')

    return parser


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
    print("7. Show statistics")
    print("8. Exit")
    print("="*50)


def get_user_choice():
    """Get and validate user choice from menu."""
    while True:
        try:
            choice = input("Enter your choice (1-8): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return choice
            else:
                print("[-] Invalid choice. Please enter a number between 1 and 8.")
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
    except ValueError as e:
        print(f"[-] Error: {e}")


def view_tasks_interactive(task_manager):
    """Interactive task viewing."""
    print("\n--- ALL TASKS ---")
    tasks = task_manager.list_tasks()

    if not tasks:
        print("No tasks found.")
        return

    # Print header with bold formatting (using console codes)
    print("\033[1m" + f"{'ID':<4} {'TITLE':<30} {'STATUS':<8} {'CREATED':<20} {'DESCRIPTION'}" + "\033[0m")
    print("-" * 80)

    for task in tasks:
        status = "[C] Complete" if task.completed else "[P] Pending"
        # Truncate long titles and descriptions if needed
        title = task.title[:28] + ".." if len(task.title) > 30 else task.title
        desc = task.description[:30] if task.description else ""
        desc = desc[:28] + ".." if len(desc) > 30 else desc
        created_time = task.created_at.strftime('%Y-%m-%d %H:%M') if task.created_at else ""
        print(f"{task.id:<4} {title:<30} {status:<8} {created_time:<20} {desc}")


def show_statistics(task_manager):
    """Show task statistics."""
    tasks = task_manager.list_tasks()
    if not tasks:
        print("No tasks available for statistics.")
        return

    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.completed)
    pending_tasks = total_tasks - completed_tasks

    print(f"\n--- STATISTICS ---")
    print(f"Total Tasks: {total_tasks}")
    print(f"Completed:   {completed_tasks}")
    print(f"Pending:     {pending_tasks}")
    if total_tasks > 0:
        completion_rate = (completed_tasks / total_tasks) * 100
        print(f"Completion:  {completion_rate:.1f}%")


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
    """Main entry point for the application."""
    parser = create_parser()
    args = parser.parse_args()

    # Initialize the task manager
    task_manager = TaskManager()

    # If no command is provided, run in interactive mode
    if args.command is None:
        print("Welcome to the Todo Application!")
        print("This application stores tasks in memory only (data is lost when application closes)")

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
                show_statistics(task_manager)
            elif choice == '8':
                print("[+] Thank you for using the Todo Application. Goodbye!")
                break

            # Pause to let user see the result
            input("\nPress Enter to continue...")
    else:
        # Process command line arguments as before
        try:
            if args.command == 'add':
                task = task_manager.add_task(args.title, args.description)
                print(f"[+] Task #{task.id} created: {task.title}")

            elif args.command == 'list':
                tasks = task_manager.list_tasks()
                if not tasks:
                    print("No tasks found.")
                else:
                    print(f"{'ID':<4} {'TITLE':<30} {'STATUS':<8} {'CREATED':<20} {'DESCRIPTION'}")
                    print("-" * 80)
                    for task in tasks:
                        status = "[C] Complete" if task.completed else "[P] Pending"
                        created_time = task.created_at.strftime('%Y-%m-%d %H:%M') if task.created_at else ""
                        print(f"{task.id:<4} {task.title:<30} {status:<8} {created_time:<20} {task.description}")

            elif args.command == 'update':
                task = task_manager.update_task(args.id, args.title, args.description)
                if task:
                    print(f"[+] Task #{task.id} updated")
                else:
                    print(f"[-] Error: Task #{args.id} not found")
                    sys.exit(1)

            elif args.command == 'complete':
                success = task_manager.mark_complete(args.id)
                if success:
                    print(f"[+] Task #{args.id} marked as complete")
                else:
                    print(f"[-] Error: Task #{args.id} not found")
                    sys.exit(1)

            elif args.command == 'incomplete':
                success = task_manager.mark_incomplete(args.id)
                if success:
                    print(f"[+] Task #{args.id} marked as incomplete")
                else:
                    print(f"[-] Error: Task #{args.id} not found")
                    sys.exit(1)

            elif args.command == 'delete':
                success = task_manager.delete_task(args.id)
                if success:
                    print(f"[+] Task #{args.id} deleted")
                else:
                    print(f"[-] Error: Task #{args.id} not found")
                    sys.exit(1)

        except ValueError as e:
            print(f"[-] Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"[-] Unexpected error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()