import re
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone("Asia/Kolkata")

def extract_time_reference(text):
    """Detects temporal keywords and converts to datetime"""
    text = text.lower()

    if "tomorrow" in text:
        t = datetime.now(IST) + timedelta(days=1)
        return t

    if "in" in text and "hour" in text:
        hrs = int(re.search(r"(\d+)", text).group())
        t = datetime.now(IST) + timedelta(hours=hrs)
        return t

    if "in" in text and "minute" in text:
        mins = int(re.search(r"(\d+)", text).group())
        t = datetime.now(IST) + timedelta(minutes=mins)
        return t

    # Date format like 2026-01-05 16:00:00
    date_match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", text)
    if date_match:
        return datetime.strptime(date_match.group(), "%Y-%m-%d %H:%M:%S")

    return None

def extract_actionable_task(text):
    """Classifies tasks into scheduling, email automation, or todo storage"""
    schedule_time = extract_time_reference(text)

    if schedule_time:
        return {
            "task_type": "scheduled_task",
            "title": re.sub(r"(schedule|set|remind|create)", "", text, flags=re.I).strip().title(),
            "execute_at": schedule_time.isoformat()
        }

    if any(keyword in text.lower() for keyword in ["send", "mail", "reply", "email"]):
        return {
            "task_type": "email_automation",
            "instruction": text,
            "status": "pending_email_rules"
        }

    return {
        "task_type": "todo_storage",
        "content": text,
        "status": "saved_for_later_processing"
    }

# Quick test
if __name__ == "__main__":
    print("Automation Engine Loaded ✔")
    print(extract_actionable_task("Schedule system demo tomorrow at 3PM"))
    print(extract_actionable_task("Send invoice mail"))
    print(extract_actionable_task("Buy flowers for gf"))
