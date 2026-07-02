from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from email.message import EmailMessage

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
gmail_service = None


def init_gmail():
    global gmail_service
    if gmail_service is None:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )
        creds = flow.run_local_server(
            port=8080,
            success_message="Authorization completed. You may close this tab."
        )
        gmail_service = build("gmail", "v1", credentials=creds)


@app.route("/")
def home():
    return "Flask server is running"


@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    domain = data.get("domain")

    message_text = f"""Hi {name}
Thank you to confirmation you set {domain}.
My team members call you 24/hrs
"""

    message = EmailMessage()
    message.set_content(message_text)
    message["To"] = email
    message["From"] = "me"
    message["Subject"] = "Confirmation"

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    gmail_service.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()

    return jsonify({"status": "Email sent successfully"})


if __name__ == "__main__":
    print("Starting Flask server...")
    init_gmail()
    app.run(port=5000)
