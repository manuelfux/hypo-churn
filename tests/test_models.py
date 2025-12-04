"""Tests for models module."""

import pytest
import pandas as pd
import numpy as np
from hypo_churn.models import ChurnPredictor


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    np.random.seed(42)
    X = pd.DataFrame({
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100)
    })
    y = pd.Series(np.random.randint(0, 2, 100))
    return X, y


def test_churn_predictor_initialization_random_forest():
    """Test ChurnPredictor initialization with random forest."""
    predictor = ChurnPredictor(model_type='random_forest')
    assert predictor.model_type == 'random_forest'
    assert predictor.model is not None


def test_churn_predictor_initialization_logistic_regression():
    """Test ChurnPredictor initialization with logistic regression."""
    predictor = ChurnPredictor(model_type='logistic_regression')
    assert predictor.model_type == 'logistic_regression'
    assert predictor.model is not None


def test_churn_predictor_invalid_model_type():
    """Test that invalid model type raises ValueError."""
    with pytest.raises(ValueError):
        ChurnPredictor(model_type='invalid_model')


def test_churn_predictor_train(sample_data):
    """Test that model can be trained."""
    X, y = sample_data
    predictor = ChurnPredictor(model_type='random_forest')

    # Should not raise any exception
    predictor.train(X, y)


def test_churn_predictor_predict(sample_data):
    """Test that model can make predictions."""
    X, y = sample_data
    predictor = ChurnPredictor(model_type='random_forest')
    predictor.train(X, y)

    predictions = predictor.predict(X)

    assert len(predictions) == len(X)
    assert all(pred in [0, 1] for pred in predictions)


def test_churn_predictor_predict_proba(sample_data):
    """Test that model can predict probabilities."""
    X, y = sample_data
    predictor = ChurnPredictor(model_type='random_forest')
    predictor.train(X, y)

    probabilities = predictor.predict_proba(X)

    assert probabilities.shape == (len(X), 2)
    assert all(0 <= prob <= 1 for prob in probabilities.flatten())
    # Check that probabilities sum to 1 for each sample
    assert all(abs(sum(probabilities[i]) - 1.0) < 1e-5 for i in range(len(probabilities)))


def test_churn_predictor_predict_before_train(sample_data):
    """Test that prediction fails gracefully before training."""
    X, _ = sample_data
    predictor = ChurnPredictor(model_type='random_forest')

    # Should raise an exception (model not fitted)
    with pytest.raises(Exception):
        predictor.predict(X)


def test_both_model_types_produce_valid_predictions(sample_data):
    """Test that both model types produce valid predictions."""
    X, y = sample_data

    for model_type in ['random_forest', 'logistic_regression']:
        predictor = ChurnPredictor(model_type=model_type)
        predictor.train(X, y)

        predictions = predictor.predict(X)
        probabilities = predictor.predict_proba(X)

        assert len(predictions) == len(X)
        assert probabilities.shape == (len(X), 2)
