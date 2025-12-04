# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip and setuptools (required for editable installs)
pip install --upgrade pip setuptools

# Install package in editable mode (REQUIRED before running tests)
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"

# Alternative: Install using requirements.txt
pip install -r requirements.txt
```

**IMPORTANT**: The package must be installed in editable mode (`pip install -e .`) before running tests, otherwise pytest will fail with `ModuleNotFoundError: No module named 'hypo_churn'`.

### Dataset Management
```bash
# Download datasets from Kaggle (requires Kaggle API token)
python scripts/download_datasets.py --banking        # Primary banking churn dataset
python scripts/download_datasets.py --credit-card    # Credit card churn dataset
python scripts/download_datasets.py --telco          # Telco churn (for comparison)
python scripts/download_datasets.py --all            # Download all datasets

# Kaggle API setup (one-time)
pip install kaggle
# Get token from: https://www.kaggle.com/settings/account
# Save to: ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

See `scripts/README.md` and `QUICKSTART_DATASETS.md` for detailed dataset information.

### Testing
```bash
# Run all tests (coverage enabled by default in pyproject.toml)
pytest

# Run tests with HTML coverage report
pytest --cov=src/hypo_churn --cov-report=html

# Run a specific test file
pytest tests/test_data_preprocessing.py

# Run a specific test function
pytest tests/test_data_preprocessing.py::test_clean_data_removes_duplicates
```

**Note**: Coverage reporting is configured by default in `pyproject.toml` with `--cov=src/hypo_churn --cov-report=term-missing`.

### Code Quality
```bash
# Format code with black (line length: 100)
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Jupyter Notebooks
```bash
# Start Jupyter notebook server
jupyter notebook

# Run notebook from command line
jupyter nbconvert --execute notebooks/example.ipynb
```

## Architecture

### Project Structure
- **src/hypo_churn/**: Main package containing all production code
  - **data_preprocessing.py**: Data loading, cleaning, and feature/target splitting
  - **models.py**: ML model implementations (ChurnPredictor class with RandomForest and LogisticRegression)
  - **evaluation.py**: Model evaluation metrics and result formatting
- **tests/**: Unit tests mirroring the src/ structure
- **notebooks/**: Jupyter notebooks for exploratory data analysis and experimentation
  - **01_banking_churn_eda.ipynb**: Banking churn dataset analysis
- **scripts/**: Utility scripts
  - **download_datasets.py**: Automated Kaggle dataset downloads
- **data/**: Data storage with subdirectories:
  - **raw/**: Original, immutable data (datasets download here)
  - **processed/**: Cleaned and transformed data ready for modeling
  - **external/**: External data sources
- **models/**: Saved model artifacts (.pkl, .h5, etc.)
- **configs/**: Configuration files for experiments and parameters

### Data Flow
1. **Data Acquisition**: Use `scripts/download_datasets.py` to fetch public datasets from Kaggle
2. **Data Loading & Preprocessing**: `data_preprocessing.py` loads raw data, cleans it, and splits features/target
3. **Model Training**: `models.py` contains ChurnPredictor class that wraps sklearn models
4. **Evaluation**: `evaluation.py` computes metrics (accuracy, precision, recall, F1, ROC-AUC)

### Key Design Patterns
- **ChurnPredictor class**: Abstracts different model types behind a common interface
  - Supports 'random_forest' and 'logistic_regression' via model_type parameter
  - Provides train(), predict(), and predict_proba() methods
- **Functional preprocessing**: Data preprocessing functions are stateless and composable
- **Type hints**: All functions use type hints for better code documentation and IDE support

### Configuration
- **pyproject.toml**: Project metadata, dependencies, and tool configurations
  - Black: 100 character line length
  - Pytest: Runs tests from tests/ directory with coverage reporting
  - Target Python version: 3.8+

### Testing Conventions
- Test files follow `test_*.py` naming convention
- Test functions start with `test_`
- Use pytest fixtures for common test data setup
- Aim for high coverage of core modules (data_preprocessing, models, evaluation)

### Data Science Workflow
1. Download datasets using `python scripts/download_datasets.py --banking` (or other options)
2. Place raw data in `data/raw/` (automatically done by download script)
3. Use notebooks for initial exploration and prototyping (e.g., `01_banking_churn_eda.ipynb`)
4. Move reusable code from notebooks to modules in `src/hypo_churn/`
5. Write tests for production code in `tests/`
6. Save trained models to `models/` directory
7. Keep processed/cleaned datasets in `data/processed/`

### Project Context
This is a **mortgage churn prediction** project that uses publicly available banking and financial churn datasets as proxies. The datasets can be adapted for mortgage-specific use cases through feature engineering (LTV ratio, payment-to-income ratio, loan age, etc.). See `QUICKSTART_DATASETS.md` for details on adapting banking features to mortgage context.
