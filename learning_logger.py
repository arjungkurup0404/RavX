import sqlite3
import datetime
import pytz

class LearningLogger:
    @staticmethod
    def init_db():
        con = sqlite3.connect("config/assistant.db")
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            intent TEXT,
            success INTEGER,
            timestamp TEXT,
            notes TEXT
        )
        """)
        con.commit()
        con.close()
        print("Learning Logs DB Initialized ✔")

    @staticmethod
    def log_result(task, intent, success, notes=""):
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.datetime.now(ist).isoformat()

        con = sqlite3.connect("config/assistant.db")
        cur = con.cursor()
        cur.execute("INSERT INTO learning_logs(task, intent, success, timestamp, notes) VALUES(?,?,?,?,?)",
                    (task, intent, int(success), now, notes))
        con.commit()
        con.close()

        return {"status": "logged", "task": task, "intent": intent, "success": success}
    
    @staticmethod
    def fetch_logs():
        con = sqlite3.connect("config/assistant.db")
        cur = con.cursor()
        cur.execute("SELECT task, intent, success, timestamp, notes FROM learning_logs ORDER BY id DESC")
        rows = cur.fetchall()
        con.close()

        logs = []
        for r in rows:
            t, i, s, ts, n = r
            logs.append({"task": t, "intent": i, "success": bool(s), "timestamp": ts, "notes": n})
        return logs
