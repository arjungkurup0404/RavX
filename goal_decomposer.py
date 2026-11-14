from .intent_classifier import classify_intent
from .short_memory import retrieve_similar
from .planning_agent import PlanningAgent
from .executor_agent import ExecutorAgent
import sqlite3
import os
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
DB_PATH = os.path.join("modules", "assistant_tasks.db")

class GoalDecomposer:
    @staticmethod
    def decompose_and_execute(command):
        # 1. Classify intent
        intent, conf = classify_intent(command)

        # 2. Retrieve similar historical tasks
        similar = retrieve_similar(command)

        # 3. Generate a structured WBS plan using planner
        plan = PlanningAgent.generate_plan(command)

        # 4. Extract only the WBS steps (text chain) and split into list
        raw_plan = plan["plan"]
        steps = [s.strip() for s in raw_plan.split("→")]

        # 5. Execute plan + log results
        execution = ExecutorAgent.execute_plan(command, steps)

        return {
            "status": "completed",
            "intent": intent,
            "confidence": round(conf, 2),
            "similar_tasks": similar,
            "generated_plan": steps,
            "execution_logs": execution["logs"]
        }

# Self-test
if __name__ == "__main__":
    print("Goal Decomposer Loaded ✔")
    print(GoalDecomposer.decompose_and_execute("Prepare sprint report and send email urgently tomorrow"))
