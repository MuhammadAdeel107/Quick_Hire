import time
import pandas as pd
from jobspy import scrape_jobs
from app.services.logger_services import is_job_applied

def fetch_all_ai_jobs(results_wanted_per_query=3):
    search_terms = [
        "AI Engineer",
        "Agentic Ai",
        "Agentic Ai Intern",
        "Artificial Intelligence",
        "Artificial Intelligence Intern",
        "Generative Ai",
        "Generative Ai Intern",
        "Machine Learning Engineer",
        "Machine Learning Intern",
        "Python AI Developer",
        "Python Intern",
        "Python Developer",
        "LLM Engineer",
        "RAG Developer"
    ]
    
    locations = [
        "Lahore",
        "Islamabad",
        "Faisalabad",
        "Remote"
    ]
    
    all_fresh_jobs = []
    seen_urls = set()
    
    for search_term in search_terms:
        for location in locations:
            print(f"Scraping fresh jobs for: '{search_term}' in '{location}'...")
            time.sleep(5)
            try:
                jobs_df = scrape_jobs(
                    site_name=["linkedin", "indeed", "glassdoor"],
                    search_term=search_term,
                    location=location,
                    results_wanted=results_wanted_per_query,
                    hours_old=24
                    # country_indeed parameter yahan se hata diya gaya hai taake error na aaye
                )
                
                if jobs_df is None or jobs_df.empty:
                    continue

                for _, row in jobs_df.iterrows():
                    job_url = row.get("job_url")
                    
                    if job_url and job_url not in seen_urls and not is_job_applied(job_url):
                        seen_urls.add(job_url)
                        all_fresh_jobs.append({
                            "title": row.get("title"),
                            "company": row.get("company"),
                            "location": row.get("location"),
                            "job_url": job_url,
                            "description": row.get("description", "No description available"),
                        })
            except Exception as e:
                print(f"Scraping error for '{search_term}' in '{location}': {e}")
                
    print(f"Total unique fresh AI jobs and internships filtered: {len(all_fresh_jobs)}")
    return all_fresh_jobs