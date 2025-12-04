"""
FastAPI REST API for Mortgage Churn Prediction.

Run with:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from hypo_churn.inference import load_inference_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Mortgage Churn Prediction API",
    description="REST API for predicting mortgage customer churn using XGBoost",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
# Adjust allowed_origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with specific origins in production
    allow_credentials=False,  # Set to True if using cookies/auth
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600,
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")

    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code} for {request.url.path}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.url.path} - {type(e).__name__}")
        raise

# Global model instance (loaded on startup)
inference_engine = None


# Pydantic models for request/response validation
class CustomerFeatures(BaseModel):
    """Customer features for prediction."""
    credit_score: float = Field(..., ge=300, le=850, description="Credit score (300-850)")
    Geography: str = Field(..., description="Customer geography (France, Spain, Germany)")
    Gender: str = Field(..., description="Customer gender (Male, Female)")
    Age: int = Field(..., ge=18, le=100, description="Customer age")
    loan_age_years: float = Field(..., ge=0, le=50, description="Loan age in years")
    outstanding_loan_balance: float = Field(..., ge=0, le=10000000, description="Outstanding loan balance")
    num_bank_products: int = Field(..., ge=1, le=4, description="Number of bank products")
    has_credit_card: int = Field(..., ge=0, le=1, description="Has credit card (0 or 1)")
    online_banking_active: int = Field(..., ge=0, le=1, description="Online banking active (0 or 1)")
    annual_income: float = Field(..., ge=0, le=10000000, description="Annual income")
    monthly_income: Optional[float] = Field(None, ge=0, le=1000000, description="Monthly income (calculated if not provided)")
    estimated_property_value: Optional[float] = Field(None, ge=0, le=100000000, description="Estimated property value")
    ltv_ratio: Optional[float] = Field(None, ge=0, le=2, description="Loan-to-value ratio")
    payment_to_income_ratio: Optional[float] = Field(None, ge=0, le=2, description="Payment-to-income ratio")
    risk_score: Optional[float] = Field(None, ge=0, le=2, description="Composite risk score")
    balance_per_product: Optional[float] = Field(None, ge=0, le=10000000, description="Balance per product")

    @validator('Geography')
    def validate_geography(cls, v):
        """Validate Geography is one of allowed values."""
        allowed = ['France', 'Spain', 'Germany']
        if v not in allowed:
            raise ValueError(f"Geography must be one of {allowed}")
        return v

    @validator('Gender')
    def validate_gender(cls, v):
        """Validate Gender is one of allowed values."""
        allowed = ['Male', 'Female']
        if v not in allowed:
            raise ValueError(f"Gender must be one of {allowed}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    prediction: int = Field(..., description="Prediction (0=not churned, 1=churned)")
    prediction_label: str = Field(..., description="Human-readable prediction label")
    churn_probability: float = Field(..., ge=0, le=1, description="Probability of churning")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    risk_level: str = Field(..., description="Risk level (Low, Medium, High, Critical)")


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions."""
    customers: List[CustomerFeatures] = Field(..., min_length=1, max_length=100, description="Max 100 customers per batch")


class BatchPredictionResponse(BaseModel):
    """Response model for batch predictions."""
    predictions: List[PredictionResponse]
    total_customers: int
    churned_count: int
    churn_rate: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    version: str


class ModelInfoResponse(BaseModel):
    """Model information response."""
    model_name: str
    model_type: str
    features_count: int
    available: bool


# Startup event
@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    global inference_engine
    import os

    # Get model name from environment or use default
    model_name = os.getenv('MODEL_NAME', 'best_xgboost_model')

    try:
        logger.info(f"Loading inference engine: {model_name}...")
        inference_engine = load_inference_engine(model_name)
        logger.info("✓ Model loaded successfully")
    except FileNotFoundError:
        # Try fallback to random forest model if xgboost not found
        logger.warning(f"Model '{model_name}' not found, trying 'best_model_random_forest'...")
        try:
            inference_engine = load_inference_engine('best_model_random_forest')
            logger.info("✓ Model loaded successfully (using Random Forest)")
        except Exception as fallback_error:
            logger.error(f"Failed to load fallback model: {fallback_error}")
            inference_engine = None
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        inference_engine = None


