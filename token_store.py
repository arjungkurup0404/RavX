import sqlite3
import os
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
DB_PATH = "config/tokens.db"

def init_token_db():
    os.makedirs("config", exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS oauth_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        service TEXT,
        token TEXT,
        created_at TEXT
    )
    """)
    con.commit()
    con.close()
    return {"status": "initialized", "db": DB_PATH}

def save_token(user_email, service, token):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO oauth_tokens (user_email, service, token, created_at) VALUES (?, ?, ?, ?)",
                (user_email, service, token, datetime.now(IST).isoformat()))
    con.commit()
    con.close()
    return {"status": "saved", "service": service}

def get_token(user_email, service):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT token FROM oauth_tokens WHERE user_email=? AND service=?", (user_email, service))
    row = cur.fetchone()
    con.close()
    return row[0] if row else None

if __name__ == "__main__":
    print("Token Store DB Ready ✔")
    print(init_token_db())
