import json
import os
from datetime import datetime
from enum import Enum
import sys
from typing import List, Dict, Optional

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Status(Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class Task:
    def __init__(self, title: str, description: str = "", due_date: str = None, 
                 priority: Priority = Priority.MEDIUM, status: Status = Status.PENDING):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.status = status
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.completed_at = None

    def __str__(self) -> str:
        due_date = self.due_date if self.due_date else "No due date"
        completed = f"Completed at: {self.completed_at}" if self.completed_at else ""
        return (
            f"Title: {self.title}\n"
            f"Description: {self.description}\n"
            f"Status: {self.status.value}\n"
            f"Priority: {self.priority.name}\n"
            f"Due: {due_date}\n"
            f"Created: {self.created_at}\n"
            f"{completed}"
        )

    def mark_complete(self):
        self.status = Status.COMPLETED
        self.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority.name,
            "status": self.status.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        task = cls(
            title=data["title"],
            description=data["description"],
            due_date=data["due_date"],
            priority=Priority[data["priority"]],
            status=Status(data["status"])
        )
        task.created_at = data["created_at"]
        task.completed_at = data["completed_at"]
        return task

class TaskManager:
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename
        self.tasks: List[Task] = []
        self.load_tasks()

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, index: int):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save_tasks()
            return True
        return False

    def update_task(self, index: int, **kwargs):
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    if key == "priority":
                        setattr(task, key, Priority[value.upper()])
                    elif key == "status":
                        setattr(task, key, Status(value))
                    else:
                        setattr(task, key, value)
            self.save_tasks()
            return True
        return False

    def list_tasks(self, filter_status: Optional[Status] = None):
        if filter_status:
            return [task for task in self.tasks if task.status == filter_status]
        return self.tasks

    def save_tasks(self):
        with open(self.filename, "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=2)

    def load_tasks(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                try:
                    tasks_data = json.load(f)
                    self.tasks = [Task.from_dict(data) for data in tasks_data]
                except json.JSONDecodeError:
                    self.tasks = []

    def search_tasks(self, keyword: str):
        keyword = keyword.lower()
        return [
            task for task in self.tasks
            if (keyword in task.title.lower() or 
                keyword in task.description.lower())
        ]

class TaskManagerUI:
    def __init__(self):
        self.manager = TaskManager()
        self.menu_options = {
            "1": ("Add New Task", self.add_task),
            "2": ("List All Tasks", self.list_tasks),
            "3": ("View Task Details", self.view_task),
            "4": ("Update Task", self.update_task),
            "5": ("Mark Task as Complete", self.mark_complete),
            "6": ("Delete Task", self.delete_task),
            "7": ("Search Tasks", self.search_tasks),
            "8": ("Filter Tasks by Status", self.filter_tasks),
            "9": ("Exit", self.exit_program)
        }

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_menu(self):
        self.clear_screen()
        print("""
╔══════════════════════════════╗
║       TASK MANAGER v1.0      ║
╚══════════════════════════════╝
""")
        for key, (option, _) in self.menu_options.items():
            print(f"{key}. {option}")
        print("\n")

    def get_user_input(self, prompt: str, input_type=str):
        while True:
            try:
                user_input = input(prompt).strip()
                if not user_input:
                    raise ValueError("Input cannot be empty")
                return input_type(user_input)
            except ValueError as e:
                print(f"Invalid input: {e}")

    def get_priority_input(self):
        print("\nPriority Levels:")
        for priority in Priority:
            print(f"{priority.value}. {priority.name}")
        while True:
            try:
                choice = int(input("Select priority (1-3): "))
                return Priority(choice)
            except (ValueError, KeyError):
                print("Invalid choice. Please enter 1, 2, or 3")

    def get_status_input(self):
        print("\nStatus Options:")
        for i, status in enumerate(Status, 1):
            print(f"{i}. {status.value}")
        while True:
            try:
                choice = int(input("Select status (1-3): "))
                return list(Status)[choice-1]
            except (ValueError, IndexError):
                print("Invalid choice. Please enter 1, 2, or 3")

    def get_date_input(self):
        while True:
            date_str = input("Due date (YYYY-MM-DD or leave blank): ").strip()
            if not date_str:
                return None
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")

    def add_task(self):
        self.clear_screen()
        print("╔══════════════════════════════╗")
        print("║         ADD NEW TASK         ║")
        print("╚══════════════════════════════╝\n")
        
        title = self.get_user_input("Title: ")
        description = self.get_user_input("Description: ")
        due_date = self.get_date_input()
        priority = self.get_priority_input()
        
        task = Task(title, description, due_date, priority)
        self.manager.add_task(task)
        print("\nTask added successfully!")
        input("\nPress Enter to continue...")

    def list_tasks(self, tasks: List[Task] = None):
        self.clear_screen()
        print("╔══════════════════════════════╗")
        print("║         TASK LISTING         ║")
        print("╚══════════════════════════════╝\n")
        
        tasks = tasks or self.manager.list_tasks()
        if not tasks:
            print("No tasks found.")
            input("\nPress Enter to continue...")
            return
        
        for i, task in enumerate(tasks, 1):
            status_color = ""
            if task.status == Status.COMPLETED:
                status_color = "\033[92m"  # Green
            elif task.status == Status.IN_PROGRESS:
                status_color = "\033[93m"  # Yellow
            else:
                status_color = "\033[91m"  # Red
                
            print(f"{i}. {task.title} - {status_color}{task.status.value}\033[0m")
            print(f"   Priority: {task.priority.name}")
            if task.due_date:
                print(f"   Due: {task.due_date}")
            print()
        
        input("\nPress Enter to continue...")

    def view_task(self):
        self.clear_screen()
        print("╔══════════════════════════════╗")
        print("║       TASK DETAIL VIEW       ║")
        print("╚══════════════════════════════╝\n")
        
        tasks = self.manager.list_tasks()
        if not tasks:
            print("No tasks available to view.")
            input("\nPress Enter to continue...")
            return
        
        self.list_tasks(tasks)
        try:
            task_num = int(input("\nEnter task number to view details: ")) - 1
            if 0 <= task_num < len(tasks):
                print("\n" + "═" * 50)
                print(tasks[task_num])
                print("═" * 50)
            else:
                print("Invalid task number.")
        except ValueError:
            print("Please enter a valid number.")
        
        input("\nPress Enter to continue...")

    def update_task(self):
        self.clear_screen()
        print("╔══════════════════════════════╗")
        print("║         UPDATE TASK          ║")
        print("╚══════════════════════════════╝\n")
        
        tasks = self.manager.list_tasks()
        if not tasks:
            print("No tasks available to update.")
            input("\nPress Enter to continue...")
            return
        
        self.list_tasks(tasks)
        try:
            task_num = int(input("\nEnter task number to update: ")) - 1
            if 0 <= task_num < len(tasks):
                task = tasks[task_num]
                print("\nCurrent Task Details:")
                print("═" * 50)
                print(task)
                print("═" * 50)
                
                print("\nEnter new values (leave blank to keep current):")
                title = input(f"Title [{task.title}]: ") or task.title
                description = input(f"Description [{task.description}]: ") or task.description
                due_date = self.get_date_input() or task.due_date
                priority = self.get_priority_input()
                status = self.get_status_input()
                
                self.manager.update_task(
                    task_num,
                    title=title,
                    description=description,
                    due_date=due_date,
                    priority=priority,
                    status=status
                )
                print("\nTask updated successfully!")
            else:
                print("Invalid task number.")
        except ValueError:
            print("Please enter a valid number.")
        
        input("\nPress Enter to continue...")

    def mark_complete(self):
        self.clear_screen()
        print("╔══════════════════════════════╗")
        print("║      MARK TASK COMPLETE      ║")
        print("╚══════════════════════════════╝\n")
        
        tasks = self.manager.list_tasks()
        if not tasks:
            print("No tasks available.")
            input("\nPress Enter to continue...")
            return
        
        # Show only pending/in-progress tasks
        incomplete_tasks = [t for t in tasks if t.status != Status.COMPLETED]
        if not incomplete_tasks:
            print("No incomplete tasks found.")
            input("\nPress Enter to continue...")
            return
        
        for i, task in enumerate(incomplete_tasks, 1):
            print(f"{i}. {task.title} - {task.status.value}")
        
        try:
            task_num = int(input("\nEnter task number to mark complete: ")) - 1
            if 0 <= task_num < len(incomplete_tasks):
                incomplete_tasks[task_num].mark_complete()
                self.manager.save_tasks()
                print("\nTask marked as complete!")
            else:
                print("Invalid task number.")
        except ValueError:
            print("Please enter a valid number.")
        
        input("\nPress Enter to continue...")

    def delete_task(self):
        self.clear_screen()
        print("╔══════════════════════════════╗")
        print("║         DELETE TASK          ║")
        print("╚══════════════════════════════╝\n")
        
        tasks = self.manager.list_tasks()
        if not tasks:
            print("No tasks available to delete.")
            input("\nPress Enter to continue...")
            return
        
        self.list_tasks(tasks)
        try:
            task_num = int(input("\nEnter task number to delete: ")) - 1
            if 0 <= task_num < len(tasks):
                if input(f"Are you sure you want to delete '{tasks[task_num].title}'? (y/n): ").lower() == 'y':
                    self.manager.delete_task(task_num)
                    print("\nTask deleted successfully!")
                else:
                    print("Deletion canceled.")
            else:
                print("Invalid task number.")
        except ValueError:
            print("Please enter a valid number.")
        
        input("\nPress Enter to continue...")

    def search_tasks(self):
        self.clear_screen()
        print("╔══════════════════════════════╗")
        print("║         SEARCH TASKS         ║")
        print("╚══════════════════════════════╝\n")
        
        keyword = input("Enter search keyword: ").strip()
        if not keyword:
            print("Please enter a search term.")
            input("\nPress Enter to continue...")
            return
        
        results = self.manager.search_tasks(keyword)
        if results:
            print(f"\nFound {len(results)} matching tasks:")
            self.list_tasks(results)
        else:
            print("\nNo tasks found matching your search.")
            input("\nPress Enter to continue...")

    def filter_tasks(self):
        self.clear_screen()
        print("╔══════════════════════════════╗")
        print("║       FILTER TASKS BY        ║")
        print("║          STATUS              ║")
        print("╚══════════════════════════════╝\n")
        
        status = self.get_status_input()
        filtered_tasks = self.manager.list_tasks(filter_status=status)
        
        if filtered_tasks:
            print(f"\n{len(filtered_tasks)} tasks with status '{status.value}':")
            self.list_tasks(filtered_tasks)
        else:
            print(f"\nNo tasks with status '{status.value}' found.")
            input("\nPress Enter to continue...")

    def exit_program(self):
        print("\nSaving tasks and exiting...")
        self.manager.save_tasks()
        sys.exit(0)

    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice: ").strip()
            
            if choice in self.menu_options:
                self.menu_options[choice][1]()
            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        ui = TaskManagerUI()
        ui.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting gracefully...")
        sys.exit(0)