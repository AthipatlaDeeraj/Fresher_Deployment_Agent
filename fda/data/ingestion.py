import pandas as pd
from fda.config import settings
from fda.core.logger import logger

def load_ris_data(file_path: str = settings.RIS_DATA_FILE) -> pd.DataFrame:
    """Loads RIS data from the specified Excel file."""
    logger.info(f"Loading RIS data from {file_path}")
    try:
        # Load all columns as string to avoid dtype issues initially
        df = pd.read_excel(file_path, dtype=str)
        logger.info(f"Successfully loaded {len(df)} records from RIS data.")
        
        # Clean column names (lowercase, replace spaces with underscores)
        df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
        
        # Map columns if they don't exactly match requirements, but user said 
        # "Create an internal clean dataframe with these fields."
        # We will assume the file might have slightly different names, so we'll try to map common variations
        # Or we assume the file already has these exact names or close to them.
        
        # Ensure allocation percent is numeric
        if 'allocation_percent' in df.columns:
            df['allocation_percent'] = pd.to_numeric(df['allocation_percent'], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        logger.error(f"Failed to load RIS data: {str(e)}")
        raise

def load_so_data(file_path: str = settings.SO_DATA_FILE) -> pd.DataFrame:
    """Loads Staffing Demand (SO) data from the specified Excel file."""
    logger.info(f"Loading SO data from {file_path}")
    try:
        df = pd.read_excel(file_path, dtype=str)
        logger.info(f"Successfully loaded {len(df)} records from SO data.")
        
        # Clean column names
        df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
        return df
    except Exception as e:
        logger.error(f"Failed to load SO data: {str(e)}")
        raise
