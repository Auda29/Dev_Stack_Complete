import json
import sys

# Configuration
TASKS_JSON = "tasks.json"
OUTPUT_MD = "docs/tasks.md"


def load_tasks():
    with open(TASKS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def render_header(metadata):
    return """# Tasks Documentation

This document is the **source of truth** for all tasks in the Dev_Stack system.
**NOTE:** This file is AUTO-GENERATED from `tasks.json`. Do not edit manually.

---

## Task Status Legend

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `TODO` | Not started | Awaiting assignment |
| `WIP` | Work in progress | Agent is actively working |
| `TESTING` | Ready for testing | Testing agent should validate |
| `REVIEW` | Ready for code review | Review agent should check |
| `APPROVED` | Review passed | DevOps should merge |
| `COMPLETED` | Merged to dev | Task finished |
| `BLOCKED` | Cannot proceed | Resolve blocker first |
| `REJECTED` | Does not meet standards | Needs rework |

---

## Active Tasks

"""


def render_task(task):
    # Determine if task is completed to hide it from active list or show in archive
    # For now, we render all tasks in the list, but you could filter.

    deps = ", ".join(task.get("dependencies", [])) if task.get("dependencies") else "None"

    md = f"""### {task['id']}: {task['title']}

**Status**: {task['status']}
**Assigned**: {task['assigned']}
**Priority**: {task.get('priority', 'Medium')}
**Created**: {task.get('created', '')}
**Dependencies**: {deps}

**Description**:
{task.get('description', '')}

**Acceptance Criteria**:
"""

    for criteria in task.get('acceptance_criteria', []):
        checked = "x" if criteria.get('completed') else " "
        md += f"- [{checked}] {criteria['description']}\n"

    md += f"""
**Technical Notes**:
{task.get('technical_notes', '')}

**Files Changed**:
"""
    for f in task.get('files_changed', []):
        md += f"- {f}\n"

    md += "\n---\n\n"
    return md


def render_backlog(backlog):
    md = "## Backlog\n\nIdeas and future tasks that are not yet scheduled:\n\n"
    for item in backlog:
        md += f"- {item}\n"
    md += "\n---\n\n"
    return md


def render_footer(metadata):
    return f"""## Notes

- Always update `tasks.json` when task status changes
- Keep descriptions clear and actionable
- Link related tasks
- Document blockers immediately

---

**Last Updated**: {metadata.get('last_updated', '')}
**Maintained By**: {metadata.get('maintained_by', '')}
"""


def main():
    try:
        data = load_tasks()

        markdown = render_header(data.get("metadata", {}))

        # Sort tasks: Active first, then Completed
        tasks = data.get("tasks", [])

        # In a real scenario, you might want to separate completed tasks into an archive section
        for task in tasks:
            markdown += render_task(task)

        markdown += render_backlog(data.get("backlog", []))
        markdown += render_footer(data.get("metadata", {}))

        with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"Successfully generated {OUTPUT_MD}")

    except Exception as e:
        print(f"Error generating markdown: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
