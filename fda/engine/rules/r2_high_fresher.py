from fda.engine.rules.base import Rule
import pandas as pd
from fda.config import settings

class R2HighFresherIntake(Rule):
    """
    R2: High Fresher Intake
    Triggered when there is a high junior ratio relative to team size.
    Configurable threshold (default 85%).
    """
    
    @property
    def rule_id(self) -> str:
        return "R2"
        
    @property
    def description(self) -> str:
        return f"High junior ratio relative to team size (> {settings.R2_HIGH_FRESHER_THRESHOLD_PCT}%)"
        
    def evaluate(self, project_data: pd.Series, *args, **kwargs) -> bool:
        junior_pct = project_data.get('junior_pct', 0)
        return junior_pct > settings.R2_HIGH_FRESHER_THRESHOLD_PCT
