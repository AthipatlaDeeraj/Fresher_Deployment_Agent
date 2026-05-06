import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, BackgroundTasks

# Ensure the root directory is in the python path so the 'fda' package can be found
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from fda.core.logger import logger
from fda.data.ingestion import load_ris_data, load_so_data
from fda.data.validation import prepare_clean_ris_data
from fda.engine.aggregation import aggregate_by_project
from fda.engine.decision import execute_rules
from fda.engine.recommendation import generate_recommendations
from fda.output.exporter import export_pyramid_report, export_suggestions_report

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
        # 1. Ingest Data
        logger.info("--- Step 1: Data Ingestion ---")
        ris_raw = load_ris_data()
        so_raw = load_so_data()
        
        # 2. Data Validation & Preparation
        logger.info("--- Step 2: Data Validation & Preparation ---")
        ris_clean = prepare_clean_ris_data(ris_raw)
        
        if ris_clean.empty:
            logger.error("No active records to process after filtering. Exiting.")
            return
            
        # 3. Aggregation Engine
        logger.info("--- Step 3: Aggregation ---")
        agg_data = aggregate_by_project(ris_clean)
        
        # 4. Rule & Decision Engine
        logger.info("--- Step 4: Decision Engine ---")
        decided_data = execute_rules(agg_data, so_data=so_raw)
        
        # 5. Recommendation Engine
        logger.info("--- Step 5: Recommendation Engine ---")
        recommendations = generate_recommendations(decided_data, ris_clean, so_raw)
        
        # 6. Output Generation
        logger.info("--- Step 6: Generating Outputs ---")
        export_pyramid_report(decided_data)
        export_suggestions_report(recommendations, ris_clean)
        
        logger.info("FDA Pipeline completed successfully.")
        
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
