from fda.engine.rules.base import Rule
import pandas as pd

class R3FresherDeployment(Rule):
    """
    R3: Fresher Deployment Opportunity
    Triggered when there is a Junior deficit (Junior Gap > 0).
    The recommendation engine will later use SO data to match skills/roles.
    """
    
    @property
    def rule_id(self) -> str:
        return "R3"
        
    @property
    def description(self) -> str:
        return "Junior deficit exists. Fresher deployment opportunity available."
        
    def evaluate(self, project_data: pd.Series, *args, **kwargs) -> bool:
        junior_gap = project_data.get('junior_gap', 0)
        return junior_gap > 0
