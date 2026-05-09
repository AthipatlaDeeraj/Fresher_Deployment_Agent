import pandas as pd
from typing import Dict, Any

def sanitize_project_data(project_row: pd.Series, ris_skills: set, so_skills: set) -> Dict[str, Any]:
    """
    Strict data sanitization before LLM calls.
    Ensures no PII or raw DataFrames are passed to the LLM.
    Returns only high-level aggregates and text features.
    """
    return {
        "project_name": str(project_row.get("project_name", "UNKNOWN")),
        "junior_gap_percentage": round(float(project_row.get("junior_gap", 0)), 2),
        "current_junior_percentage": round(float(project_row.get("junior_pct", 0)), 2),
        "team_size": int(project_row.get("total_headcount", 0)),
        "current_team_skills": list(ris_skills),
        "demanded_skills": list(so_skills)
    }
