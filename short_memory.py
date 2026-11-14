import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
import os

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
DB_PATH = os.path.join("modules", "agent_logs.db")  # reuse your log DB

def get_embedding(text):
    return MODEL.encode(text).tolist()

def init_memory_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS task_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            intent TEXT,
            embedding TEXT
        )
    """)
    conn.commit()
    conn.close()
    return "Short Memory Table Ready ✔"

def save_task(text, intent):
    emb = get_embedding(text)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO task_memory (task, intent, embedding) VALUES (?,?,?)",
                (text, intent, str(emb)))
    conn.commit()
    conn.close()
    return {"status": "saved", "task": text, "intent": intent}

def retrieve_similar(text, top_k=3):
    query_emb = np.array(get_embedding(text))
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    rows = cur.execute("SELECT task, intent, embedding FROM task_memory").fetchall()
    conn.close()

    scored = []
    for task, intent, emb_str in rows:
        emb = np.array(eval(emb_str))
        sim = (query_emb @ emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
        scored.append((sim, task, intent))

    scored.sort(reverse=True)
    return [{"task": t, "intent": i, "similarity": float(s)} for s, t, i in scored[:top_k]]

# Self-test
if __name__ == "__main__":
    print(init_memory_table())
    print(save_task("Prepare presentation slides", "todo"))
    print(save_task("Send invoice email to client", "email"))
    print("Similar →", retrieve_similar("Send invoice to client"))
