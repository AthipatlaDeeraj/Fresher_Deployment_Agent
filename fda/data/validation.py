import pandas as pd
from fda.config import settings
from fda.core.logger import logger

def load_grade_band_map(file_path: str = settings.GRADE_BAND_MAP_FILE) -> dict:
    """Loads the grade to band mapping from CSV."""
    try:
        df = pd.read_csv(file_path)
        return dict(zip(df['grade'], df['band']))
    except Exception as e:
        logger.error(f"Failed to load grade band map from {file_path}: {str(e)}")
        raise

def filter_active_resources(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the RIS dataframe to only include active resources based on:
    - allocation_percent > 0
    - employee_status not resigned/exit (we check if it's in ACTIVE_EMPLOYEE_STATUSES or just not exit)
    - project_status valid
    """
    initial_count = len(df)
    
    # Example logic: customize based on exact synthetic data content
    # Ensure allocation is numeric
    if 'allocation_percent' not in df.columns:
        logger.warning("'allocation_percent' column not found. Skipping allocation filter.")
        alloc_mask = pd.Series([True] * len(df))
    else:
        alloc_mask = df['allocation_percent'] > 0
        
    if 'employee_status' not in df.columns:
        logger.warning("'employee_status' column not found. Skipping employee status filter.")
        emp_status_mask = pd.Series([True] * len(df))
    else:
        # Assuming we want to exclude Resigned/Exit
        emp_status_mask = ~df['employee_status'].str.lower().isin(['resigned', 'exit', 'terminated'])
        
    if 'project_status' not in df.columns:
        logger.warning("'project_status' column not found. Skipping project status filter.")
        proj_status_mask = pd.Series([True] * len(df))
    else:
        # Assuming we want to exclude Closed/Completed
        proj_status_mask = ~df['project_status'].str.lower().isin(['closed', 'completed'])
        
    active_df = df[alloc_mask & emp_status_mask & proj_status_mask].copy()
    
    filtered_count = len(active_df)
    logger.info(f"Filtered active resources: {filtered_count} / {initial_count} records kept.")
    
    return active_df

def map_grades_to_bands(df: pd.DataFrame, grade_map: dict) -> pd.DataFrame:
    """
    Maps the 'grade' column to 'band' (Junior, Mid, Senior).
    Logs unmapped grades and excludes them.
    """
    if 'grade' not in df.columns:
        logger.error("'grade' column missing from dataframe. Cannot map bands.")
        return df
        
    # Apply mapping
    df['band'] = df['grade'].map(grade_map)
    
    # Find unmapped grades
    unmapped_mask = df['band'].isna()
    if unmapped_mask.any():
        unmapped_grades = df.loc[unmapped_mask, 'grade'].unique()
        logger.warning(f"Unmapped grades found: {unmapped_grades}. These records will be excluded from pyramid calculation.")
        
        # Log sample of unmapped records
        for _, row in df[unmapped_mask].head(5).iterrows():
            emp_id = row.get('employee_id', 'Unknown')
            logger.warning(f"Excluded Employee ID {emp_id} due to unmapped grade: {row['grade']}")
            
    # Filter out unmapped
    mapped_df = df.dropna(subset=['band']).copy()
    return mapped_df

def prepare_clean_ris_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Executes the full cleaning and validation pipeline on RIS data.
    """
    logger.info("Starting RIS data validation and cleaning.")
    
    # 1. Filter active resources
    active_df = filter_active_resources(df)
    
    # 2. Load grade map
    grade_map = load_grade_band_map()
    
    # 3. Map grades to bands
    clean_df = map_grades_to_bands(active_df, grade_map)
    
    # 4. Ensure required columns are present (fill with empty/default if missing but needed later)
    for col in settings.RIS_REQUIRED_COLS:
        if col not in clean_df.columns:
            logger.warning(f"Expected column '{col}' not found in RIS data. Creating with empty values.")
            clean_df[col] = None
            
    logger.info("RIS data preparation complete.")
    return clean_df
