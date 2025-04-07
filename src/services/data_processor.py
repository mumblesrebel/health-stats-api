import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime

async def process_health_data(df: pd.DataFrame) -> Dict:
    """
    Process health data from various file formats into a standardized format.
    """
    try:
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Basic data cleaning
        df = df.dropna(how='all')
        
        # Extract test information
        test_info = {
            'test_date': extract_test_date(df),
            'test_type': extract_test_type(df),
            'parameters': extract_parameters(df),
        }
        
        return test_info
    except Exception as e:
        raise ValueError(f"Error processing health data: {str(e)}")

def extract_test_date(df: pd.DataFrame) -> datetime:
    """
    Extract test date from the dataframe.
    """
    date_columns = [col for col in df.columns if 'date' in col]
    if date_columns:
        # Try to parse the first date column
        try:
            return pd.to_datetime(df[date_columns[0]].iloc[0])
        except:
            pass
    
    # If no date column found or parsing failed, use current date
    return datetime.utcnow()

def extract_test_type(df: pd.DataFrame) -> str:
    """
    Determine the type of test from the data.
    """
    # Look for common test type indicators in column names
    test_indicators = {
        'blood': ['hemoglobin', 'wbc', 'rbc', 'platelets'],
        'lipid': ['cholesterol', 'hdl', 'ldl', 'triglycerides'],
        'thyroid': ['tsh', 't3', 't4'],
        'metabolic': ['glucose', 'calcium', 'sodium', 'potassium']
    }
    
    columns = df.columns.str.lower()
    for test_type, indicators in test_indicators.items():
        if any(indicator in columns.str.contains(indicator).any() for indicator in indicators):
            return f"{test_type}_panel"
    
    return "general_test"

def extract_parameters(df: pd.DataFrame) -> List[Dict]:
    """
    Extract test parameters and their values.
    """
    parameters = []
    
    # Skip metadata columns
    skip_columns = ['date', 'id', 'patient', 'doctor', 'notes']
    
    for column in df.columns:
        if not any(skip in column.lower() for skip in skip_columns):
            try:
                value = float(df[column].iloc[0])
                parameters.append({
                    'name': column,
                    'value': value,
                    'unit': detect_unit(column, value),
                    'status': 'normal'  # Default status
                })
            except (ValueError, TypeError):
                continue
    
    return parameters

def detect_unit(parameter: str, value: float) -> str:
    """
    Detect the likely unit for a parameter based on its name and value.
    """
    parameter = parameter.lower()
    
    # Common units mapping
    unit_mappings = {
        'hemoglobin': 'g/dL',
        'glucose': 'mg/dL',
        'cholesterol': 'mg/dL',
        'wbc': '10³/µL',
        'rbc': '10⁶/µL',
        'platelets': '10³/µL',
        'tsh': 'mIU/L',
        'sodium': 'mEq/L',
        'potassium': 'mEq/L',
        'calcium': 'mg/dL',
        'creatinine': 'mg/dL',
    }
    
    # Try to find a matching unit
    for key, unit in unit_mappings.items():
        if key in parameter:
            return unit
    
    # Default units based on value ranges
    if value < 1:
        return 'ratio'
    elif value < 100:
        return 'units'
    else:
        return 'mg/dL'
