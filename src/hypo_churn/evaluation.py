"""Model evaluation utilities."""

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
import pandas as pd
import numpy as np
from typing import Dict


def evaluate_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray = None
) -> Dict[str, float]:
    """
    Evaluate model performance using multiple metrics.

    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_proba: Predicted probabilities (optional)

    Returns:
        Dictionary of evaluation metrics
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1_score": f1_score(y_true, y_pred, zero_division=0),
    }

    if y_proba is not None:
        metrics["roc_auc"] = roc_auc_score(y_true, y_proba[:, 1])

    return metrics


def print_evaluation_results(metrics: Dict[str, float]) -> None:
    """
    Print evaluation results in a formatted manner.

    Args:
        metrics: Dictionary of evaluation metrics
    """
    print("\n" + "="*50)
    print("Model Evaluation Results")
    print("="*50)
    for metric_name, value in metrics.items():
        print(f"{metric_name.replace('_', ' ').title()}: {value:.4f}")
    print("="*50 + "\n")
