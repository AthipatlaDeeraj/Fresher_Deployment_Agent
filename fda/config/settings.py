import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
CONFIG_DIR = BASE_DIR / "config"
OUTPUT_DIR = ROOT_DIR / "output"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Input Files
RIS_DATA_FILE = ROOT_DIR / "RIS_Synthetic.xlsx"
SO_DATA_FILE = ROOT_DIR / "SO_Ageing_Synthetic.xlsx"
GRADE_BAND_MAP_FILE = CONFIG_DIR / "grade_band_map.csv"

# Output Files
PYRAMID_REPORT_FILE = OUTPUT_DIR / "Pyramid_Analysis_Report.xlsx"
SUGGESTIONS_REPORT_FILE = OUTPUT_DIR / "Deployment_Training_Suggestions.xlsx"

# Pyramid Target Ratios (percentages)
TARGET_JUNIOR_PCT = 79.0
TARGET_MID_PCT = 20.0
TARGET_SENIOR_PCT = 1.0

# Rule Thresholds
R2_HIGH_FRESHER_THRESHOLD_PCT = 85.0 # If junior % is higher than this, it's a high fresher intake

# Active Resource Statuses
ACTIVE_EMPLOYEE_STATUSES = ["Active", "Deployed", "Bench"]
ACTIVE_PROJECT_STATUSES = ["Active", "In Progress", "Green", "Yellow", "Red"]

# Required columns for internal dataframes
RIS_REQUIRED_COLS = [
    "employee_id", "employee_name", "grade", "project_id", "project_name",
    "project_status", "employee_status", "allocation_percent", "start_date",
    "end_date", "project_role", "technology", "skills"
]
