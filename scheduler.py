"""
Scheduler module.
ONLY defines scheduler-related functions.
NO code should execute automatically on import.
"""

from datetime import datetime
from modules.notification_queue import queue_task


def schedule_calendar_task(task_name: str, execute_at: str, user_id: str = None):
    """
    Schedules a calendar-related task for future execution.
    """
    task = {
        "task": task_name,
        "execute_at": execute_at,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat()
    }

    queue_task(task)
    return {
        "status": "scheduled",
        "task": task
    }
