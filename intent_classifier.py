from sentence_transformers import SentenceTransformer
import numpy as np
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

INTENT_LABELS = {
    "calendar": ["schedule meeting", "create event", "remind tomorrow", "plan meeting", "calendar event"],
    "email": ["send mail", "reply email", "draft email", "send invoice", "email response"],
    "todo": ["todo list", "remember task", "note this", "add to do", "list tasks"]
}

def classify_intent(text):
    query_emb = model.encode(text.lower())
    best_intent = None
    best_score = -1.0

    for intent, phrases in INTENT_LABELS.items():
        label_emb = model.encode(" ".join(phrases))
        score = (query_emb @ label_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(label_emb))
        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent, float(best_score)  # convert to normal float ✔

def parse_tasks(text):
    text = text.lower()
    if " and " in text:
        parts = text.split(" and ")
        return [p.strip().title() for p in parts]
    return [text.strip().title()]

if __name__ == "__main__":
    print(classify_intent("Schedule a meeting tomorrow"))
    print(parse_tasks("Buy milk and send mail to HR"))
