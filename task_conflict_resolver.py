import sqlite3
import datetime
import pytz

class TaskConflictResolver:
    @staticmethod
    def init_db():
        con = sqlite3.connect("config/assistant.db")
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            intent TEXT,
            execute_at TEXT,
            priority INTEGER,
            status TEXT
        )
        """)
        con.commit()
        con.close()
        print("Conflict Resolver DB Initialized ✔")

    @staticmethod
    def resolve_conflicts():
        con = sqlite3.connect("config/assistant.db")
        cur = con.cursor()
        cur.execute("SELECT id, task, execute_at FROM tasks WHERE status='queued'")
        rows = cur.fetchall()
        con.close()

        seen_times = {}
        conflicts = []

        for r in rows:
            tid, tname, texec = r
            if texec in seen_times:
                conflicts.append({
                    "task_1": seen_times[texec],
                    "task_2": tname,
                    "execute_at": texec,
                    "resolution": "rescheduled_task_2"
                })
            else:
                seen_times[texec] = tname

        if not conflicts:
            return {"status": "ok", "message": "No conflicts found ✔"}

        return conflicts
