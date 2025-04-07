import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.services.data_processor import (
    process_health_data,
    extract_test_date,
    extract_test_type,
    extract_parameters,
    detect_unit
)

@pytest.fixture
def sample_blood_test_data():
    return pd.DataFrame({
        'Test Date': ['2025-04-07'],
        'Hemoglobin': [14.5],
        'WBC': [7.8],
        'RBC': [5.2],
        'Platelets': [250],
        'Notes': ['Regular checkup']
    })

@pytest.mark.asyncio
async def test_process_health_data(sample_blood_test_data):
    result = await process_health_data(sample_blood_test_data)
    
    assert isinstance(result, dict)
    assert 'test_date' in result
    assert 'test_type' in result
    assert 'parameters' in result
    assert len(result['parameters']) == 4  # Excluding Notes and Test Date

def test_extract_test_date(sample_blood_test_data):
    result = extract_test_date(sample_blood_test_data)
    
    assert isinstance(result, datetime)
    assert result.date() == datetime(2025, 4, 7).date()

def test_extract_test_type(sample_blood_test_data):
    result = extract_test_type(sample_blood_test_data)
    
    assert result == 'blood_panel'

def test_extract_parameters(sample_blood_test_data):
    result = extract_parameters(sample_blood_test_data)
    
    assert isinstance(result, list)
    assert len(result) == 4  # Four blood test parameters
    assert all(isinstance(param, dict) for param in result)
    assert all(key in param for param in result for key in ['name', 'value', 'unit', 'status'])

def test_detect_unit():
    assert detect_unit('hemoglobin', 14.5) == 'g/dL'
    assert detect_unit('glucose', 95) == 'mg/dL'
    assert detect_unit('wbc', 7.8) == '10³/µL'
    assert detect_unit('unknown_parameter', 0.5) == 'ratio'
