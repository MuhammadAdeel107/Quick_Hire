import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent # Ya create_react_agent
from app.services.scraper import fetch_all_ai_jobs
from app.services.matcher import evaluate_job
from app.services.applier import apply_to_job
from app.services.logger_services import init_db, log_application

load_dotenv()

@tool
def discover_and_apply_tool(query: str) -> str:
    """Discovers AI/Python jobs, evaluates them using Gemini AI, and applies if match score >= 65."""
    print("\n[INFO] Initializing Database & Scraping Fresh Jobs...")
    init_db()
    
    # 1. Scrape jobs
    jobs = fetch_all_ai_jobs(results_wanted_per_query=2)
    if not jobs:
        return "No fresh jobs found."
    
    print(f"[INFO] Evaluating {len(jobs)} unique jobs against your profile...")
    applied_count = 0
    
    # 2. Evaluate and Apply loop
    for job in jobs:
        title = job.get("title", "Unknown Role")
        company = job.get("company", "Unknown Company")
        print(f"-> Evaluating: {title} at {company}...")
        
        evaluation = evaluate_job(job.get("description", ""), company, title)
        score = evaluation.get("match_score", 0)
        
        if score >= 60:
            print(f"   [MATCH {score}%] High match! Applying...")
            success, status = apply_to_job(job, evaluation)
            if success:
                log_application(job.get("job_url"), company, title, score, evaluation.get("application_method"), status)
                applied_count += 1
        else:
            print(f"   [SKIP {score}%] Low match.")
                
    return f"Process finished. Successfully applied to {applied_count} matching positions out of {len(jobs)} discovered jobs."

# Setup LLM & Agent
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    google_api_key=os.getenv("GEMINI_API_KEY")
    )

tools = [discover_and_apply_tool]
agent_executor = create_agent(llm, tools)

def run_agent_workflow():
    print("==================================================")
    print(" Autonomous Job Agent Workflow Started...")
    print("==================================================")
    
    query = "Find fresh AI and Python jobs, evaluate them, and apply to matching roles."
    
    try:
        # Stream ke bajaye direct invoke use karein taake extra JSON logs print na hon
        response = agent_executor.invoke({"messages": [("user", query)]})
        
        print("\n==================================================")
        print("AGENT EXECUTION REPORT:")
        print("==================================================")
        for message in response["messages"]:
            # Sirf agent ka final text output print karein
            if message.type == "ai" and message.content:
                if isinstance(message.content, list):
                    for block in message.content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            print(block["text"])
                print(message.content)
        print("==================================================")
    except Exception as e:
        print(f"[ERROR]: {e}")