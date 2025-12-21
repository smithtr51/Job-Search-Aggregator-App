"""
Simple in-memory progress tracker for background tasks.
"""

from datetime import datetime
from typing import Dict, Optional

# In-memory storage for task progress
_task_progress: Dict[str, dict] = {}


def create_task(task_id: str, task_type: str, total_items: int = 0):
    """Create a new task progress entry."""
    _task_progress[task_id] = {
        "task_id": task_id,
        "task_type": task_type,
        "status": "running",
        "progress": 0,
        "total": total_items,
        "current_item": "",
        "message": "Starting...",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "error": None,
    }


def update_task(
    task_id: str,
    progress: Optional[int] = None,
    total: Optional[int] = None,
    current_item: Optional[str] = None,
    message: Optional[str] = None,
    status: Optional[str] = None,
    error: Optional[str] = None,
):
    """Update task progress."""
    if task_id not in _task_progress:
        return
    
    task = _task_progress[task_id]
    
    if progress is not None:
        task["progress"] = progress
    if total is not None:
        task["total"] = total
    if current_item is not None:
        task["current_item"] = current_item
    if message is not None:
        task["message"] = message
    if status is not None:
        task["status"] = status
        if status in ["completed", "failed"]:
            task["completed_at"] = datetime.now().isoformat()
    if error is not None:
        task["error"] = error


def get_task(task_id: str) -> Optional[dict]:
    """Get task progress."""
    return _task_progress.get(task_id)


def complete_task(task_id: str, message: str = "Completed"):
    """Mark task as completed."""
    update_task(task_id, status="completed", message=message)


def fail_task(task_id: str, error: str):
    """Mark task as failed."""
    update_task(task_id, status="failed", error=error)


def get_all_tasks() -> list:
    """Get all task progress entries."""
    return list(_task_progress.values())

