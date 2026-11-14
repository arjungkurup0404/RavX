from modules.calendar_connector import create_event
from modules.gmail_connector import create_draft
import datetime

def orchestrate_action(message: str, user_id: str):
    results = []

    if "meeting" in message.lower():
        results.append({
            "tool": "calendar",
            "result": create_event(
                title="Scheduled Meeting",
                description=message
            )
        })

    if "email" in message.lower():
        results.append({
            "tool": "gmail",
            "result": create_draft(
                to="example@company.com",
                subject="Automated Draft",
                body=f"Draft based on command: {message}"
            )
        })

    return {
        "time": datetime.datetime.utcnow().isoformat(),
        "message": message,
        "results": results
    }
