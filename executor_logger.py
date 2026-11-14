from datetime import datetime
from modules.tool_registry import ToolRegistry

def log_execution(user_message, plan, routed_tasks, results):
    log_entry = {
        "time": datetime.utcnow().isoformat(),
        "message": user_message,
        "allowed_tools": ToolRegistry.get_allowed_tools(),
        "plan": plan,
        "routed_tasks": routed_tasks,
        "results": results
    }

    print("AGENT LOG →", log_entry)
