"""Machine learning models for churn prediction."""

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from typing import Tuple, Any
import pandas as pd
import numpy as np


class ChurnPredictor:
    """Base class for churn prediction models."""

    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize the churn predictor.

        Args:
            model_type: Type of model to use ('random_forest' or 'logistic_regression')
        """
        self.model_type = model_type
        self.model = self._initialize_model()

    def _initialize_model(self) -> Any:
        """Initialize the ML model based on model_type."""
        if self.model_type == "random_forest":
            return RandomForestClassifier(random_state=42)
        elif self.model_type == "logistic_regression":
            return LogisticRegression(random_state=42, max_iter=1000)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Train the model.

        Args:
            X: Feature matrix
            y: Target vector
        """
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions.

        Args:
            X: Feature matrix

        Returns:
            Predicted labels
        """
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict probabilities.

        Args:
            X: Feature matrix

        Returns:
            Predicted probabilities
        """
        return self.model.predict_proba(X)
