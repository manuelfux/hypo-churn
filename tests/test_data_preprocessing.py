"""Tests for data preprocessing module."""

import pytest
import pandas as pd
import numpy as np
from hypo_churn.data_preprocessing import (
    clean_data,
    split_features_target,
)


def test_clean_data_removes_duplicates():
    """Test that clean_data removes duplicate rows."""
    df = pd.DataFrame({
        'A': [1, 1, 2, 3],
        'B': [4, 4, 5, 6]
    })
    result = clean_data(df)
    assert len(result) == 3
    assert not result.duplicated().any()


def test_split_features_target():
    """Test splitting features and target."""
    df = pd.DataFrame({
        'feature1': [1, 2, 3],
        'feature2': [4, 5, 6],
        'target': [0, 1, 0]
    })
    X, y = split_features_target(df, 'target')
    assert X.shape == (3, 2)
    assert y.shape == (3,)
    assert 'target' not in X.columns
    assert list(y) == [0, 1, 0]
