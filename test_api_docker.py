#!/usr/bin/env python3
"""Test script for the Hypo-Churn REST API running in Docker."""

import requests
import json
import sys


def test_health():
    """Test health endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health: {data['status']}")
        print(f"   Model loaded: {data['model_loaded']}")
        print(f"   Version: {data['version']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_model_info():
    """Test model info endpoint."""
    print("\n🔍 Testing model info endpoint...")
    try:
        response = requests.get("http://localhost:8000/model/info", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Model Info:")
        print(f"   Name: {data['model_name']}")
        print(f"   Type: {data['model_type']}")
        print(f"   Features: {data['features_count']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Model info failed: {e}")
        return False


def test_prediction():
    """Test single prediction endpoint."""
    print("\n🔍 Testing single prediction...")

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

    try:
        response = requests.post(
            "http://localhost:8000/predict",
            json=customer,
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        print(f"✅ Prediction Result:")
        print(f"   Prediction: {data['prediction_label']}")
        print(f"   Churn Probability: {data['churn_probability']:.2%}")
        print(f"   Confidence: {data['confidence']:.2%}")
        print(f"   Risk Level: {data['risk_level']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Prediction failed: {e}")
        return False


def test_batch_prediction():
    """Test batch prediction endpoint."""
    print("\n🔍 Testing batch prediction...")

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
                "credit_score": 800,
                "Geography": "Germany",
                "Gender": "Male",
                "Age": 35,
                "loan_age_years": 5,
                "outstanding_loan_balance": 50000.0,
                "num_bank_products": 3,
                "has_credit_card": 1,
                "online_banking_active": 1,
                "annual_income": 150000.0,
                "monthly_income": 12500.0,
                "estimated_property_value": 500000.0,
                "ltv_ratio": 0.1,
                "payment_to_income_ratio": 0.2,
                "risk_score": 0.05,
                "balance_per_product": 16666.67
            }
        ]
    }

    try:
        response = requests.post(
            "http://localhost:8000/predict/batch",
            json=customers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        print(f"✅ Batch Prediction Result:")
        print(f"   Total Customers: {data['total_customers']}")
        print(f"   Churned Count: {data['churned_count']}")
        print(f"   Churn Rate: {data['churn_rate']:.2%}")
        print(f"   Individual Predictions:")

        for i, pred in enumerate(data['predictions'], 1):
            print(f"      Customer {i}: {pred['prediction_label']} "
                  f"({pred['churn_probability']:.2%}, {pred['risk_level']})")

        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Batch prediction failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Hypo-Churn API Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Model Info", test_model_info()))
    results.append(("Single Prediction", test_prediction()))
    results.append(("Batch Prediction", test_batch_prediction()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    # Exit code
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
