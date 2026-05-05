# Fresher Deployment Agent (FDA)

FDA is a production-grade Decision Intelligence System that ingests synthetic resource (RIS) and staffing demand (SO) data to analyze team compositions, calculate pyramid ratios, and provide deployment and training recommendations based on modular rules.

## Architecture

The system is built using Clean Architecture principles to ensure modularity, scalability, and ease of testing.

* **config/**: Contains `settings.py` for global configuration (thresholds, paths) and `grade_band_map.csv` for data mapping.
* **core/**: Contains centralized components like `logger.py` to ensure consistent logging across the application.
* **data/**:
  * `ingestion.py`: Handles loading raw data from external Excel files using Pandas.
  * `validation.py`: Filters active resources (based on allocation, status) and maps grades to standard bands (Junior, Mid, Senior), rejecting invalid data.
* **engine/**:
  * `aggregation.py`: Groups validated data by project and calculates headcounts, ratios, and target gaps.
  * `decision.py`: The core rule engine executor. It applies each configured rule to the aggregated data.
  * `rules/`: A pluggable rule system. `base.py` defines the `Rule` interface. Each rule (e.g., R1, R2) is self-contained.
  * `recommendation.py`: Consumes decision outputs and SO data to generate specific deployment numbers and training suggestions based on dominant skills.
* **output/**: `exporter.py` handles writing the final analyzed datasets into the required Excel formats.
* **tests/**: `pytest` based unit and pipeline tests to verify mathematical correctness and data flow.
* **main.py**: The orchestrator script that links all layers together.

## Setup Instructions

1. Ensure you have Python 3.9+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure the synthetic data files (`RIS_Synthetic.xlsx`, `SO_Ageing_Synthetic.xlsx`) are in the root directory (parent of `fda`).

## Execution Instructions

Run the main pipeline:
```bash
python fda/main.py
```

Run tests:
```bash
pytest fda/tests/
```

## Output

The application will generate a `logs/` folder containing execution logs, and an `output/` folder containing:
1. `Pyramid_Analysis_Report.xlsx`: Contains aggregated project counts, ratios, gaps, and triggered flags.
2. `Deployment_Training_Suggestions.xlsx`: Contains project-level fresher deployment recommendations and skill training suggestions.
