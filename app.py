import os, json, hmac, hashlib, base64, requests, sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlencode

from fastapi import FastAPI, Request, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse

from openai import OpenAI

# =====================================================
# ENV
# =====================================================
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SESSION_SECRET = os.getenv("SESSION_SECRET")

GOOGLE_REDIRECT_URI = "https://api.ravx.in/oauth/callback"
IST = ZoneInfo("Asia/Kolkata")
DB_PATH = "ravx.db"

# =====================================================
# APP
# =====================================================
app = FastAPI(title="RavX Phase 2 + Phase 3 (SQLite)")
@app.get("/")
def home():
    return {"message": "RavX backend is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ravx.in", "https://www.ravx.in"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# GPT
# =====================================================
client = OpenAI(api_key=OPENAI_API_KEY)

def ask_gpt(prompt: str) -> str:
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are RavX, a helpful personal AI assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )
    return res.choices[0].message.content.strip()

# =====================================================
# DATABASE (SQLite)
# =====================================================
def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            text TEXT,
            created DATE,
            due DATE,
            reminded INTEGER DEFAULT 0
        )
    """)
    db.commit()
    db.close()

init_db()

# =====================================================
# STATELESS SESSION
# =====================================================
def sign_session(data: dict) -> str:
    payload = json.dumps(data, separators=(",", ":"))
    sig = hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}.{sig}".encode()).decode()

def verify_session(token: str | None):
    if not token:
        return None
    try:
        decoded = base64.urlsafe_b64decode(token).decode()
        payload, sig = decoded.rsplit(".", 1)
        expected = hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        return json.loads(payload)
    except:
        return None

# =====================================================
# IN-MEMORY (SAFE TO KEEP)
# =====================================================
DRAFT_CACHE = {}  # temporary email drafts only

# =====================================================
# HEALTH
# =====================================================
@app.get("/health")
def health():
    return {"status": "ok"}

# =====================================================
# AUTH
# =====================================================
@app.get("/auth/google")
def auth_google():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": (
            "openid email profile "
            "https://www.googleapis.com/auth/gmail.readonly "
            "https://www.googleapis.com/auth/gmail.modify "
            "https://www.googleapis.com/auth/calendar.readonly "
            "https://www.googleapis.com/auth/calendar.events"
        ),
        "access_type": "offline",
        "prompt": "consent",
    }
    return RedirectResponse(
        "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    )

@app.get("/oauth/callback")
def oauth_callback(code: str):
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI,
        },
    )
    token_res.raise_for_status()
    tokens = token_res.json()

    userinfo = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": "Bearer " + tokens["access_token"]},
    ).json()

    response = RedirectResponse("https://ravx.in/chat")
    response.set_cookie(
        "ravx_session",
        sign_session({
            "name": userinfo["name"],
            "email": userinfo["email"],
            "access_token": tokens["access_token"],
        }),
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 30,
    )
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse("https://ravx.in")
    response.delete_cookie("ravx_session", secure=True, samesite="none")
    return response

# =====================================================
# UI
# =====================================================
@app.get("/web/chat", response_class=HTMLResponse)
def web_chat(ravx_session: str | None = Cookie(default=None)):
    user = verify_session(ravx_session)
    if not user:
        return RedirectResponse("https://api.ravx.in/auth/google")

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RavX Chat</title>

<style>
  :root {{
    --bg: #020617;          /* 🔁 CHANGE THIS to your website background */
    --panel: #020617;
    --primary: #2563eb;
    --bot: #1e293b;
    --text: #e5e7eb;
  }}

  body {{
    margin: 0;
    font-family: system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    height: 100vh;
  }}

  .container {{
    max-width: 900px;
    margin: auto;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }}

  /* HEADER */
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 20px;
    border-bottom: 1px solid #334155;
  }}

  .header span {{
    font-weight: 600;
  }}

  .header a {{
    color: var(--primary);
    text-decoration: none;
    font-size: 14px;
  }}

  /* MESSAGES */
  .messages {{
    flex: 1;
    padding: 20px;
    overflow-y: auto;
  }}

  .msg {{
    max-width: 70%;
    padding: 12px 14px;
    border-radius: 12px;
    margin-bottom: 14px;
    white-space: pre-wrap;
    line-height: 1.4;
    font-size: 14px;
  }}

  .user {{
    background: var(--primary);
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
  }}

  .bot {{
    background: var(--bot);
    color: var(--text);
    margin-right: auto;
    border-bottom-left-radius: 4px;
  }}

  /* INPUT AREA */
  .input-area {{
    border-top: 1px solid #334155;
    padding: 14px;
    background: var(--panel);
  }}

  .input-box {{
    display: flex;
    gap: 10px;
    align-items: center;
  }}

  textarea {{
    flex: 1;
    resize: none;
    background: #020617;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px;
    color: white;
    font-size: 14px;
    outline: none;
  }}

  button {{
    background: var(--primary);
    border: none;
    color: white;
    padding: 8px 14px;
    border-radius: 8px;
    cursor: pointer;
  }}

  /* PLUS MENU */
  .plus {{
    background: #020617;
    border: 1px solid #334155;
    color: white;
  }}

  .menu {{
    display: none;
    position: absolute;
    bottom: 80px;
    background: #020617;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px;
  }}

  .menu div {{
    padding: 8px;
    cursor: pointer;
  }}

  .menu div:hover {{
    background: #1e293b;
  }}
</style>
</head>

<body>
<div class="container">

  <!-- HEADER -->
  <div class="header">
    <span>Welcome, {user['name']}</span>
    <a href="/logout">Logout</a>
  </div>

  <!-- MESSAGES -->
  <div class="messages" id="messages"></div>

  <!-- INPUT -->
  <div class="input-area">
    <div class="input-box">
      <button class="plus" onclick="toggleMenu()">+</button>
      <textarea id="input" rows="2" placeholder="Message RavX..."></textarea>
      <button onclick="send()">Send</button>
    </div>
    <div class="menu" id="menu"></div>
  </div>

</div>

<script>
const input = document.getElementById("input");
const messages = document.getElementById("messages");
const menu = document.getElementById("menu");

const FEATURES = [
  "Summarize my recent emails",
  "Draft a professional email reply",
  "What are my tasks today?",
  "Show my upcoming deadlines",
  "Schedule a meeting tomorrow at 11",
  "Help me plan my day"
];

FEATURES.forEach(f => {{
  const item = document.createElement("div");
  item.innerText = f;
  item.onclick = () => {{
    input.value = f;
    input.focus();
    menu.style.display = "none";
  }};
  menu.appendChild(item);
}});

function toggleMenu() {{
  menu.style.display = menu.style.display === "block" ? "none" : "block";
}}

function addMessage(type, text) {{
  const div = document.createElement("div");
  div.className = "msg " + type;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}}

async function send() {{
  const text = input.value.trim();
  if (!text) return;

  addMessage("user", text);
  input.value = "";

  const res = await fetch("/agent/execute", {{
    method: "POST",
    headers: {{ "Content-Type": "application/json" }},
    body: JSON.stringify({{ message: text }})
  }});

  const d = await res.json();
  addMessage("bot", d.message);
}}

input.addEventListener("keydown", e => {{
  if (e.key === "Enter" && !e.shiftKey) {{
    e.preventDefault();
    send();
  }}
}});
</script>

</body>
</html>
"""


