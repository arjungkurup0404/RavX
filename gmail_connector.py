import os
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ===== CONFIG =====
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
TOKEN_PATH = "config/token.json"


def get_gmail_service():
    """
    Loads Gmail service using OAuth token created via Web OAuth.
    """
    if not os.path.exists(TOKEN_PATH):
        raise Exception("Google OAuth not completed. Visit /auth/google first.")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build("gmail", "v1", credentials=creds)


def create_draft(to: str, subject: str, body: str):
    """
    Creates a Gmail draft (does NOT send email).
    """
    service = get_gmail_service()

    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": encoded_message}},
    ).execute()

    return {
        "status": "draft_created",
        "draft_id": draft.get("id"),
    }
