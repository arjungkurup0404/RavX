import sqlite3
import os
import time
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
DB_PATH = os.path.join("modules", "assistant_tasks.db")

class TaskMonitor:
    @staticmethod
    def get_due_tasks():
        now = datetime.now(IST).isoformat()
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        rows = cur.execute("SELECT id, task, intent, execute_at, status FROM notifications WHERE status='queued'").fetchall()
        conn.close()

        due = []
        for r in rows:
            task_id, task, intent, execute_at, status = r
            # If execution time is set and is <= now, mark due
            if execute_at and execute_at <= now:
                due.append({"id": task_id, "task": task, "intent": intent, "execute_at": execute_at})
            # If no time is set, still consider for manual/AI trigger later
            if not execute_at:
                due.append({"id": task_id, "task": task, "intent": intent, "execute_at": None})
        return due

    @staticmethod
    def mark_executed(task_id):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE notifications SET status=? WHERE id=?", ("executed", task_id))
        conn.commit()
        conn.close()
        return {"id": task_id, "status": "executed"}

    @staticmethod
    def log_execution(parent_task, subtask, result):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO execution_logs (timestamp, parent_task, subtask, result)
            VALUES (?,?,?,?)
        """, (datetime.now(IST).isoformat(), parent_task, subtask, result))
        conn.commit()
        conn.close()

    @staticmethod
    def run_monitor_loop(interval_sec=30):
        print("Task Monitor Running (Local Mode) ✔")
        while True:
            due_tasks = TaskMonitor.get_due_tasks()
            if due_tasks:
                print("\nDue Tasks Found →", due_tasks)
                for t in due_tasks:
                    TaskMonitor.mark_executed(t["id"])
                    # Log a simulated execution result
                    TaskMonitor.log_execution(t["task"], "WBS Execution", "Triggered by Task Monitor")
            else:
                print("\nNo due tasks at", datetime.now(IST).isoformat())

            time.sleep(interval_sec)

# Self test
if __name__ == "__main__":
    print("Task Monitor Module Loaded ✔")
