import sqlite3
import os

DB_PATH = os.path.join("modules", "assistant_tasks.db")

def fetch_tasks(limit=20):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    rows = cur.execute("SELECT id, task, intent, execute_at, status FROM notifications ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [
        {"id": r[0], "task": r[1], "intent": r[2], "execute_at": r[3], "status": r[4]}
        for r in rows
    ]

def fetch_tasks_by_priority():
    # Priority sort based on urgency words + confidence
    tasks = fetch_tasks()
    urgency_words = ["urgent", "asap", "immediately", "deadline", "hour", "tomorrow", "today"]

    def score(t):
        s = 0
        for w in urgency_words:
            if w in t["task"].lower():
                s += 1
        # optional boost if dispatched soon
        if t["status"] == "queued":
            s += 0.5
        return s

    tasks.sort(key=lambda t: score(t), reverse=True)
    return tasks

# Self-test
if __name__ == "__main__":
    print("Dashboard Loaded ✔")
    print(fetch_tasks())
    print("Priority Sorted →", fetch_tasks_by_priority())

