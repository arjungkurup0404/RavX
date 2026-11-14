"""
Tool Registry
Defines which tools the agent is allowed to execute.
"""

class ToolRegistry:
    # 🔒 ALLOWED TOOLS ONLY
    ALLOWED_TOOLS = {
        "calendar.create_event": {
            "description": "Create calendar events / meetings"
        },
        "gmail.create_draft": {
            "description": "Create Gmail draft emails"
        }
    }

    @staticmethod
    def is_tool_allowed(tool_name: str) -> bool:
        return tool_name in ToolRegistry.ALLOWED_TOOLS

    @staticmethod
    def get_allowed_tools():
        return list(ToolRegistry.ALLOWED_TOOLS.keys())
