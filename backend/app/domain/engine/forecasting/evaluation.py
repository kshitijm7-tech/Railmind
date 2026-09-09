from typing import List, Dict
from app.domain.models.forecasting import ForecastObservation

def calculate_mae(actuals: List[float], predictions: List[float]) -> float:
    if not actuals or not predictions or len(actuals) != len(predictions):
        return 0.0
    errors = [abs(a - p) for a, p in zip(actuals, predictions)]
    return sum(errors) / len(errors)

def calculate_rmse(actuals: List[float], predictions: List[float]) -> float:
    import math
    if not actuals or not predictions or len(actuals) != len(predictions):
        return 0.0
    errors_sq = [(a - p) ** 2 for a, p in zip(actuals, predictions)]
    return math.sqrt(sum(errors_sq) / len(errors_sq))

def calculate_mape(actuals: List[float], predictions: List[float]) -> float:
    if not actuals or not predictions or len(actuals) != len(predictions):
        return 0.0
    percentage_errors = []
    for a, p in zip(actuals, predictions):
        if a == 0:
            # Avoid division by zero, use absolute error or skip
            percentage_errors.append(abs(a - p)) 
        else:
            percentage_errors.append(abs((a - p) / a))
    return (sum(percentage_errors) / len(percentage_errors)) * 100.0