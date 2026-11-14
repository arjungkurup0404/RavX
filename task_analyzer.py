from modules.intent_classifier import classify_intent, parse_tasks

def analyze_tasks(text):
    """Extract and classify tasks from input text."""
    return parse_tasks(text)
