import argparse
import json
import sys
import os
from datetime import datetime

# Dynamic path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
TASKS_FILE = os.path.join(REPO_ROOT, "tasks.json")
VALID_STATUSES = ["TODO", "WIP", "TESTING", "REVIEW", "APPROVED", "COMPLETED", "BLOCKED", "REJECTED"]
VALID_AGENTS = ["Taskmaster", "Dev1", "Dev2", "Testing", "Review", "DevOps", "Unassigned"]


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
    
    # Atomic write to prevent race conditions
    temp_file = TASKS_FILE + ".tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        os.replace(temp_file, TASKS_FILE)
        print(f"Successfully updated {TASKS_FILE}")
    except Exception as e:
        print(f"Error saving tasks: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)


def generate_id(tasks):
    # Find the highest existing ID to prevent collisions
    existing_ids = []
    for t in tasks:
        if t['id'].startswith('T-'):
            try:
                existing_ids.append(int(t['id'].split('-')[1]))
            except ValueError:
                continue
    
    if not existing_ids:
        next_id = 1
    else:
        next_id = max(existing_ids) + 1
    return f"T-{next_id:03d}"


def add_task(args):
    if args.assigned not in VALID_AGENTS:
        print(f"Error: Invalid agent '{args.assigned}'. Valid agents: {', '.join(VALID_AGENTS)}")
        sys.exit(1)

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
        "technical_notes": args.technical_notes,
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
        if args.status not in VALID_STATUSES:
            print(f"Error: Invalid status '{args.status}'. Valid statuses: {', '.join(VALID_STATUSES)}")
            sys.exit(1)
        task["status"] = args.status
    if args.assigned:
        if args.assigned not in VALID_AGENTS:
            print(f"Error: Invalid agent '{args.assigned}'. Valid agents: {', '.join(VALID_AGENTS)}")
            sys.exit(1)
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


def generate_report(args):
    data = load_tasks()

    report = f"# Project Status Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    # By Status
    by_status = {}
    for t in data["tasks"]:
        s = t["status"]
        if s not in by_status:
            by_status[s] = []
        by_status[s].append(t)

    # Summary Table
    report += "## Summary\n\n"
    report += "| Status | Count |\n"
    report += "|--------|-------|\n"
    order = ["COMPLETED", "APPROVED", "REVIEW", "TESTING", "WIP", "TODO", "BLOCKED"]
    for status in order:
        count = len(by_status.get(status, []))
        report += f"| {status} | {count} |\n"
    report += "\n"

    for status in order:
        tasks = by_status.get(status, [])
        if tasks:
            report += f"## {status} ({len(tasks)})\n"
            for t in tasks:
                report += f"- **{t['id']}**: {t['title']} (Assigned: {t['assigned']})\n"
            report += "\n"

    # Backlog
    if data.get("backlog"):
        report += f"## Backlog ({len(data['backlog'])})\n"
        for item in data["backlog"]:
            report += f"- {item}\n"

    print(report)


def generate_html_report(args):
    data = load_tasks()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dev_Stack Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; border: 1px solid #e9ecef; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #6c757d; font-size: 14px; }}
            .task-list {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
            th {{ background: #f8f9fa; font-weight: 600; }}
            .status-badge {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
            .status-TODO {{ background: #e9ecef; color: #495057; }}
            .status-WIP {{ background: #fff3cd; color: #856404; }}
            .status-TESTING {{ background: #cce5ff; color: #004085; }}
            .status-REVIEW {{ background: #d4edda; color: #155724; }}
            .status-APPROVED {{ background: #d1ecf1; color: #0c5460; }}
            .status-COMPLETED {{ background: #d4edda; color: #155724; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Dev_Stack Dashboard</h1>
            <p>Last Updated: {timestamp}</p>
            
            <div class="stats">
    """
    
    # Stats
    by_status = {}
    for t in data["tasks"]:
        s = t["status"]
        if s not in by_status:
            by_status[s] = []
        by_status[s].append(t)
        
    order = ["COMPLETED", "APPROVED", "REVIEW", "TESTING", "WIP", "TODO"]
    for status in order:
        count = len(by_status.get(status, []))
        html += f"""
            <div class="stat-card">
                <div class="stat-value">{count}</div>
                <div class="stat-label">{status}</div>
            </div>
        """
        
    html += """
            </div>
            
            <h2>Active Tasks</h2>
            <table class="task-list">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Status</th>
                        <th>Assigned</th>
                        <th>Title</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for t in data["tasks"]:
        html += f"""
            <tr>
                <td>{t['id']}</td>
                <td><span class="status-badge status-{t['status']}">{t['status']}</span></td>
                <td>{t['assigned']}</td>
                <td>{t['title']}</td>
            </tr>
        """
        
    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Generated dashboard.html")


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
    add_parser.add_argument("--technical-notes", default="", dest="technical_notes")

    # UPDATE
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("id", help="Task ID (e.g. T-001)")
    update_parser.add_argument("--status", choices=VALID_STATUSES)
    update_parser.add_argument("--assigned")
    update_parser.add_argument("--priority")

    # LIST
    subparsers.add_parser("list", help="List all tasks")

    # REPORT
    report_parser = subparsers.add_parser("report", help="Generate a status report")
    report_parser.add_argument("--html", action="store_true", help="Generate HTML dashboard")

    args = parser.parse_args()

    if args.command == "add":
        add_task(args)
    elif args.command == "update":
        update_task(args)
    elif args.command == "list":
        list_tasks(args)
    elif args.command == "report":
        if args.html:
            generate_html_report(args)
        else:
            generate_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
