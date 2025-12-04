"""
Simple script to test the API endpoints.

Make sure the API is running first:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_model_info():
    """Test model info endpoint."""
    print("Testing /model/info endpoint...")
    response = requests.get(f"{BASE_URL}/model/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_single_prediction():
    """Test single prediction endpoint."""
    print("Testing /predict endpoint...")

    customer = {
        "credit_score": 650,
        "Geography": "France",
        "Gender": "Female",
        "Age": 42,
        "loan_age_years": 2,
        "outstanding_loan_balance": 0.0,
        "num_bank_products": 1,
        "has_credit_card": 1,
        "online_banking_active": 1,
        "annual_income": 101348.88,
        "monthly_income": 8445.74,
        "estimated_property_value": 354721.08,
        "ltv_ratio": 0.0,
        "payment_to_income_ratio": 0.0,
        "risk_score": 0.168,
        "balance_per_product": 0.0
    }

    response = requests.post(f"{BASE_URL}/predict", json=customer)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_batch_prediction():
    """Test batch prediction endpoint."""
    print("Testing /predict/batch endpoint...")

    customers = {
        "customers": [
            {
                "credit_score": 650,
                "Geography": "France",
                "Gender": "Female",
                "Age": 42,
                "loan_age_years": 2,
                "outstanding_loan_balance": 0.0,
                "num_bank_products": 1,
                "has_credit_card": 1,
                "online_banking_active": 1,
                "annual_income": 101348.88,
                "monthly_income": 8445.74,
                "estimated_property_value": 354721.08,
                "ltv_ratio": 0.0,
                "payment_to_income_ratio": 0.0,
                "risk_score": 0.168,
                "balance_per_product": 0.0
            },
            {
                "credit_score": 700,
                "Geography": "Spain",
                "Gender": "Male",
                "Age": 35,
                "loan_age_years": 5,
                "outstanding_loan_balance": 50000.0,
                "num_bank_products": 2,
                "has_credit_card": 1,
                "online_banking_active": 0,
                "annual_income": 85000.0,
                "monthly_income": 7083.33,
                "estimated_property_value": 297500.0,
                "ltv_ratio": 0.168,
                "payment_to_income_ratio": 0.095,
                "risk_score": 0.25,
                "balance_per_product": 25000.0
            }
        ]
    }

    response = requests.post(f"{BASE_URL}/predict/batch", json=customers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_probability_get():
    """Test probability GET endpoint."""
    print("Testing /predict/probability endpoint...")

    params = {
        "credit_score": 650,
        "Geography": "France",
        "Gender": "Female",
        "Age": 42,
        "loan_age_years": 2,
        "outstanding_loan_balance": 0.0,
        "num_bank_products": 1,
        "has_credit_card": 1,
        "online_banking_active": 1,
        "annual_income": 101348.88
    }

    response = requests.get(f"{BASE_URL}/predict/probability", params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


if __name__ == "__main__":
    print("="*70)
    print("API TESTING")
    print("="*70)
    print()

    try:
        test_health()
        test_model_info()
        test_single_prediction()
        test_batch_prediction()
        test_probability_get()

        print("="*70)
        print("All tests completed!")
        print("="*70)

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Make sure it's running:")
        print("  uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
