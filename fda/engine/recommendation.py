import pandas as pd
import math
from fda.core.logger import logger
from fda.config import settings

def extract_dominant_skills(df: pd.DataFrame, project_id: str, col_name: str = 'skills') -> set:
    """Extracts dominant skills for a given project from a dataframe column."""
    if col_name not in df.columns:
        return set()
        
    proj_data = df[df['project_id'] == project_id]
    if proj_data.empty:
        return set()
        
    all_skills = []
    for skills_str in proj_data[col_name].dropna():
        # Handle comma-separated skills
        skills = [s.strip().upper() for s in str(skills_str).split(',')]
        all_skills.extend(skills)
        
    # Get top 3 most common skills
    if not all_skills:
        return set()
        
    skill_counts = pd.Series(all_skills).value_counts()
    top_skills = set(skill_counts.head(3).index.tolist())
    return top_skills

def generate_recommendations(decided_df: pd.DataFrame, ris_data: pd.DataFrame, so_data: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Deployment & Training Suggestions Report based on decision engine output and SO data.
    """
    logger.info("Generating deployment and training recommendations.")
    
    recommendations = []
    
    for _, row in decided_df.iterrows():
        project_id = row['project_id']
        total_hc = row.get('total_headcount', 0)
        junior_gap_pct = row.get('junior_gap', 0)
        r3_flag = row.get('R3', False)
        r4_flag = row.get('R4', False)
        
        # 1. Suggested Fresher Count
        suggested_fresher_count = 0
        if junior_gap_pct > 0 and total_hc > 0:
            suggested_fresher_count = math.ceil((junior_gap_pct / 100.0) * total_hc)
            
        # 2. Extract skills
        so_skills = extract_dominant_skills(so_data, project_id, 'skills')
        ris_skills = extract_dominant_skills(ris_data, project_id, 'skills')
        
        # Determine relevant skills for deployment (from SO data)
        relevant_skills = ", ".join(so_skills) if so_skills else "N/A"
        primary_skills = ", ".join(ris_skills) if ris_skills else "N/A"
        
        # Determine training suggestions
        training_suggestions = "N/A"
        if r4_flag:
            combined_skills = ris_skills.union(so_skills)
            if combined_skills:
                training_suggestions = f"Focus training on: {', '.join(combined_skills)}"
            else:
                training_suggestions = "General Fresher Onboarding Training"
                
        rec = {
            'project_id': project_id,
            'junior_pct': row.get('junior_pct', 0),
            'junior_gap': row.get('junior_gap', 0),
            'deployment_flag': 'Yes' if r3_flag else 'No',
            'suggested_fresher_count': suggested_fresher_count if r3_flag else 0,
            'relevant_skills': relevant_skills,
            'primary_skills': primary_skills,
            'training_suggestions': training_suggestions
        }
        recommendations.append(rec)
        
    rec_df = pd.DataFrame(recommendations)
    logger.info("Recommendation generation complete.")
    return rec_df
