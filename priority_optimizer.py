import sqlite3
import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier

class PriorityOptimizer:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.clf = None
        self.init_db()
        self.train_model()
        print("Priority Optimizer Ready ✔")

    def init_db(self):
        con = sqlite3.connect("config/assistant.db")
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS learning_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            intent TEXT,
            success INTEGER,
            timestamp TEXT,
            notes TEXT
        )""")
        con.commit()
        con.close()

    def load_logs(self):
        con = sqlite3.connect("config/assistant.db")
        cur = con.cursor()
        cur.execute("SELECT task, intent, success, timestamp, notes FROM learning_logs")
        rows = cur.fetchall()
        con.close()
        return rows

    def predict_priority(self, command):
        # Intent mapping rules
        if "urgent" in command.lower():
            return 1
        if "tomorrow" in command.lower():
            return 2
        if "schedule" in command.lower():
            return 3
        return 4

    def train_model(self):
        logs = self.load_logs()
        if not logs:
            return
        X = [self.model.encode(row[0]) for row in logs]
        y = [row[2] for row in logs]  # success flag as label
        self.clf = RandomForestClassifier()
        self.clf.fit(X, y)
