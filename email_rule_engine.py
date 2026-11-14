from .intent_classifier import classify_intent, parse_tasks
from .email_generator import EmailGenerator
from .notification_queue import queue_task
import sqlite3
import os
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
DB_PATH = os.path.join("modules", "assistant_tasks.db")

class EmailRuleEngine:
    @staticmethod
    def process(command, recipient="ops@enterprise.local"):
        # 1. Classify intent
        intent, conf = classify_intent(command)

        # 2. Parse high-level tasks
        tasks = parse_tasks(command)

        # 3. If email intent → generate draft + queue
        if intent == "email":
            task_obj = {"command": command, "intent": intent, "confidence": conf, "execute_at": None, "subtasks": tasks}
            draft = EmailGenerator.generate_email_from_task(task_obj, coordinator_name="Enterprise Ops")

            # queue email dispatch task
            queued = queue_task(command, "email", datetime.now(IST).isoformat())
            return {"draft": draft, "queue": queued}

        # 4. Otherwise queue normally
        queued = queue_task(command, intent, datetime.now(IST).isoformat())
        return {"queue": queued}

# Self-test
if __name__ == "__main__":
    print("Email Rule Engine Loaded ✔")
    print(EmailRuleEngine.process("Send invoice email to client urgently tomorrow"))

