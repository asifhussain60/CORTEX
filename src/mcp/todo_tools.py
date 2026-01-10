"""
CORTEX 6.0 - TODO MCP Tools

MCP tool wrappers for TODO Orchestrator operations.
Provides 5 MCP tools for task management with DAG dependencies.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List


def todo_create(
    title: str,
    description: str = "",
    workspace_root: str = ".",
    priority: str = "MEDIUM",
    tags: Optional[List[str]] = None,
    dependencies: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new TODO item.
    
    Args:
        title: TODO title
        description: TODO description
        workspace_root: Path to workspace (default: current directory)
        priority: Priority level (LOW, MEDIUM, HIGH, CRITICAL)
        tags: Optional list of tags
        dependencies: Optional list of dependent TODO IDs
    
    Returns:
        Created TODO with ID
    """
    try:
        # Use YAML-based fallback directly (orchestrator has complex deps)
        import uuid
        from datetime import datetime
        import yaml
        
        workspace = Path(workspace_root).resolve()
        todos_dir = workspace / "cortex-brain" / "tier1" / "todos"
        todos_dir.mkdir(parents=True, exist_ok=True)
        
        todo_id = f"todo-{uuid.uuid4().hex[:8]}"
        
        todo_data = {
            "id": todo_id,
            "title": title,
            "description": description,
            "status": "PENDING",
            "priority": priority,
            "tags": tags or [],
            "dependencies": dependencies or [],
            "created": datetime.now().isoformat()
        }
        
        todo_path = todos_dir / f"{todo_id}.yaml"
        with open(todo_path, 'w') as f:
            yaml.dump(todo_data, f, default_flow_style=False)
        
        return {
            "success": True,
            "todo_id": todo_id,
            "title": title,
            "status": "PENDING",
            "priority": priority
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def todo_list(
    workspace_root: str = ".",
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    List TODO items with optional filters.
    
    Args:
        workspace_root: Path to workspace (default: current directory)
        status: Optional filter by status (PENDING, IN_PROGRESS, COMPLETE)
        priority: Optional filter by priority
        tags: Optional filter by tags
    
    Returns:
        List of matching TODOs
    """
    try:
        import yaml
        
        workspace = Path(workspace_root).resolve()
        todos_dir = workspace / "cortex-brain" / "tier1" / "todos"
        
        if not todos_dir.exists():
            return {
                "success": True,
                "todos": [],
                "count": 0
            }
        
        todos = []
        for todo_file in todos_dir.glob("todo-*.yaml"):
            try:
                with open(todo_file) as f:
                    todo_data = yaml.safe_load(f)
                
                # Apply filters
                if status and todo_data.get("status") != status:
                    continue
                if priority and todo_data.get("priority") != priority:
                    continue
                if tags and not any(t in todo_data.get("tags", []) for t in tags):
                    continue
                
                todos.append({
                    "id": todo_data.get("id"),
                    "title": todo_data.get("title"),
                    "status": todo_data.get("status"),
                    "priority": todo_data.get("priority"),
                    "tags": todo_data.get("tags", [])
                })
            except Exception:
                continue
        
        return {
            "success": True,
            "todos": todos,
            "count": len(todos)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def todo_update(
    todo_id: str,
    workspace_root: str = ".",
    status: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing TODO item.
    
    Args:
        todo_id: TODO ID to update
        workspace_root: Path to workspace (default: current directory)
        status: New status
        title: New title
        description: New description
        priority: New priority
    
    Returns:
        Updated TODO status
    """
    try:
        import yaml
        from datetime import datetime
        
        workspace = Path(workspace_root).resolve()
        todo_path = workspace / "cortex-brain" / "tier1" / "todos" / f"{todo_id}.yaml"
        
        if not todo_path.exists():
            return {
                "success": False,
                "error": f"TODO not found: {todo_id}"
            }
        
        with open(todo_path) as f:
            todo_data = yaml.safe_load(f)
        
        # Apply updates
        if status:
            todo_data["status"] = status
        if title:
            todo_data["title"] = title
        if description:
            todo_data["description"] = description
        if priority:
            todo_data["priority"] = priority
        
        todo_data["updated"] = datetime.now().isoformat()
        
        with open(todo_path, 'w') as f:
            yaml.dump(todo_data, f, default_flow_style=False)
        
        return {
            "success": True,
            "todo_id": todo_id,
            "status": todo_data["status"],
            "message": "TODO updated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def todo_complete(
    todo_id: str,
    workspace_root: str = "."
) -> Dict[str, Any]:
    """
    Mark a TODO item as complete.
    
    Args:
        todo_id: TODO ID to complete
        workspace_root: Path to workspace (default: current directory)
    
    Returns:
        Completion status
    """
    return todo_update(todo_id, workspace_root=workspace_root, status="COMPLETE")


def todo_dependencies(
    todo_id: str,
    workspace_root: str = "."
) -> Dict[str, Any]:
    """
    Get dependencies for a TODO item (DAG analysis).
    
    Args:
        todo_id: TODO ID to analyze
        workspace_root: Path to workspace (default: current directory)
    
    Returns:
        Dependency information including blocking and blocked-by
    """
    try:
        import yaml
        
        workspace = Path(workspace_root).resolve()
        todo_path = workspace / "cortex-brain" / "tier1" / "todos" / f"{todo_id}.yaml"
        
        if not todo_path.exists():
            return {
                "success": False,
                "error": f"TODO not found: {todo_id}"
            }
        
        with open(todo_path) as f:
            todo_data = yaml.safe_load(f)
        
        dependencies = todo_data.get("dependencies", [])
        
        # Find TODOs blocked by this one
        blocked_by_me = []
        todos_dir = workspace / "cortex-brain" / "tier1" / "todos"
        if todos_dir.exists():
            for other_file in todos_dir.glob("todo-*.yaml"):
                try:
                    with open(other_file) as f:
                        other_data = yaml.safe_load(f)
                    if todo_id in other_data.get("dependencies", []):
                        blocked_by_me.append(other_data.get("id"))
                except Exception:
                    continue
        
        # Check if all dependencies are complete
        all_deps_complete = True
        for dep_id in dependencies:
            dep_path = todos_dir / f"{dep_id}.yaml"
            if dep_path.exists():
                with open(dep_path) as f:
                    dep_data = yaml.safe_load(f)
                if dep_data.get("status") != "COMPLETE":
                    all_deps_complete = False
                    break
        
        return {
            "success": True,
            "todo_id": todo_id,
            "dependencies": dependencies,
            "blocked_by_me": blocked_by_me,
            "can_start": all_deps_complete,
            "dependency_count": len(dependencies)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
