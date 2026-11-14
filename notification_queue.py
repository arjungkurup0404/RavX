import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("db/notification_queue.db")

def init_queue_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            execute_at TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

def queue_task(task: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO task_queue (task, execute_at, created_at) VALUES (?, ?, ?)",
        (
            str(task),
            task.get("execute_at"),
            datetime.utcnow().isoformat()
        )
    )

    conn.commit()
    conn.close()
