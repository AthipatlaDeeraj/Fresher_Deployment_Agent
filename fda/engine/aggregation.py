import pandas as pd
from fda.config import settings
from fda.core.logger import logger

def aggregate_by_project(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups data by Project ID and computes:
    - total headcount
    - junior count, mid count, senior count
    - ratios for each band
    - gaps for each band
    """
    logger.info("Aggregating data by Project ID.")
    
    if 'project_id' not in df.columns or 'band' not in df.columns:
        logger.error("Missing required columns ('project_id' or 'band') for aggregation.")
        return pd.DataFrame()
        
    # Group by project
    # We want to count occurrences of each band per project
    agg_df = df.groupby('project_id').agg(
        total_headcount=('employee_id', 'count'),
        # Ensure we capture project_name if available
        project_name=('project_name', 'first') if 'project_name' in df.columns else ('project_id', 'first')
    ).reset_index()
    
    # Calculate band counts
    band_counts = df.groupby(['project_id', 'band']).size().unstack(fill_value=0).reset_index()
    
    # Merge band counts into agg_df
    agg_df = pd.merge(agg_df, band_counts, on='project_id', how='left')
    
    # Rename columns if they exist
    for col, new_name in [('Junior', 'junior_count'), ('Mid', 'mid_count'), ('Senior', 'senior_count')]:
        if col in agg_df.columns:
            agg_df.rename(columns={col: new_name}, inplace=True)
        else:
            agg_df[new_name] = 0
            
    # Compute Ratios
    agg_df['junior_pct'] = (agg_df['junior_count'] / agg_df['total_headcount']) * 100
    agg_df['mid_pct'] = (agg_df['mid_count'] / agg_df['total_headcount']) * 100
    agg_df['senior_pct'] = (agg_df['senior_count'] / agg_df['total_headcount']) * 100
    
    # Compute Gaps
    agg_df['junior_gap'] = settings.TARGET_JUNIOR_PCT - agg_df['junior_pct']
    agg_df['mid_gap'] = settings.TARGET_MID_PCT - agg_df['mid_pct']
    agg_df['senior_gap'] = settings.TARGET_SENIOR_PCT - agg_df['senior_pct']
    
    logger.info(f"Aggregation complete for {len(agg_df)} projects.")
    return agg_df
