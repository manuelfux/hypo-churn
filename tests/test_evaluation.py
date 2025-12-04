"""Tests for evaluation module."""

import pytest
import numpy as np
from hypo_churn.evaluation import evaluate_model, print_evaluation_results


@pytest.fixture
def sample_predictions():
    """Create sample predictions for testing."""
    np.random.seed(42)
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1, 0, 1])
    y_pred = np.array([0, 0, 1, 0, 0, 1, 0, 1, 1, 1])
    y_proba = np.random.rand(10, 2)
    # Normalize probabilities
    y_proba = y_proba / y_proba.sum(axis=1, keepdims=True)
    return y_true, y_pred, y_proba


def test_evaluate_model_returns_dict(sample_predictions):
    """Test that evaluate_model returns a dictionary."""
    y_true, y_pred, y_proba = sample_predictions
    metrics = evaluate_model(y_true, y_pred, y_proba)

    assert isinstance(metrics, dict)


def test_evaluate_model_contains_required_metrics(sample_predictions):
    """Test that all required metrics are present."""
    y_true, y_pred, y_proba = sample_predictions
    metrics = evaluate_model(y_true, y_pred, y_proba)

    required_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
    for metric in required_metrics:
        assert metric in metrics


def test_evaluate_model_without_probabilities(sample_predictions):
    """Test evaluation without probabilities."""
    y_true, y_pred, _ = sample_predictions
    metrics = evaluate_model(y_true, y_pred, y_proba=None)

    # Should have all metrics except roc_auc
    assert 'accuracy' in metrics
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'f1_score' in metrics
    assert 'roc_auc' not in metrics


def test_evaluate_model_metric_ranges(sample_predictions):
    """Test that all metrics are in valid range [0, 1]."""
    y_true, y_pred, y_proba = sample_predictions
    metrics = evaluate_model(y_true, y_pred, y_proba)

    for metric_name, value in metrics.items():
        assert 0 <= value <= 1, f"{metric_name} out of range: {value}"


def test_evaluate_model_perfect_predictions():
    """Test evaluation with perfect predictions."""
    y_true = np.array([0, 0, 1, 1, 0, 1])
    y_pred = np.array([0, 0, 1, 1, 0, 1])
    y_proba = np.array([
        [1.0, 0.0], [1.0, 0.0], [0.0, 1.0],
        [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]
    ])

    metrics = evaluate_model(y_true, y_pred, y_proba)

    # Perfect predictions should give 1.0 for all metrics
    assert metrics['accuracy'] == 1.0
    assert metrics['precision'] == 1.0
    assert metrics['recall'] == 1.0
    assert metrics['f1_score'] == 1.0
    assert metrics['roc_auc'] == 1.0


def test_evaluate_model_all_zeros():
    """Test evaluation when all predictions are zero."""
    y_true = np.array([0, 0, 1, 1, 0, 1])
    y_pred = np.array([0, 0, 0, 0, 0, 0])

    metrics = evaluate_model(y_true, y_pred, y_proba=None)

    # Should handle zero division gracefully
    assert 0 <= metrics['precision'] <= 1
    assert metrics['recall'] == 0  # No positive predictions


def test_print_evaluation_results(sample_predictions, capsys):
    """Test that print_evaluation_results produces output."""
    y_true, y_pred, y_proba = sample_predictions
    metrics = evaluate_model(y_true, y_pred, y_proba)

    print_evaluation_results(metrics)

    captured = capsys.readouterr()
    assert "Model Evaluation Results" in captured.out
    assert "Accuracy" in captured.out
    assert "Precision" in captured.out


def test_evaluate_model_with_binary_class():
    """Test evaluation with binary classification."""
    # Simple binary case
    y_true = np.array([0, 1, 0, 1])
    y_pred = np.array([0, 1, 1, 1])
    y_proba = np.array([[0.9, 0.1], [0.2, 0.8], [0.4, 0.6], [0.3, 0.7]])

    metrics = evaluate_model(y_true, y_pred, y_proba)

    assert metrics['accuracy'] == 0.75  # 3 out of 4 correct
    assert 0 <= metrics['roc_auc'] <= 1
