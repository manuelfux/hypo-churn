"""Comprehensive tests for data preprocessing module."""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from hypo_churn.data_preprocessing import load_data, clean_data, split_features_target


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file for testing."""
    data = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': [5, 6, 7, 8],
        'target': [0, 1, 0, 1]
    })

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        data.to_csv(f.name, index=False)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [10, 20, 30, 40, 50],
        'target': [0, 1, 0, 1, 0]
    })


@pytest.fixture
def dataframe_with_duplicates():
    """Create a DataFrame with duplicate rows."""
    return pd.DataFrame({
        'A': [1, 1, 2, 3],
        'B': [4, 4, 5, 6],
        'C': [7, 7, 8, 9]
    })


# Tests for load_data
def test_load_data_returns_dataframe(sample_csv_file):
    """Test that load_data returns a DataFrame."""
    df = load_data(sample_csv_file)
    assert isinstance(df, pd.DataFrame)


def test_load_data_correct_shape(sample_csv_file):
    """Test that loaded data has correct shape."""
    df = load_data(sample_csv_file)
    assert df.shape == (4, 3)


def test_load_data_correct_columns(sample_csv_file):
    """Test that loaded data has correct columns."""
    df = load_data(sample_csv_file)
    assert list(df.columns) == ['A', 'B', 'target']


def test_load_data_file_not_found():
    """Test that load_data raises error for non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_data('non_existent_file.csv')


# Tests for clean_data
def test_clean_data_returns_dataframe(sample_dataframe):
    """Test that clean_data returns a DataFrame."""
    result = clean_data(sample_dataframe)
    assert isinstance(result, pd.DataFrame)


def test_clean_data_removes_duplicates(dataframe_with_duplicates):
    """Test that clean_data removes duplicate rows."""
    result = clean_data(dataframe_with_duplicates)
    assert len(result) == 3
    assert not result.duplicated().any()


def test_clean_data_preserves_original(sample_dataframe):
    """Test that clean_data doesn't modify original DataFrame."""
    original_len = len(sample_dataframe)
    clean_data(sample_dataframe)
    assert len(sample_dataframe) == original_len


def test_clean_data_keeps_all_columns(sample_dataframe):
    """Test that clean_data preserves all columns."""
    result = clean_data(sample_dataframe)
    assert list(result.columns) == list(sample_dataframe.columns)


def test_clean_data_empty_dataframe():
    """Test clean_data with empty DataFrame."""
    df = pd.DataFrame()
    result = clean_data(df)
    assert len(result) == 0


def test_clean_data_no_duplicates(sample_dataframe):
    """Test clean_data when there are no duplicates."""
    result = clean_data(sample_dataframe)
    assert len(result) == len(sample_dataframe)


# Tests for split_features_target
def test_split_features_target_returns_tuple(sample_dataframe):
    """Test that split_features_target returns a tuple."""
    result = split_features_target(sample_dataframe, 'target')
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_split_features_target_correct_shapes(sample_dataframe):
    """Test that features and target have correct shapes."""
    X, y = split_features_target(sample_dataframe, 'target')
    assert X.shape == (5, 2)  # 5 rows, 2 features
    assert y.shape == (5,)  # 5 rows


def test_split_features_target_removes_target_from_features(sample_dataframe):
    """Test that target column is removed from features."""
    X, y = split_features_target(sample_dataframe, 'target')
    assert 'target' not in X.columns


def test_split_features_target_preserves_feature_columns(sample_dataframe):
    """Test that all non-target columns are preserved."""
    X, y = split_features_target(sample_dataframe, 'target')
    expected_features = ['feature1', 'feature2']
    assert list(X.columns) == expected_features


def test_split_features_target_correct_target_values(sample_dataframe):
    """Test that target values are correct."""
    X, y = split_features_target(sample_dataframe, 'target')
    assert list(y) == [0, 1, 0, 1, 0]


def test_split_features_target_invalid_column():
    """Test that invalid target column raises KeyError."""
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    with pytest.raises(KeyError):
        split_features_target(df, 'non_existent_column')


def test_split_features_target_returns_correct_types(sample_dataframe):
    """Test that returned types are DataFrame and Series."""
    X, y = split_features_target(sample_dataframe, 'target')
    assert isinstance(X, pd.DataFrame)
    assert isinstance(y, pd.Series)


# Integration tests
def test_full_preprocessing_pipeline(sample_csv_file):
    """Test complete preprocessing pipeline."""
    # Load
    df = load_data(sample_csv_file)

    # Clean
    df_clean = clean_data(df)

    # Split
    X, y = split_features_target(df_clean, 'target')

    # Verify
    assert isinstance(X, pd.DataFrame)
    assert isinstance(y, pd.Series)
    assert len(X) == len(y)
    assert 'target' not in X.columns
