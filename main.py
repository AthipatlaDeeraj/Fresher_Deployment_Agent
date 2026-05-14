import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, BackgroundTasks

# Ensure the root directory is in the python path so the 'fda' package can be found
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from fda.logger import logger
from fda.graph.graph_builder import build_fda_graph
from fda.graph.state import FDAState

# Initialize FastAPI app
app = FastAPI(
    title="Fresher Deployment Agent (FDA) API", 
    description="API for triggering the FDA pipeline",
    version="1.0.0"
)

def run_fda_pipeline():
    """Core pipeline logic."""
    logger.info("Starting Fresher Deployment Agent (FDA) Pipeline...")
    
    try:
        # Compile Graph
        logger.info("Building LangGraph...")
        graph = build_fda_graph()
        
        # Initialize State
        initial_state = FDAState()
        
        # Run Graph
        logger.info("Executing LangGraph Pipeline...")
        final_state = graph.invoke(initial_state)
        
        logger.info("LangGraph Pipeline completed successfully.")
        
    except Exception as e:
        logger.exception(f"FDA Pipeline failed with error: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "FDA API is running. Go to /docs to view the Swagger UI."}

@app.post("/run-pipeline")
def trigger_pipeline(background_tasks: BackgroundTasks):
    """Triggers the FDA analysis pipeline via Swagger."""
    background_tasks.add_task(run_fda_pipeline)
    return {"message": "FDA Pipeline triggered successfully. Check logs and the output/ folder for results."}

def start():
    """Entry point for the application."""
    logger.info("Starting FDA API Server...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    start()