# API Endpoints
@app.get("/", tags=["General"])
@limiter.limit("30/minute")
async def root(request: Request):
    """Root endpoint with API information."""
    return {
        "message": "Mortgage Churn Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if inference_engine is not None else "unhealthy",
        model_loaded=inference_engine is not None,
        version="1.0.0"
    )


@app.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
@limiter.limit("30/minute")
async def model_info(request: Request):
    """Get model information."""
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Model not available")

    return ModelInfoResponse(
        model_name="best_xgboost_model",
        model_type="XGBoost Classifier",
        features_count=len(inference_engine.feature_names) if inference_engine.feature_names else 0,
        available=True
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
@limiter.limit("10/minute")
async def predict_single(request: Request, customer: CustomerFeatures):
    """
    Make a churn prediction for a single customer.

    Returns prediction, probability, and risk level.
    Rate limit: 10 requests per minute per IP.
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Model not available")

    try:
        # Convert to dict
        customer_data = customer.model_dump()

        # Make prediction
        result = inference_engine.predict_with_details(customer_data)[0]

        return PredictionResponse(**result)

    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        raise HTTPException(status_code=400, detail="Invalid input data")
    except Exception as e:
        logger.error(f"Prediction error: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Prediction service temporarily unavailable")


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Predictions"])
@limiter.limit("5/minute")
async def predict_batch(request: Request, batch_request: BatchPredictionRequest):
    """
    Make churn predictions for multiple customers.

    Maximum 100 customers per request.
    Rate limit: 5 requests per minute per IP.
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Model not available")

    try:
        # Convert to list of dicts
        customers_data = [c.model_dump() for c in batch_request.customers]

        # Make predictions
        results = inference_engine.predict_with_details(customers_data)

        # Calculate statistics
        churned_count = sum(1 for r in results if r['prediction'] == 1)
        total_customers = len(results)
        churn_rate = churned_count / total_customers if total_customers > 0 else 0

        return BatchPredictionResponse(
            predictions=[PredictionResponse(**r) for r in results],
            total_customers=total_customers,
            churned_count=churned_count,
            churn_rate=churn_rate
        )

    except ValueError as e:
        logger.warning(f"Invalid batch input: {e}")
        raise HTTPException(status_code=400, detail="Invalid input data in batch")
    except Exception as e:
        logger.error(f"Batch prediction error: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Batch prediction service temporarily unavailable")


@app.get("/predict/probability", tags=["Predictions"])
@limiter.limit("15/minute")
async def predict_probability(
    request: Request,
    credit_score: float,
    Geography: str,
    Gender: str,
    Age: int,
    loan_age_years: float,
    outstanding_loan_balance: float,
    num_bank_products: int,
    has_credit_card: int,
    online_banking_active: int,
    annual_income: float
):
    """
    Quick probability check via query parameters.

    Useful for simple GET requests without POST body.
    Rate limit: 15 requests per minute per IP.
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Model not available")

    try:
        # Validate Geography and Gender using the same logic
        if Geography not in ['France', 'Spain', 'Germany']:
            raise ValueError("Invalid Geography")
        if Gender not in ['Male', 'Female']:
            raise ValueError("Invalid Gender")

        # Create customer data
        customer_data = {
            'credit_score': credit_score,
            'Geography': Geography,
            'Gender': Gender,
            'Age': Age,
            'loan_age_years': loan_age_years,
            'outstanding_loan_balance': outstanding_loan_balance,
            'num_bank_products': num_bank_products,
            'has_credit_card': has_credit_card,
            'online_banking_active': online_banking_active,
            'annual_income': annual_income,
            # Calculate derived features
            'monthly_income': annual_income / 12,
            'estimated_property_value': annual_income * 3.5,
            'ltv_ratio': 0.0,
            'payment_to_income_ratio': 0.0,
            'risk_score': 0.0,
            'balance_per_product': 0.0
        }

        result = inference_engine.predict_with_details(customer_data)[0]

        return {
            "churn_probability": result['churn_probability'],
            "risk_level": result['risk_level']
        }

    except ValueError as e:
        logger.warning(f"Invalid query parameter: {e}")
        raise HTTPException(status_code=400, detail="Invalid query parameters")
    except Exception as e:
        logger.error(f"Probability prediction error: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Prediction service temporarily unavailable")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
