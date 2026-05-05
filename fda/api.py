from fastapi import FastAPI, BackgroundTasks
import sys
from pathlib import Path

# Ensure the root directory is in the python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from fda.main import main as run_fda_pipeline

app = FastAPI(
    title="Fresher Deployment Agent (FDA) API", 
    description="API for triggering the FDA pipeline",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "FDA API is running. Go to /docs to view the Swagger UI."}

@app.post("/run-pipeline")
def trigger_pipeline(background_tasks: BackgroundTasks):
    """
    Triggers the FDA analysis pipeline.
    This reads the configured Excel files and generates the output reports in the output/ folder.
    """
    # Running in background so the API doesn't block while processing large files
    background_tasks.add_task(run_fda_pipeline)
    return {"message": "FDA Pipeline triggered successfully. Check logs and the output/ folder for results."}
