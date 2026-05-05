import pytest
import pandas as pd
from fda.engine.aggregation import aggregate_by_project
from fda.engine.decision import execute_rules
from fda.engine.recommendation import generate_recommendations

@pytest.fixture
def sample_ris_data():
    return pd.DataFrame([
        {'employee_id': '1', 'project_id': 'P1', 'band': 'Junior', 'skills': 'Python, SQL'},
        {'employee_id': '2', 'project_id': 'P1', 'band': 'Mid', 'skills': 'Python'},
        {'employee_id': '3', 'project_id': 'P2', 'band': 'Junior', 'skills': 'Java'},
    ])

@pytest.fixture
def sample_so_data():
    return pd.DataFrame([
        {'project_id': 'P1', 'skills': 'Python, AWS'},
        {'project_id': 'P2', 'skills': 'Java, Spring'}
    ])

def test_aggregation(sample_ris_data):
    agg_df = aggregate_by_project(sample_ris_data)
    assert len(agg_df) == 2
    p1 = agg_df[agg_df['project_id'] == 'P1'].iloc[0]
    assert p1['total_headcount'] == 2
    assert p1['junior_count'] == 1
    assert p1['junior_pct'] == 50.0

def test_decision_engine(sample_ris_data, sample_so_data):
    agg_df = aggregate_by_project(sample_ris_data)
    decided_df = execute_rules(agg_df, so_data=sample_so_data)
    
    assert 'R1' in decided_df.columns
    assert 'flags' in decided_df.columns
    # With 50% junior, P1 should trigger R1 (Low Junior)
    p1 = decided_df[decided_df['project_id'] == 'P1'].iloc[0]
    assert p1['R1'] is True

def test_recommendation_engine(sample_ris_data, sample_so_data):
    agg_df = aggregate_by_project(sample_ris_data)
    decided_df = execute_rules(agg_df, so_data=sample_so_data)
    rec_df = generate_recommendations(decided_df, sample_ris_data, sample_so_data)
    
    assert len(rec_df) == 2
    p1_rec = rec_df[rec_df['project_id'] == 'P1'].iloc[0]
    assert 'PYTHON' in p1_rec['training_suggestions'].upper()
    assert 'AWS' in p1_rec['training_suggestions'].upper()
