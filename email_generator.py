import sqlite3
import os
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
DB_PATH = os.path.join("modules", "assistant_tasks.db")

class EmailGenerator:
    @staticmethod
    def generate_email_from_task(task, coordinator_name="Program Coordinator"):
        # Build email safely using existing keys from task
        subject = f"Automated Task Update: {task.get('intent','').title()}"
        body = f"""
Dear {coordinator_name},

The AI Assistant has analyzed and processed the following request:

Task: {task.get('command','').title()}
Identified Intent: {task.get('intent','')}
Confidence Score: {round(task.get('confidence',0), 2)}
Scheduled Execution Time: {task.get('execute_at') or 'Not specified'}

Generated Work Breakdown Structure:
""" + "\n".join([f"- {s}" for s in task.get('subtasks', [])]) + """

The request is queued in the automation pipeline and execution logs are stored for learning.

This email draft is system-generated and stored for future dispatch.

Regards,  
Autonomous AI Assistant System
"""
        body = body.strip()

        # Store draft in DB
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS email_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                subject TEXT,
                body TEXT,
                status TEXT
            )
        """)
        cur.execute("INSERT INTO email_drafts (timestamp, subject, body, status) VALUES (?,?,?,?)",
                    (datetime.now(IST).isoformat(), subject, body, "stored"))
        conn.commit()
        conn.close()

        return {"subject": subject, "body": body, "status": "stored"}

    @staticmethod
    def fetch_drafts(limit=5):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        rows = cur.execute("SELECT id, timestamp, subject, status FROM email_drafts ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return rows


if __name__ == "__main__":
    print("Email Generator Module Loaded ✔")
