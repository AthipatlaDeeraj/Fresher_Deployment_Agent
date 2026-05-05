import sys
from pathlib import Path

# Ensure the root directory is in the python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from fda.core.logger import logger
from fda.data.ingestion import load_ris_data, load_so_data
from fda.data.validation import prepare_clean_ris_data
from fda.engine.aggregation import aggregate_by_project
from fda.engine.decision import execute_rules
from fda.engine.recommendation import generate_recommendations
from fda.output.exporter import export_pyramid_report, export_suggestions_report

def main():
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
        export_suggestions_report(recommendations)
        
        logger.info("FDA Pipeline completed successfully.")
        
    except Exception as e:
        logger.exception(f"FDA Pipeline failed with error: {str(e)}")

if __name__ == "__main__":
    main()
