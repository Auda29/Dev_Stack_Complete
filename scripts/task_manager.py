import argparse
import json
import sys
import os
from datetime import datetime

TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return {"tasks": [], "backlog": [], "metadata": {}}
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {TASKS_FILE} is corrupt.")
        sys.exit(1)


def save_tasks(data):
    data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Successfully updated {TASKS_FILE}")


def generate_id(tasks):
    # Simple auto-increment T-XXX
    existing_ids = [int(t['id'].split('-')[1]) for t in tasks if t['id'].startswith('T-')]
    if not existing_ids:
        next_id = 1
    else:
        next_id = max(existing_ids) + 1
    return f"T-{next_id:03d}"


def add_task(args):
    data = load_tasks()
    new_id = generate_id(data["tasks"])

    new_task = {
        "id": new_id,
        "title": args.title,
        "status": "TODO",
        "assigned": args.assigned,
        "priority": args.priority,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "dependencies": args.dependencies.split(',') if args.dependencies else [],
        "description": args.description,
        "acceptance_criteria": [],  # Simplified for CLI, agent can edit later
        "technical_notes": args.tech_notes,
        "files_changed": []
    }

    data["tasks"].insert(0, new_task)  # Add to top
    save_tasks(data)
    print(f"Created Task {new_id}")


def update_task(args):
    data = load_tasks()
    task = next((t for t in data["tasks"] if t["id"] == args.id), None)

    if not task:
        print(f"Error: Task {args.id} not found.")
        sys.exit(1)

    if args.status:
        task["status"] = args.status
    if args.assigned:
        task["assigned"] = args.assigned
    if args.priority:
        task["priority"] = args.priority

    save_tasks(data)
    print(f"Updated Task {args.id}")


def list_tasks(args):
    data = load_tasks()
    print(f"{'ID':<8} {'STATUS':<12} {'ASSIGNED':<15} {'TITLE'}")
    print("-" * 60)
    for t in data["tasks"]:
        print(f"{t['id']:<8} {t['status']:<12} {t['assigned']:<15} {t['title']}")


def main():
    parser = argparse.ArgumentParser(description="Task Manager CLI for Agents")
    subparsers = parser.add_subparsers(dest="command")

    # ADD
    add_parser = subparsers.add_parser("add", help="Create a new task")
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--assigned", default="Unassigned")
    add_parser.add_argument("--priority", default="Medium")
    add_parser.add_argument("--dependencies", help="Comma-separated IDs (e.g. T-001,T-002)")
    add_parser.add_argument("--description", default="")
    add_parser.add_argument("--tech_notes", default="")

    # UPDATE
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("id", help="Task ID (e.g. T-001)")
    update_parser.add_argument("--status", choices=["TODO", "WIP", "TESTING", "REVIEW", "APPROVED", "COMPLETED", "BLOCKED"])
    update_parser.add_argument("--assigned")
    update_parser.add_argument("--priority")

    # LIST
    subparsers.add_parser("list", help="List all tasks")

    args = parser.parse_args()

    if args.command == "add":
        add_task(args)
    elif args.command == "update":
        update_task(args)
    elif args.command == "list":
        list_tasks(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
