import sqlite3
import os

DB_PATH = os.path.join("config", "tasks.db")

def init_calendar_db():
    os.makedirs("config", exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Table for queued automation tasks (calendar/email/todo)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        intent TEXT NOT NULL,
        execute_at TEXT NOT NULL,
        priority INTEGER DEFAULT 3,
        status TEXT DEFAULT 'queued'
    )
    """)

    # Table for storing OAuth tokens (Gmail/Calendar)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT UNIQUE NOT NULL,
        token TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Calendar events log table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        start TEXT,
        end TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    con.commit()
    con.close()
    return "Calendar DB Initialized ✔"

if __name__ == "__main__":
    print(init_calendar_db())
