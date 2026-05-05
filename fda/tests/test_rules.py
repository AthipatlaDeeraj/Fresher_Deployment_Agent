import pytest
import pandas as pd
from fda.engine.rules.r1_low_junior import R1LowJuniorRatio
from fda.engine.rules.r2_high_fresher import R2HighFresherIntake
from fda.engine.rules.r3_deployment import R3FresherDeployment
from fda.config import settings

def test_r1_low_junior():
    rule = R1LowJuniorRatio()
    # Below target
    data_below = pd.Series({'junior_pct': settings.TARGET_JUNIOR_PCT - 5})
    assert rule.evaluate(data_below) is True
    
    # Above target
    data_above = pd.Series({'junior_pct': settings.TARGET_JUNIOR_PCT + 5})
    assert rule.evaluate(data_above) is False

def test_r2_high_fresher():
    rule = R2HighFresherIntake()
    # Above threshold
    data_above = pd.Series({'junior_pct': settings.R2_HIGH_FRESHER_THRESHOLD_PCT + 5})
    assert rule.evaluate(data_above) is True
    
    # Below threshold
    data_below = pd.Series({'junior_pct': settings.R2_HIGH_FRESHER_THRESHOLD_PCT - 5})
    assert rule.evaluate(data_below) is False

def test_r3_deployment():
    rule = R3FresherDeployment()
    # Gap > 0
    data_gap = pd.Series({'junior_gap': 5})
    assert rule.evaluate(data_gap) is True
    
    # Gap <= 0
    data_no_gap = pd.Series({'junior_gap': -5})
    assert rule.evaluate(data_no_gap) is False
