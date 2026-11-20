import os
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class SheetsLogger:
    from pathlib import Path

    def __init__(self, sheet_name: str = "Job_Applications_Tracker"):
        # api/ folder ke andar se credentials/service_account.json ka exact path
        base_dir = Path(__file__).resolve().parent.parent.parent  # QuickHire/api/ folder tak
        self.creds_path = base_dir / "credentials" / "service_account.json"
        self.sheet_name = sheet_name
        self.sheet = None
        
        if self.creds_path.exists():
            self._authenticate()
        else:
            print(f"[WARNING] Service account file not found at {self.creds_path}. Skipping Google Sheets sync.")
            
    def _authenticate(self):
        try:
            creds = Credentials.from_service_account_file(str(self.creds_path), scopes=SCOPES)
            client = gspread.authorize(creds)
            self.sheet = client.open(self.sheet_name).sheet1
            
            # Agar sheet bilkul khali ho toh headers add kar dena
            if not self.sheet.row_values(1):
                headers = ["Date", "Company", "Role", "Location", "Match Score", "Method", "Status", "Job URL", "Notes"]
                self.sheet.append_row(headers)
        except Exception as e:
            print(f"[GOOGLE SHEETS ERROR] Authentication failed: {e}")

    def log_application(self, company: str, role: str, location: str, match_score: int, method: str, status: str, job_url: str, notes: str = ""):
        if not self.sheet:
            return
        try:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                company,
                role,
                location,
                f"{match_score}%",
                method,
                status,
                job_url,
                notes
            ]
            self.sheet.append_row(row)
            print("Logged application to Google Sheets successfully.")
        except Exception as e:
            print(f"Google Sheets Log Error: {e}")