from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Import your utility functions
from utils.feature_engineering import create_prediction_features
from utils.data_validation import validate_prediction_input
from utils.business_rule import apply_business_rules

# Load ML model
MODEL_PATH = "models/supply_chain_model_best.pkl"
FEATURE_PATH = "models/model_features.pkl"

try:
    model = joblib.load(MODEL_PATH)
    feature_info = joblib.load(FEATURE_PATH)
    print("✅ ML model loaded successfully")
    print(f"📊 Model features: {len(feature_info['feature_columns'])}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    feature_info = None

app = FastAPI(title="Supply Chain Prediction API")

# CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class PredictionRequest(BaseModel):
    stockyard_id: str
    product_id: str
    current_inventory: float
    next_7day_demand: float

class PredictionResponse(BaseModel):
    success: bool
    raw_prediction: float
    final_prediction: float
    wagons_required: int
    wagon_type: str
    wagon_capacity: float
    message: str
    business_rules_applied: list

@app.get("/")
def read_root():
    return {"message": "Supply Chain Prediction API", "version": "1.0"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "model_loaded": model is not None,
        "features_loaded": feature_info is not None
    }

@app.get("/features")
def get_feature_info():
    """Return information about required features"""
    if feature_info is None:
        raise HTTPException(status_code=500, detail="Feature info not loaded")
    
    return {
        "total_features": len(feature_info['feature_columns']),
        "numerical_features": len(feature_info['numerical_columns']),
        "categorical_features": len(feature_info['categorical_columns']),
        "feature_columns": feature_info['feature_columns']
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_supply(request: PredictionRequest):
    if model is None or feature_info is None:
        raise HTTPException(status_code=500, detail="ML model or feature info not loaded")
    
    try:
        # 1. Validate input data
        validation_errors = validate_prediction_input(request.dict())
        if validation_errors:
            raise HTTPException(status_code=400, detail=f"Validation errors: {validation_errors}")
        
        print(f"🔮 Predicting for {request.stockyard_id} - {request.product_id}")
        
        # 2. Create complete feature set
        input_features = create_prediction_features(
            stockyard_id=request.stockyard_id,
            product_id=request.product_id,
            current_inventory=request.current_inventory,
            next_7day_demand=request.next_7day_demand,
            prediction_date=datetime.now()
        )
        
        # 3. Convert to DataFrame with correct column order
        feature_df = pd.DataFrame([input_features])[feature_info['feature_columns']]
        
        # 4. Make raw ML prediction
        raw_prediction = model.predict(feature_df)[0]
        print(f"🤖 Raw ML prediction: {raw_prediction:.2f} tonnes")
        
        # 5. Apply business rules
        business_result = apply_business_rules(
            raw_prediction=raw_prediction,
            features=input_features,
            stockyard_id=request.stockyard_id,
            product_id=request.product_id
        )
        
        return PredictionResponse(
            success=True,
            raw_prediction=round(raw_prediction, 2),
            final_prediction=round(business_result['final_supply'], 2),
            wagons_required=business_result['wagons_required'],
            wagon_type=business_result['wagon_type'],
            wagon_capacity=business_result['wagon_capacity'],
            message="Prediction successful",
            business_rules_applied=business_result['rules_applied']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)