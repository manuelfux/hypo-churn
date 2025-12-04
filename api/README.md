# Mortgage Churn Prediction API

FastAPI REST API for predicting mortgage customer churn.

## Quick Start

### 1. Start the API

```bash
# From project root
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

### 2. Test the API

```bash
python api/test_api.py
```

---

## API Endpoints

### General

#### `GET /`
Root endpoint with API information.

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

#### `GET /model/info`
Get model information.

**Response:**
```json
{
  "model_name": "best_xgboost_model",
  "model_type": "XGBoost Classifier",
  "features_count": 18,
  "available": true
}
```

---

### Predictions

#### `POST /predict`
Make a churn prediction for a single customer.

**Request Body:**
```json
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
}
```

**Response:**
```json
{
  "prediction": 1,
  "prediction_label": "Churned",
  "churn_probability": 0.75,
  "confidence": 0.75,
  "risk_level": "High"
}
```

#### `POST /predict/batch`
Make predictions for multiple customers (max 1000).

**Request Body:**
```json
{
  "customers": [
    { /* customer 1 data */ },
    { /* customer 2 data */ }
  ]
}
```

**Response:**
```json
{
  "predictions": [
    {
      "prediction": 1,
      "prediction_label": "Churned",
      "churn_probability": 0.75,
      "confidence": 0.75,
      "risk_level": "High"
    }
  ],
  "total_customers": 2,
  "churned_count": 1,
  "churn_rate": 0.5
}
```

#### `GET /predict/probability`
Quick probability check via query parameters.

**Query Parameters:**
- `credit_score`: float
- `Geography`: string
- `Gender`: string
- `Age`: int
- `loan_age_years`: float
- `outstanding_loan_balance`: float
- `num_bank_products`: int
- `has_credit_card`: int (0 or 1)
- `online_banking_active`: int (0 or 1)
- `annual_income`: float

**Example:**
```
GET /predict/probability?credit_score=650&Geography=France&Gender=Female&Age=42&loan_age_years=2&outstanding_loan_balance=0&num_bank_products=1&has_credit_card=1&online_banking_active=1&annual_income=101348.88
```

**Response:**
```json
{
  "churn_probability": 0.75,
  "risk_level": "High"
}
```

---

## Usage Examples

### cURL

**Single Prediction:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Python (requests)

```python
import requests

# Single prediction
url = "http://localhost:8000/predict"
customer = {
    "credit_score": 650,
    "Geography": "France",
    "Gender": "Female",
    "Age": 42,
    # ... other fields
}

response = requests.post(url, json=customer)
result = response.json()

print(f"Churn Risk: {result['churn_probability']:.2%}")
print(f"Risk Level: {result['risk_level']}")
```

### JavaScript (fetch)

```javascript
// Single prediction
const customer = {
  credit_score: 650,
  Geography: "France",
  Gender: "Female",
  Age: 42,
  // ... other fields
};

fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(customer)
})
.then(response => response.json())
.then(data => {
  console.log('Churn Probability:', data.churn_probability);
  console.log('Risk Level:', data.risk_level);
});
```

---

## Deployment

### Production Settings

```bash
# Run with multiple workers
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Run with Gunicorn
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (Optional)

See `Dockerfile` for containerization (if created).

---

## Error Handling

The API uses standard HTTP status codes:

- **200**: Success
- **422**: Validation Error (invalid input)
- **500**: Internal Server Error
- **503**: Service Unavailable (model not loaded)

**Error Response Example:**
```json
{
  "detail": "Model not loaded"
}
```

---

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You can test all endpoints directly from the browser!
