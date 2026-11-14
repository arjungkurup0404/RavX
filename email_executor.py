import sqlite3
import os
from datetime import datetime
import pytz
from .planning_agent import PlanningAgent

IST = pytz.timezone("Asia/Kolkata")
DB_PATH = os.path.join("modules", "assistant_tasks.db")

class EmailExecutor:
    @staticmethod
    def draft_email(subject, body, recipient):
        return {
            "subject": subject,
            "body": body,
            "to": recipient,
            "created_at": datetime.now(IST).isoformat(),
            "status": "ready_to_send"
        }

    @staticmethod
    def send_email(task_command, recipient="team@company.com"):
        # 1. Generate plan
        plan = PlanningAgent.generate_plan(task_command)

        # 2. Create professional draft
        email = EmailExecutor.draft_email(
            subject="Automated Action: " + plan["intent"].title(),
            body="Task processed and queued by AI assistant.\n\nPlan → " + plan["plan"],
            recipient=recipient
        )

        # 3. Log to DB as dispatched
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notifications (created_at, task, intent, execute_at, status)
            VALUES (?,?,?,?,?)
        """, (datetime.now(IST).isoformat(), task_command, "email", datetime.now(IST).isoformat(), "dispatched"))
        conn.commit()
        conn.close()

        return {"analysis": plan, "email": email}

# Self test
if __name__ == "__main__":
    result = EmailExecutor.send_email("Send invoice email urgently tomorrow")
    print("Email Execution Module Loaded ✔")
    print(result)

