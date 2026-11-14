import sqlite3, os, datetime
from modules.calendar_connector import authenticate_calendar

DB = os.path.join("config", "tasks.db")

def fix_calendar_auth():
    creds = authenticate_calendar()
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO tokens(service, token, created_at)
        VALUES('calendar', ?, ?)
    """, (creds.to_json(), datetime.datetime.now().isoformat()))
    con.commit()
    con.close()
    print("Calendar Token Stored with refresh_token ✔")

if __name__ == "__main__":
    fix_calendar_auth()