# =====================================================
# GMAIL HELPERS
# =====================================================
def get_unread_email_ids(token, max_results=25):
    r = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers={"Authorization": f"Bearer {token}"},
        params={"maxResults": max_results},
    )
    r.raise_for_status()
    return r.json().get("messages", [])

def get_email_content(token, mid):
    r = requests.get(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}",
        headers={"Authorization": f"Bearer {token}"},
        params={"format": "full"},
    )
    r.raise_for_status()
    msg = r.json()

    subject = sender = ""
    for h in msg["payload"].get("headers", []):
        if h["name"] == "Subject": subject = h["value"]
        if h["name"] == "From": sender = h["value"]

    return f"From: {sender}\nSubject: {subject}\n{msg.get('snippet','')}"

def send_email(token, to, subject, body):
    raw = f"To: {to}\nSubject: {subject}\n\n{body}"
    encoded = base64.urlsafe_b64encode(raw.encode()).decode()
    r = requests.post(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        headers={"Authorization": f"Bearer {token}"},
        json={"raw": encoded},
    )
    r.raise_for_status()

# =====================================================
# CALENDAR
# =====================================================
def parse_meeting_request(text):
    now = datetime.now(IST)
    day = now.date()
    if "tomorrow" in text:
        day += timedelta(days=1)

    hour, minute = 11, 0
    cleaned = text.lower().replace("am", "").replace("pm", "").replace("at", "")
    for w in cleaned.split():
        if ":" in w:
            try: hour, minute = map(int, w.split(":"))
            except: pass
        elif w.isdigit():
            hour = int(w)

    start = datetime.combine(day, datetime.min.time(), tzinfo=IST).replace(hour=hour, minute=minute)
    end = start + timedelta(minutes=30)
    return start.isoformat(), end.isoformat()

