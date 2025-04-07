import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest

async def calculate_trends(df: pd.DataFrame, parameter: str, timeframe: str) -> Dict:
    """
    Calculate trends for a specific health parameter over time.
    """
    try:
        # Convert timeframe to datetime
        end_date = datetime.utcnow()
        if timeframe == "1m":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "6m":
            start_date = end_date - timedelta(days=180)
        else:  # 1y default
            start_date = end_date - timedelta(days=365)
        
        # Filter data by timeframe
        mask = (df['test_date'] >= start_date) & (df['test_date'] <= end_date)
        df_filtered = df.loc[mask]
        
        # Extract parameter values
        values = []
        dates = []
        for record in df_filtered.itertuples():
            for param in record.parameters:
                if param['name'].lower() == parameter.lower():
                    values.append(param['value'])
                    dates.append(record.test_date)
        
        if not values:
            return {"message": f"No data available for parameter: {parameter}"}
        
        # Calculate basic statistics
        stats = {
            "mean": np.mean(values),
            "median": np.median(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "trend": calculate_trend_direction(values)
        }
        
        # Create time series data
        time_series = list(zip(dates, values))
        
        return {
            "parameter": parameter,
            "statistics": stats,
            "time_series": time_series
        }
    
    except Exception as e:
        raise ValueError(f"Error calculating trends: {str(e)}")

async def detect_anomalies(df: pd.DataFrame) -> List[Dict]:
    """
    Detect anomalies in health parameters using Isolation Forest.
    """
    try:
        anomalies = []
        
        # Process each parameter separately
        for record in df.itertuples():
            for param in record.parameters:
                # Get historical values for this parameter
                param_values = []
                for r in df.itertuples():
                    for p in r.parameters:
                        if p['name'] == param['name']:
                            param_values.append(p['value'])
                
                if len(param_values) >= 5:  # Only analyze if we have enough data points
                    # Reshape for sklearn
                    X = np.array(param_values).reshape(-1, 1)
                    
                    # Fit isolation forest
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    yhat = iso_forest.fit_predict(X)
                    
                    # Check if current value is an anomaly
                    if yhat[-1] == -1:
                        anomalies.append({
                            "parameter": param['name'],
                            "value": param['value'],
                            "date": record.test_date,
                            "severity": calculate_anomaly_severity(param['value'], param_values)
                        })
        
        return anomalies
    
    except Exception as e:
        raise ValueError(f"Error detecting anomalies: {str(e)}")

async def generate_health_score(df: pd.DataFrame) -> float:
    """
    Generate an overall health score based on various parameters.
    """
    try:
        # Define weights for different parameter categories
        weights = {
            "blood": 0.3,
            "metabolic": 0.25,
            "lipid": 0.25,
            "thyroid": 0.2
        }
        
        scores = []
        weight_sum = 0
        
        # Calculate scores for each category
        for category, weight in weights.items():
            category_score = calculate_category_score(df, category)
            if category_score is not None:
                scores.append(category_score * weight)
                weight_sum += weight
        
        if not scores:
            return 0.0
        
        # Normalize the final score to 0-100 range
        final_score = sum(scores) / weight_sum * 100
        
        return round(final_score, 2)
    
    except Exception as e:
        raise ValueError(f"Error generating health score: {str(e)}")

async def get_reference_ranges() -> Dict:
    """
    Get reference ranges for common health parameters.
    """
    return {
        "blood": {
            "hemoglobin": {"male": {"min": 13.5, "max": 17.5}, "female": {"min": 12.0, "max": 15.5}, "unit": "g/dL"},
            "wbc": {"min": 4.5, "max": 11.0, "unit": "10³/µL"},
            "rbc": {"male": {"min": 4.7, "max": 6.1}, "female": {"min": 4.2, "max": 5.4}, "unit": "10⁶/µL"},
            "platelets": {"min": 150, "max": 450, "unit": "10³/µL"}
        },
        "lipid": {
            "total_cholesterol": {"min": 0, "max": 200, "unit": "mg/dL"},
            "hdl": {"min": 40, "max": 60, "unit": "mg/dL"},
            "ldl": {"min": 0, "max": 100, "unit": "mg/dL"},
            "triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"}
        },
        "metabolic": {
            "glucose": {"min": 70, "max": 100, "unit": "mg/dL"},
            "calcium": {"min": 8.5, "max": 10.5, "unit": "mg/dL"},
            "sodium": {"min": 135, "max": 145, "unit": "mEq/L"},
            "potassium": {"min": 3.5, "max": 5.0, "unit": "mEq/L"}
        },
        "thyroid": {
            "tsh": {"min": 0.4, "max": 4.0, "unit": "mIU/L"},
            "t3": {"min": 80, "max": 200, "unit": "ng/dL"},
            "t4": {"min": 5.0, "max": 12.0, "unit": "µg/dL"}
        }
    }

def calculate_trend_direction(values: List[float]) -> str:
    """
    Calculate the trend direction based on recent values.
    """
    if len(values) < 2:
        return "stable"
    
    # Calculate percentage change
    change = (values[-1] - values[0]) / values[0] * 100
    
    if change > 5:
        return "increasing"
    elif change < -5:
        return "decreasing"
    else:
        return "stable"

def calculate_anomaly_severity(value: float, historical_values: List[float]) -> str:
    """
    Calculate the severity of an anomaly based on its deviation from the mean.
    """
    mean = np.mean(historical_values)
    std = np.std(historical_values)
    z_score = abs((value - mean) / std)
    
    if z_score > 3:
        return "high"
    elif z_score > 2:
        return "medium"
    else:
        return "low"

def calculate_category_score(df: pd.DataFrame, category: str) -> float:
    """
    Calculate a score for a specific category of health parameters.
    """
    try:
        # Get reference ranges
        ranges = get_reference_ranges()[category]
        
        scores = []
        for record in df.itertuples():
            for param in record.parameters:
                param_name = param['name'].lower()
                if param_name in ranges:
                    value = param['value']
                    range_info = ranges[param_name]
                    
                    # Handle gender-specific ranges
                    if isinstance(range_info, dict) and ('male' in range_info or 'female' in range_info):
                        # Use male ranges as default if gender not specified
                        range_info = range_info.get('male', range_info.get('female'))
                    
                    min_val = range_info['min']
                    max_val = range_info['max']
                    
                    # Calculate score (0-1 range)
                    if value < min_val:
                        score = value / min_val
                    elif value > max_val:
                        score = max_val / value
                    else:
                        score = 1.0
                    
                    scores.append(score)
        
        if not scores:
            return None
        
        return np.mean(scores)
    
    except Exception:
        return None
