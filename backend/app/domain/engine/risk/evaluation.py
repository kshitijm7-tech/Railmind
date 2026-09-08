from typing import List, Dict

def evaluate_classification_accuracy(actuals: List[str], predictions: List[str]) -> float:
    if not actuals or not predictions or len(actuals) != len(predictions):
        return 0.0
    matches = sum(1 for a, p in zip(actuals, predictions) if a == p)
    return matches / len(actuals)

def evaluate_precision_recall(actuals: List[str], predictions: List[str], target_class: str) -> Dict[str, float]:
    if not actuals or not predictions or len(actuals) != len(predictions):
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
    tp = sum(1 for a, p in zip(actuals, predictions) if a == target_class and p == target_class)
    fp = sum(1 for a, p in zip(actuals, predictions) if a != target_class and p == target_class)
    fn = sum(1 for a, p in zip(actuals, predictions) if a == target_class and p != target_class)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {"precision": precision, "recall": recall, "f1": f1}