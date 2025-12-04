"""
Example script showing how to use the inference module.
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from hypo_churn.inference import load_inference_engine


def example_single_prediction():
    """Example: Make prediction for a single customer."""
    print("="*70)
    print("EXAMPLE 1: Single Customer Prediction")
    print("="*70)

    # Load the inference engine
    inference = load_inference_engine()

    # Sample customer data
    customer = {
        'credit_score': 650,
        'Geography': 'France',
        'Gender': 'Female',
        'Age': 42,
        'loan_age_years': 2,
        'outstanding_loan_balance': 0.0,
        'num_bank_products': 1,
        'has_credit_card': 1,
        'online_banking_active': 1,
        'annual_income': 101348.88,
        'monthly_income': 8445.74,
        'estimated_property_value': 354721.08,
        'ltv_ratio': 0.0,
        'payment_to_income_ratio': 0.0,
        'risk_score': 0.168,
        'balance_per_product': 0.0
    }

    # Make prediction
    result = inference.predict_with_details(customer)[0]

    print(f"\nCustomer Profile:")
    print(f"  Age: {customer['Age']}")
    print(f"  Credit Score: {customer['credit_score']}")
    print(f"  Annual Income: ${customer['annual_income']:,.2f}")

    print(f"\nPrediction:")
    print(f"  Result: {result['prediction_label']}")
    print(f"  Churn Probability: {result['churn_probability']:.2%}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Risk Level: {result['risk_level']}")


def example_batch_prediction():
    """Example: Make predictions for multiple customers."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Batch Prediction")
    print("="*70)

    # Load the inference engine
    inference = load_inference_engine()

    # Sample customers
    customers = pd.DataFrame({
        'credit_score': [650, 700, 580],
        'Geography': ['France', 'Spain', 'Germany'],
        'Gender': ['Female', 'Male', 'Female'],
        'Age': [42, 35, 50],
        'loan_age_years': [2, 5, 8],
        'outstanding_loan_balance': [0.0, 50000.0, 120000.0],
        'num_bank_products': [1, 2, 1],
        'has_credit_card': [1, 1, 0],
        'online_banking_active': [1, 0, 1],
        'annual_income': [101348.88, 85000.0, 60000.0],
        'monthly_income': [8445.74, 7083.33, 5000.0],
        'estimated_property_value': [354721.08, 297500.0, 210000.0],
        'ltv_ratio': [0.0, 0.168, 0.571],
        'payment_to_income_ratio': [0.0, 0.095, 0.333],
        'risk_score': [0.168, 0.25, 0.45],
        'balance_per_product': [0.0, 25000.0, 120000.0]
    })

    # Make predictions
    results = inference.predict_with_details(customers)

    print(f"\nProcessed {len(customers)} customers:")
    print("\nResults:")
    for i, result in enumerate(results):
        print(f"\nCustomer {i+1}:")
        print(f"  Prediction: {result['prediction_label']}")
        print(f"  Churn Probability: {result['churn_probability']:.2%}")
        print(f"  Risk Level: {result['risk_level']}")


def example_probability_only():
    """Example: Get only probabilities."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Probability Only")
    print("="*70)

    inference = load_inference_engine()

    customer = {
        'credit_score': 650,
        'Geography': 'France',
        'Gender': 'Female',
        'Age': 42,
        'loan_age_years': 2,
        'outstanding_loan_balance': 0.0,
        'num_bank_products': 1,
        'has_credit_card': 1,
        'online_banking_active': 1,
        'annual_income': 101348.88,
        'monthly_income': 8445.74,
        'estimated_property_value': 354721.08,
        'ltv_ratio': 0.0,
        'payment_to_income_ratio': 0.0,
        'risk_score': 0.168,
        'balance_per_product': 0.0
    }

    # Get probabilities
    proba = inference.predict_proba(customer)

    print(f"\nProbabilities:")
    print(f"  Not Churning: {proba[0][0]:.2%}")
    print(f"  Churning: {proba[0][1]:.2%}")


if __name__ == '__main__':
    # Run all examples
    example_single_prediction()
    example_batch_prediction()
    example_probability_only()

    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70)
