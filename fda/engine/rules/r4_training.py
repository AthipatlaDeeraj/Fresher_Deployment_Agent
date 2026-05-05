from fda.engine.rules.base import Rule
import pandas as pd

class R4TrainingSuggestions(Rule):
    """
    R4: Training Suggestions
    Triggered to indicate that training suggestions should be extracted.
    For simplicity, this rule flags projects that have a junior gap,
    implying we need to train incoming freshers on dominant skills.
    Alternatively, it flags all projects for the recommendation engine to process.
    """
    
    @property
    def rule_id(self) -> str:
        return "R4"
        
    @property
    def description(self) -> str:
        return "Training suggestions needed based on RIS + SO dominant skills."
        
    def evaluate(self, project_data: pd.Series, *args, **kwargs) -> bool:
        # We can trigger this for projects that have a deployment opportunity (R3) 
        # or just generally return True so the recommendation engine always evaluates it.
        # Let's trigger if there's any gap or high fresher intake, meaning training is needed.
        junior_gap = project_data.get('junior_gap', 0)
        junior_pct = project_data.get('junior_pct', 0)
        
        # Trigger if we need freshers (gap > 0) OR if we have too many (high intake > 85)
        # In both cases, training is highly relevant.
        if junior_gap > 0 or junior_pct > 85.0:
            return True
        return False
