# Hypo-Churn

A machine learning project for customer churn prediction and analysis.

## Project Structure

```
hypo-churn/
├── src/hypo_churn/          # Main package source code
│   ├── __init__.py
│   ├── data_preprocessing.py # Data cleaning and preprocessing
│   ├── models.py            # ML models for churn prediction
│   └── evaluation.py        # Model evaluation utilities
├── notebooks/               # Jupyter notebooks for exploration
├── data/                    # Data directory
│   ├── raw/                # Raw data files
│   ├── processed/          # Processed data files
│   └── external/           # External data sources
├── tests/                   # Unit tests
├── models/                  # Trained model artifacts
├── configs/                 # Configuration files
├── pyproject.toml          # Project configuration
└── requirements.txt        # Python dependencies
```

## Setup

### Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

Or install the package in editable mode with dev dependencies:

```bash
pip install -e ".[dev]"
```

## Development

### Running tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/hypo_churn --cov-report=html

# Run a specific test file
pytest tests/test_data_preprocessing.py
```

### Code formatting and linting

```bash
# Format code with black
black src/ tests/

# Lint code with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### Running Jupyter notebooks

```bash
jupyter notebook
```

## Usage

```python
from hypo_churn.data_preprocessing import load_data, clean_data, split_features_target
from hypo_churn.models import ChurnPredictor
from hypo_churn.evaluation import evaluate_model, print_evaluation_results

# Load and preprocess data
df = load_data('data/raw/customer_data.csv')
df_clean = clean_data(df)
X, y = split_features_target(df_clean, 'churned')

# Train model
predictor = ChurnPredictor(model_type='random_forest')
predictor.train(X_train, y_train)

# Evaluate
y_pred = predictor.predict(X_test)
y_proba = predictor.predict_proba(X_test)
metrics = evaluate_model(y_test, y_pred, y_proba)
print_evaluation_results(metrics)
```
