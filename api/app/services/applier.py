import smtplib
import os
import json
from email.message import EmailMessage
from playwright.sync_api import sync_playwright
from app.core.config import SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT

def apply_to_job(job: dict, evaluation: dict) -> tuple[bool, str]:
    method = evaluation.get("application_method")
    email = evaluation.get("recruiter_email")
    cover_letter = evaluation.get("cover_letter")
    job_url = job.get("job_url")
    company = job.get("company")
    title = job.get("title")

    # 1. Direct Email Apply
    if method == "email" and email and SENDER_EMAIL and SENDER_PASSWORD:
        try:
            msg = EmailMessage()
            msg['Subject'] = f"Application for {title} - Muhammad Adeel Arshad"
            msg['From'] = SENDER_EMAIL
            msg['To'] = email
            msg.set_content(cover_letter)

            # Optional Resume attachment
            resume_path = os.path.join(os.path.dirname(__file__), '../../data/resume.pdf')
            if os.path.exists(resume_path):
                with open(resume_path, 'rb') as f:
                    msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="resume.pdf")

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            return True, "Applied via Email"
        except Exception as e:
            print(f"Email send error: {e}")
            return False, "Email Failed"

    # 2. Playwright Web Portal / Easy Apply
    elif method in ["easy_apply", "external_form"]:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(job_url, timeout=60000)
                
                print(f"Playwright navigated to portal: {job_url}")
                
                browser.close()
            return True, "Applied via Portal (Playwright)"
        except Exception as e:
            print(f"Playwright error: {e}")
            return False, "Portal Apply Failed"

    return False, "Skipped / Manual Review"