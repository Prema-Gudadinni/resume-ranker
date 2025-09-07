# app/send_email.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")  # e.g. "hr@company.com"

def send_shortlist_email(to_email: str, candidate_name: str, job_title: str, message: str):
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    subject = f"You've been shortlisted for {job_title}"
    content = f"Hi {candidate_name},\n\n{message}\n\nRegards,\nHiring Team"
    mail = Mail(from_email=FROM_EMAIL, to_emails=to_email, subject=subject, plain_text_content=content)
    resp = sg.send(mail)
    return resp.status_code, resp.body, resp.headers
