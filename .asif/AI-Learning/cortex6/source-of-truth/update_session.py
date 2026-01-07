#!/usr/bin/env python3
"""
CORTEX 6.0 Build Session Manager
================================
Manages session state, audit logging, and plan viewer updates for GitHub Copilot execution.

Usage:
    python3 update_session.py --task-complete "task-1.1.5" --message "Created smoke tests"
    python3 update_session.py --refresh-viewer
    python3 update_session.py --session-end

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
SOURCE_OF_TRUTH = SCRIPT_DIR
TODO_TRACKER = SOURCE_OF_TRUTH / "todo" / "00-TODO-CONTINUITY-TRACKER.yaml"
PLAN_VIEWER = SOURCE_OF_TRUTH / "plan-viewer.html"
AUDIT_LOG_DIR = Path(__file__).parent.parent.parent.parent.parent / "cortex-brain" / "audit-logs"
SESSION_LOG = SOURCE_OF_TRUTH / "session-audit.jsonl"


def log_audit(operation: str, message: str, context: dict = None):
    """Log audit entry to session log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "category": "BUILD_EXECUTION",
        "component": "github_copilot",
        "operation": operation,
        "message": message,
        "context": context or {},
        "executor": "GitHub Copilot"
    }
    
    with open(SESSION_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✅ Audit logged: {operation} - {message}")


def update_tracker_position(task_id: str, status: str = "COMPLETED"):
    """Update the TODO tracker with new position."""
    if not TODO_TRACKER.exists():
        print(f"❌ Tracker not found: {TODO_TRACKER}")
        return False
    
    content = TODO_TRACKER.read_text()
    
    # Parse current position
    match = re.search(r'current_position:\s*\n\s*feature:\s*"([^"]+)"\s*\n\s*phase:\s*(\d+)\s*\n\s*task:\s*"([^"]+)"', content)
    if match:
        current_feature = match.group(1)
        current_phase = int(match.group(2))
        current_task = match.group(3)
        
        # Update last_completed
        content = re.sub(
            r'(last_completed:\s*)"[^"]*"',
            f'\\1"{task_id}"',
            content
        )
        
        # Update completed_count
        count_match = re.search(r'completed_count:\s*(\d+)', content)
        if count_match:
            new_count = int(count_match.group(1)) + 1
            content = re.sub(
                r'completed_count:\s*\d+',
                f'completed_count: {new_count}',
                content
            )
        
        # Calculate next task
        task_parts = task_id.split("-")
        if len(task_parts) >= 2:
            task_num = task_parts[-1]
            parts = task_num.split(".")
            if len(parts) >= 3:
                next_minor = int(parts[2]) + 1
                next_task = f"task-{parts[0]}.{parts[1]}.{next_minor}"
                content = re.sub(
                    r'(task:\s*)"[^"]+"',
                    f'\\1"{next_task}"',
                    content
                )
        
        TODO_TRACKER.write_text(content)
        print(f"✅ Tracker updated: {task_id} → {status}")
        return True
    
    print("❌ Could not parse current position")
    return False


def calculate_progress():
    """Calculate overall progress from tracker."""
    if not TODO_TRACKER.exists():
        return 0, {}
    
    content = TODO_TRACKER.read_text()
    
    # Count completed vs total tasks
    completed = len(re.findall(r'status:\s*COMPLETED', content))
    total = len(re.findall(r'id:\s*"task-', content))
    
    progress = int((completed / total * 100)) if total > 0 else 0
    
    return progress, {
        "completed": completed,
        "total": total,
        "in_progress": 1,  # Current task
        "blocked": max(0, total - completed - 1)
    }


def refresh_plan_viewer():
    """Update the plan viewer with current progress."""
    if not PLAN_VIEWER.exists():
        print(f"❌ Plan viewer not found: {PLAN_VIEWER}")
        return False
    
    progress, stats = calculate_progress()
    
    content = PLAN_VIEWER.read_text()
    
    # Update progress percentage
    content = re.sub(
        r'progress:\s*\d+',
        f'progress: {progress}',
        content
    )
    
    # Update stroke-dashoffset for progress ring (circumference = 364.42, radius = 58)
    circumference = 364.42
    offset = circumference - (progress / 100) * circumference
    content = re.sub(
        r'stroke-dashoffset="[\d.]+"',
        f'stroke-dashoffset="{offset:.2f}"',
        content,
        count=1
    )
    
    # Update progress text
    content = re.sub(
        r'<span class="progress-percent" id="progress-percent">\d+%</span>',
        f'<span class="progress-percent" id="progress-percent">{progress}%</span>',
        content
    )
    
    # Update generation timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = re.sub(
        r'Generated 2026-01-07',
        f'Updated {now}',
        content
    )
    
    PLAN_VIEWER.write_text(content)
    print(f"✅ Plan viewer refreshed: {progress}% complete")
    return True


def end_session():
    """End current session and prepare for continuation."""
    log_audit("session_end", "GitHub Copilot session ended", {
        "timestamp": datetime.now().isoformat()
    })
    
    # Update session info in tracker
    if TODO_TRACKER.exists():
        content = TODO_TRACKER.read_text()
        content = re.sub(
            r'(ended_at:\s*)null',
            f'\\1"{datetime.now().isoformat()}"',
            content
        )
        TODO_TRACKER.write_text(content)
    
    refresh_plan_viewer()
    print("\n📋 Session ended. To continue, use CONTINUATION-PROMPT.md")


def main():
    parser = argparse.ArgumentParser(description="CORTEX 6.0 Build Session Manager")
    parser.add_argument("--task-complete", help="Mark a task as complete")
    parser.add_argument("--message", help="Completion message for audit log")
    parser.add_argument("--refresh-viewer", action="store_true", help="Refresh plan viewer")
    parser.add_argument("--session-end", action="store_true", help="End current session")
    parser.add_argument("--log", help="Log custom audit entry")
    
    args = parser.parse_args()
    
    if args.task_complete:
        message = args.message or f"Completed {args.task_complete}"
        log_audit("task_complete", message, {"task_id": args.task_complete})
        update_tracker_position(args.task_complete)
        refresh_plan_viewer()
    
    elif args.refresh_viewer:
        refresh_plan_viewer()
    
    elif args.session_end:
        end_session()
    
    elif args.log:
        log_audit("manual_log", args.log)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
