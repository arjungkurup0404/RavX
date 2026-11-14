from sentence_transformers import SentenceTransformer
from modules.intent_classifier import classify_intent

# Load lightweight semantic embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text: str):
    """Generate embedding vector for email text"""
    return embed_model.encode(text)

class EmailAgent:
    """
    Enterprise-grade email understanding agent
    (Gmail API integration will be added later)
    """
    def analyze(self, email_text: str):
        """Analyze email semantics and detect intent"""
        intent = classify_intent(email_text)
        vector = embed(email_text)

        return {
            "status": "analyzed",
            "intent": intent,
            "embedding_dim": len(vector),
            "preview": email_text[:120] + "..." if len(email_text) > 120 else email_text
        }

    def process(self, email_text: str):
        """
        Placeholder for future automation execution.
        Currently performs semantic analysis only.
        """
        analysis = self.analyze(email_text)
        return {**analysis, "action": "pending_automation_rules"}

# Expose class for module import
EmailAgent = EmailAgent
