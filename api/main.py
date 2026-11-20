from app.services.agent import run_agent_workflow

if __name__ == "__main__":
    print("==================================================")
    print(" Starting Autonomous Job Agent Execution...")
    print("==================================================")
    
    # Run the workflow once and auto-exit upon completion
    run_agent_workflow()
    
    print("==================================================")
    print(" Job Agent finished and exited successfully.")
    print("==================================================")