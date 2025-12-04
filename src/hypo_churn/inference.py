"""Inference module for making predictions with trained models."""

import pickle
from pathlib import Path
from typing import Union, Dict, List
import pandas as pd
import numpy as np


class ChurnInference:
    """Class for making churn predictions with trained models."""

    def __init__(self, model_path: Union[str, Path], feature_names_path: Union[str, Path] = None):
        """
        Initialize the inference engine.

        Args:
            model_path: Path to the trained model pickle file
            feature_names_path: Path to feature names pickle file (optional)
        """
        self.model_path = Path(model_path)
        self.feature_names_path = Path(feature_names_path) if feature_names_path else None

        # Load model
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)

        # Load feature names if provided
        self.feature_names = None
        if self.feature_names_path and self.feature_names_path.exists():
            with open(self.feature_names_path, 'rb') as f:
                self.feature_names = pickle.load(f)

    def predict(self, data: Union[pd.DataFrame, Dict, List[Dict]]) -> np.ndarray:
        """
        Make binary predictions (0 or 1).

        Args:
            data: Input data (DataFrame, dict, or list of dicts)

        Returns:
            Array of predictions (0 = not churned, 1 = churned)
        """
        df = self._prepare_data(data)
        predictions = self.model.predict(df)
        return predictions

    def predict_proba(self, data: Union[pd.DataFrame, Dict, List[Dict]]) -> np.ndarray:
        """
        Predict probabilities for each class.

        Args:
            data: Input data (DataFrame, dict, or list of dicts)

        Returns:
            Array of probabilities, shape (n_samples, 2)
            Column 0: probability of not churning
            Column 1: probability of churning
        """
        df = self._prepare_data(data)
        probabilities = self.model.predict_proba(df)
        return probabilities

    def predict_with_details(self, data: Union[pd.DataFrame, Dict, List[Dict]]) -> List[Dict]:
        """
        Make predictions with detailed output.

        Args:
            data: Input data (DataFrame, dict, or list of dicts)

        Returns:
            List of dicts with prediction details for each sample
        """
        df = self._prepare_data(data)
        predictions = self.model.predict(df)
        probabilities = self.model.predict_proba(df)

        results = []
        for i, (pred, proba) in enumerate(zip(predictions, probabilities)):
            result = {
                'prediction': int(pred),
                'prediction_label': 'Churned' if pred == 1 else 'Not Churned',
                'churn_probability': float(proba[1]),
                'confidence': float(max(proba)),
                'risk_level': self._get_risk_level(proba[1])
            }
            results.append(result)

        return results

    def _prepare_data(self, data: Union[pd.DataFrame, Dict, List[Dict]]) -> pd.DataFrame:
        """
        Prepare input data for prediction.

        Args:
            data: Input data in various formats

        Returns:
            Prepared DataFrame
        """
        # Convert to DataFrame if needed
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

        # Handle categorical encoding if needed
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

        # Ensure all required features are present
        if self.feature_names:
            missing_features = set(self.feature_names) - set(df.columns)
            if missing_features:
                # Add missing features with zeros
                for feature in missing_features:
                    df[feature] = 0

            # Reorder columns to match training
            df = df[self.feature_names]

        return df

    def _get_risk_level(self, churn_probability: float) -> str:
        """
        Determine risk level based on churn probability.

        Args:
            churn_probability: Probability of churning

        Returns:
            Risk level string
        """
        if churn_probability < 0.3:
            return 'Low'
        elif churn_probability < 0.6:
            return 'Medium'
        elif churn_probability < 0.8:
            return 'High'
        else:
            return 'Critical'


def load_inference_engine(
    model_name: str = 'best_xgboost_model',
    models_dir: Union[str, Path] = None
) -> ChurnInference:
    """
    Convenience function to load the inference engine.

    Args:
        model_name: Name of the model file (without .pkl extension)
        models_dir: Directory containing model files (default: project_root/models)

    Returns:
        Initialized ChurnInference instance
    """
    if models_dir is None:
        # Assume we're in src/hypo_churn, go up to project root
        project_root = Path(__file__).parent.parent.parent
        models_dir = project_root / 'models'
    else:
        models_dir = Path(models_dir)

    model_path = models_dir / f'{model_name}.pkl'

    # Try to find feature names file
    feature_names_files = [
        'xgboost_feature_names.pkl',
        'feature_names.pkl'
    ]

    feature_names_path = None
    for fname in feature_names_files:
        fpath = models_dir / fname
        if fpath.exists():
            feature_names_path = fpath
            break

    return ChurnInference(model_path, feature_names_path)
