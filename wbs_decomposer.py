from .short_memory import retrieve_similar
from .intent_classifier import classify_intent
from .intent_classifier import classify_intent, parse_tasks
import numpy as np
import re
from datetime import datetime, timedelta
import pytz
import sqlite3
import os

IST = pytz.timezone("Asia/Kolkata")
MODEL = "all-MiniLM-L6-v2"
from sentence_transformers import SentenceTransformer
model = SentenceTransformer(MODEL)

def extract_time_reference(text):
    text = text.lower()
    if "tomorrow" in text:
        t = datetime.now(IST) + timedelta(days=1)
        return t.replace(hour=16, minute=0, second=0, microsecond=0)
    hour_match = re.search(r"in (\d+) hour", text)
    if hour_match:
        return datetime.now(IST) + timedelta(hours=int(hour_match.group(1)))
    minute_match = re.search(r"in (\d+) minute", text)
    if minute_match:
        return datetime.now(IST) + timedelta(minutes=int(minute_match.group(1)))
    return None

def priority_score(task):
    urgency_words = ["urgent", "asap", "immediately", "tomorrow", "today", "deadline", "hour", "minute"]
    score = 0
    t = task.lower()
    for w in urgency_words:
        if w in t:
            score += 1
    return score

def decompose_task(command):
    intent_conf, confidence = classify_intent(command)
    time_ref = extract_time_reference(command)
    tasks = parse_tasks(command)

    subtasks = [
        "Recognize intent and goal",
        "Retrieve similar historical tasks from memory",
        "Generate WBS hierarchical structure",
        "Apply temporal constraints",
        "Compute urgency and priority score",
        "Map required tools and resources",
        "Generate execution sequence",
        "Store execution logs for learning"
    ]

    # semantic branching
    lower = command.lower()
    if "meeting" in lower:
        subtasks += ["Calendar interface triggered", "Meeting title drafted", "Reminder notification queued"]
    if "email" in lower or "send" in lower:
        subtasks += ["Email automation engine triggered", "Professional email drafted", "Email queued for dispatch"]
    if "todo" in lower or "remember" in lower or "task" in lower:
        subtasks += ["Saved to todo memory", "Queued for future scheduling"]

    # decomposition relevance score
    sub_emb = model.encode(" ".join(subtasks))
    cmd_emb = model.encode(command.lower())
    sim = float((cmd_emb @ sub_emb) / (np.linalg.norm(cmd_emb) * np.linalg.norm(sub_emb)))

    return {
        "command": command,
        "intent": intent_conf,
        "confidence": confidence,
        "tasks_detected": tasks,
        "decomposition_relevance": round(sim, 2),
        "execute_at": time_ref.isoformat() if time_ref else None,
        "priority": priority_score(command),
        "subtasks": subtasks
    }

# Self test
if __name__ == "__main__":
    print("WBS Decomposer Loaded ✔")
    print(decompose_task("Send invoice email urgently tomorrow"))
