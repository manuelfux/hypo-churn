#!/usr/bin/env python
"""
Command-line script for making churn predictions.

Usage:
    python scripts/predict.py --input data.csv --output predictions.csv
    python scripts/predict.py --single '{"Age": 35, "credit_score": 650, ...}'
"""

import argparse
import json
import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from hypo_churn.inference import load_inference_engine


def predict_from_csv(input_path: str, output_path: str, model_name: str = 'best_xgboost_model'):
    """
    Make predictions from a CSV file.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output CSV file
        model_name: Name of the model to use
    """
    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"  Loaded {len(df)} samples")

    print(f"\nLoading model: {model_name}...")
    inference = load_inference_engine(model_name)
    print("  Model loaded successfully")

    print("\nMaking predictions...")
    predictions = inference.predict_with_details(df)

    # Add predictions to DataFrame
    df['prediction'] = [p['prediction'] for p in predictions]
    df['prediction_label'] = [p['prediction_label'] for p in predictions]
    df['churn_probability'] = [p['churn_probability'] for p in predictions]
    df['confidence'] = [p['confidence'] for p in predictions]
    df['risk_level'] = [p['risk_level'] for p in predictions]

    # Save results
    df.to_csv(output_path, index=False)
    print(f"\n✓ Predictions saved to {output_path}")

    # Print summary
    print("\n" + "="*70)
    print("PREDICTION SUMMARY")
    print("="*70)
    print(f"Total samples: {len(df)}")
    print(f"Predicted churners: {(df['prediction'] == 1).sum()} ({(df['prediction'] == 1).mean():.1%})")
    print(f"Predicted non-churners: {(df['prediction'] == 0).sum()} ({(df['prediction'] == 0).mean():.1%})")
    print(f"\nRisk Level Distribution:")
    print(df['risk_level'].value_counts().sort_index())


def predict_single(data_json: str, model_name: str = 'best_xgboost_model'):
    """
    Make prediction for a single sample.

    Args:
        data_json: JSON string with sample data
        model_name: Name of the model to use
    """
    print("Parsing input data...")
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

    print(f"\nLoading model: {model_name}...")
    inference = load_inference_engine(model_name)

    print("\nMaking prediction...")
    result = inference.predict_with_details(data)[0]

    print("\n" + "="*70)
    print("PREDICTION RESULT")
    print("="*70)
    print(f"Prediction: {result['prediction_label']}")
    print(f"Churn Probability: {result['churn_probability']:.2%}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Risk Level: {result['risk_level']}")
    print("="*70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Make churn predictions using trained models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Predict from CSV file
  python scripts/predict.py --input customers.csv --output predictions.csv

  # Single prediction
  python scripts/predict.py --single '{"Age": 35, "credit_score": 650}'

  # Use specific model
  python scripts/predict.py --input data.csv --output out.csv --model best_model_random_forest
        """
    )

    parser.add_argument(
        '--input', '-i',
        help='Input CSV file with customer data'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output CSV file for predictions'
    )
    parser.add_argument(
        '--single', '-s',
        help='JSON string with single customer data'
    )
    parser.add_argument(
        '--model', '-m',
        default='best_xgboost_model',
        help='Model name to use (default: best_xgboost_model)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.single:
        predict_single(args.single, args.model)
    elif args.input and args.output:
        predict_from_csv(args.input, args.output, args.model)
    else:
        parser.print_help()
        print("\nError: You must specify either --single or both --input and --output")
        sys.exit(1)


if __name__ == '__main__':
    main()
