import sqlite3
import os
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
DB_PATH = os.path.join("modules", "assistant_tasks.db")

def init_exec_logs_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            parent_task TEXT,
            subtask TEXT,
            result TEXT
        )
    """)
    conn.commit()
    conn.close()
    return "Execution Logs Table Ready ✔"

class ExecutorAgent:
    @staticmethod
    def execute_plan(parent_task, subtasks):
        logs = []
        for sub in subtasks:
            # Simulated execution result
            result = "Executed successfully"
            logs.append((parent_task, sub, result))

            # Log each subtask execution to DB
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO execution_logs (timestamp, parent_task, subtask, result)
                VALUES (?,?,?,?)
            """, (datetime.now(IST).isoformat(), parent_task, sub, result))
            conn.commit()
            conn.close()

        return {"status": "executed", "logs": logs}

    @staticmethod
    def get_logs(limit=10):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        rows = cur.execute("SELECT timestamp, parent_task, subtask, result FROM execution_logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [
            {"timestamp": r[0], "parent_task": r[1], "subtask": r[2], "result": r[3]}
            for r in rows
        ]

# Self-test
if __name__ == "__main__":
    print(init_exec_logs_db())
    sample = ["Generate WBS", "Schedule Task", "Send Email"]
    print(ExecutorAgent.execute_plan("Demo Task", sample))
    print("Logs →", ExecutorAgent.get_logs())

