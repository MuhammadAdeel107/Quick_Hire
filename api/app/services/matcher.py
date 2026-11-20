import os
import json
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from app.core.config import GEMINI_API_KEY

class JobMatchResult(BaseModel):
    match_score: int = Field(description="Match score between 0 and 100")
    application_method: str = Field(description="email, easy_apply, or external_form")
    recruiter_email: str | None = Field(description="Recruiter email if mentioned")
    cover_letter: str | None = Field(description="Tailored cover letter if score >= 75")

def evaluate_job(job_description: str, company: str, title: str) -> dict:
    profile_path = os.path.join(os.path.dirname(__file__), '../../data/profile.json')
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
    except:
        profile_data = {}

    prompt = f"""
    Evaluate the Job Description against the profile.
    Profile: {json.dumps(profile_data)}
    Job: {title} at {company}
    Description: {job_description}
    Calculate match_score (0-100), application_method ('email', 'easy_apply', 'external_form'), recruiter_email, and cover_letter (if score >= 75).
    """

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JobMatchResult,
                temperature=0.1
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Matching error: {e}")
        return {"match_score": 0, "application_method": "external_form", "recruiter_email": None, "cover_letter": None}