def create_calendar_event(token, start, end):
    r = requests.post(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "summary": "Scheduled Meeting",
            "start": {"dateTime": start},
            "end": {"dateTime": end},
        },
    )
    r.raise_for_status()

# =====================================================
# DEADLINES
# =====================================================
def parse_deadline(text):
    today = datetime.now(IST).date()
    t = text.lower()

    if "today" in t:
        return today
    if "tomorrow" in t:
        return today + timedelta(days=1)
    if "next week" in t:
        return today + timedelta(days=7)

    for part in t.split():
        try:
            return datetime.strptime(f"{part} {today.year}", "%d %b %Y").date()
        except:
            pass

    return None

# =====================================================
# AGENT
# =====================================================
@app.post("/agent/execute")
async def execute_agent(request: Request, ravx_session: str | None = Cookie(default=None)):
    user = verify_session(ravx_session)
    if not user:
        raise HTTPException(401)

    email = user["email"]
    token = user["access_token"]
    msg = (await request.json()).get("message", "").lower()
    today = datetime.now(IST).date()

    db = get_db()

    # ---- ADD TASK ----
    if msg.startswith("add task"):
        text = msg.replace("add task", "").strip()
        due = parse_deadline(text)

        db.execute(
            "INSERT INTO tasks (email, text, created, due) VALUES (?, ?, ?, ?)",
            (email, text, today.isoformat(), due.isoformat() if due else None)
        )
        db.commit()

        return {"message": f"📝 Task added" + (f" (due {due})" if due else "") + f": {text}"}

    # ---- TASKS TODAY ----
    if "tasks today" in msg or "my tasks" in msg:
        rows = db.execute(
            "SELECT text FROM tasks WHERE email=? AND created=?",
            (email, today.isoformat())
        ).fetchall()
        return {"message": "📋 Tasks today:\n" + "\n".join("• " + r[0] for r in rows)} if rows else {"message": "✅ No tasks today."}

    # ---- DEADLINES ----
    if "deadlines today" in msg:
        rows = db.execute(
            "SELECT text FROM tasks WHERE email=? AND due=?",
            (email, today.isoformat())
        ).fetchall()
        return {"message": "⏰ Deadlines today:\n" + "\n".join("• " + r[0] for r in rows)} if rows else {"message": "✅ No deadlines today."}

    if "deadlines" in msg:
        rows = db.execute(
            "SELECT text, due FROM tasks WHERE email=? AND due>? ",
            (email, today.isoformat())
        ).fetchall()
        return {"message": "📆 Upcoming deadlines:\n" + "\n".join(f"• {r[0]} → {r[1]}" for r in rows)} if rows else {"message": "✅ No upcoming deadlines."}

    # ---- GMAIL ----
    if msg in ["yes", "send it", "send email"]:
        draft = DRAFT_CACHE.get(email)
        if not draft:
            return {"message": "❌ No draft to send."}
        send_email(token, draft["to"], draft["subject"], draft["body"])
        del DRAFT_CACHE[email]
        return {"message": "✅ Email sent successfully."}

    if "reply" in msg or "draft" in msg:
        ids = get_unread_email_ids(token)
        if not ids:
            return {"message": "📭 No unread emails."}

        raw = get_email_content(token, ids[0]["id"])
        body = ask_gpt("Draft a polite professional reply:\n\n" + raw)

        to = raw.split("\n")[0].replace("From:", "").strip()
        subject = "Re: " + raw.split("Subject:")[-1].split("\n")[0].strip()
        DRAFT_CACHE[email] = {"to": to, "subject": subject, "body": body}

        return {"message": f"✉️ Draft reply:\n\n{body}\n\nSend it?"}

    # ---- CALENDAR ----
    if "schedule" in msg and "meeting" in msg:
        start, end = parse_meeting_request(msg)
        create_calendar_event(token, start, end)
        return {"message": "📅 Meeting scheduled successfully."}
    
    # ---- EMAIL SUMMARY ----
    if "summarize" in msg and "email" in msg:
        ids = get_unread_email_ids(token)
        if not ids:
            return {"message": "📭 No recent emails to summarize."}

        contents = []
        for m in ids:
            contents.append(get_email_content(token, m["id"]))

        summary = ask_gpt(
            "Summarize these emails clearly and concisely:\n\n" +
            "\n\n".join(contents)
        )

        return {"message": "📨 Email Summary:\n\n" + summary}


    return {"message": ask_gpt(msg)}
