"""
OFFLINE PLANNER
No OpenAI dependency.
Deterministic and safe.
"""

class LLMPlanner:
    @staticmethod
    def generate_plan(command: str):
        text = command.lower()

        actions = []

        # Calendar intent
        if "meeting" in text or "schedule" in text:
            actions.append({
                "tool": "calendar.create_event",
                "parameters": {
                    "title": "Scheduled Meeting",
                    "description": command
                }
            })

        # Email intent
        if "email" in text or "mail" in text or "draft" in text:
            actions.append({
                "tool": "gmail.create_draft",
                "parameters": {
                    "to": "example@company.com",
                    "subject": "Automated Draft",
                    "body": f"Draft based on command: {command}"
                }
            })

        # Fallback
        if not actions:
            return {
                "status": "error",
                "message": "No executable action detected"
            }

        return {
            "status": "generated",
            "plan": {
                "goal": command,
                "actions": actions
            }
        }
