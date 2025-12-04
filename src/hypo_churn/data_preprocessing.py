"""Data preprocessing utilities for churn analysis."""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def load_data(filepath: str) -> pd.DataFrame:
    """
    Load data from a CSV file.

    Args:
        filepath: Path to the CSV file

    Returns:
        DataFrame containing the loaded data
    """
    return pd.read_csv(filepath)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the input dataframe by handling missing values and duplicates.

    Args:
        df: Input dataframe

    Returns:
        Cleaned dataframe
    """
    df_clean = df.copy()
    # Remove duplicates
    df_clean = df_clean.drop_duplicates()
    return df_clean


def split_features_target(
    df: pd.DataFrame,
    target_column: str
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Split dataframe into features and target.

    Args:
        df: Input dataframe
        target_column: Name of the target column

    Returns:
        Tuple of (features, target)
    """
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return X, y
