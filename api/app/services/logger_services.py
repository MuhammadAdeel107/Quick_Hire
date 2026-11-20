import sqlite3
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

DB_PATH = "db/tracker.db"

def init_db():
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applied_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_url TEXT UNIQUE,
            company TEXT,
            title TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def is_job_applied(job_url: str) -> bool:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM applied_jobs WHERE job_url = ?", (job_url,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def log_application(job_url: str, company: str, title: str, score: int, method: str, status: str):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO applied_jobs (job_url, company, title, status) VALUES (?, ?, ?, ?)",
                   (job_url, company, title, status))
    conn.commit()
    conn.close()

    # Google Sheets Logging
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_path = os.path.join(os.path.dirname(__file__), 'api/credentials/service_account.json')
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Job_Applications_Tracker").sheet1
        sheet.append_row([company, title, job_url, score, method, status])
        print("Logged application to Google Sheets successfully.")
    except Exception as e:
        print(f"Google Sheets Log Error: {e}")