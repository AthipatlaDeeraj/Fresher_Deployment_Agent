import pandas as pd
import math
from fda.graph.state import FDAState
from fda.services.recommendation_engine import extract_skills_for_project
from fda.core.logger import logger

def recommendation_node(state: FDAState) -> FDAState:
    logger.info("--- NODE: recommendation_node ---")
    df = state.rule_results
    so_df = state.raw_data.get("so")
    ris_df = state.raw_data.get("ris")
    r3_outputs = state.r3_output
    r4_outputs = state.r4_output
    
    if df is None:
        return state
        
    so_skill_cols = ['technology', 'skills', 'secondary_skills']
    ris_skill_cols = ['technology', 'skills']
    
    recommendations = []
    
    for _, row in df.iterrows():
        project_name = row['project_name']
        project_id = row.get('project_id', 'N/A')
        total_hc = int(row.get('total_headcount', 0))
        junior_gap_pct = float(row.get('junior_gap', 0))
        
        r3_result = r3_outputs.get(project_name, {})
        r4_result = r4_outputs.get(project_name, {})
        
        is_r3 = r3_result.get("suitable_for_fresher", False)
        
        suggested_fresher_count = 0
        if is_r3 and total_hc > 0:
            suggested_fresher_count = math.ceil((junior_gap_pct / 100.0) * total_hc)
            
        ris_skills = extract_skills_for_project(ris_df, project_name, ris_skill_cols)
        so_skills = extract_skills_for_project(so_df, project_name, so_skill_cols)
        
        relevant_skills = ", ".join(so_skills) if so_skills else "N/A"
        primary_skills_present = ", ".join(ris_skills) if ris_skills else "N/A"
        
        training_theme = r4_result.get("primary_theme", "N/A")
        training_flag = "YES" if r4_result.get("training_required", False) else "NO"
        
        readiness_score = r3_result.get("deployment_readiness_score", 0.0)
        
        recommendations.append({
            'project_id': project_id,
            'project_name': project_name,
            'junior_pct': round(float(row.get('junior_pct', 0)), 2),
            'junior_gap': round(junior_gap_pct, 2),
            'pyramid_health': row.get('flags', 'Healthy / Monitoring'),
            'deployment_flag': 'Yes' if is_r3 else 'No',
            'suggested_fresher_count': suggested_fresher_count if is_r3 else 0,
            'relevant_skills': relevant_skills,
            'primary_skills': primary_skills_present,
            'training_suggestions': training_theme,
            'training_flag': training_flag,
            'deployment_readiness_score': readiness_score
        })
        
    state.recommendations = pd.DataFrame(recommendations)
    return state
