from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import json
import os
import shap
import pandas as pd
import numpy as np

app = FastAPI(title="Fertilizer Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load artifacts safely
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(BASE_DIR, 'ml-model', 'artifacts')

try:
    model = joblib.load(os.path.join(ARTIFACTS_DIR, "best_model.pkl"))
    scaler = joblib.load(os.path.join(ARTIFACTS_DIR, "scaler.pkl"))
    encoder = joblib.load(os.path.join(ARTIFACTS_DIR, "encoder.pkl"))
    with open(os.path.join(ARTIFACTS_DIR, "metrics.json"), "r") as f:
        metrics = json.load(f)
        
    # Initialize SHAP explainer
    explainer = shap.TreeExplainer(model)
except Exception as e:
    print(f"Warning: Could not load models. Did you run train.py? Error: {e}")
    model, scaler, encoder, metrics, explainer = None, None, None, {}, None

class SoilData(BaseModel):
    N: float = Field(..., description="Nitrogen content (0-140)", ge=0)
    P: float = Field(..., description="Phosphorus content (0-145)", ge=0)
    K: float = Field(..., description="Potassium content (0-205)", ge=0)
    temperature: float = Field(..., description="Temperature in Celsius", ge=-10, le=60)
    humidity: float = Field(..., description="Humidity in %", ge=0, le=100)
    ph: float = Field(..., description="pH value", ge=0, le=14)

def generate_human_explanation(shap_values_dict, recommendation):
    """Convert SHAP feature importances to human-readable insights for farmers."""
    sorted_features = sorted(shap_values_dict.items(), key=lambda x: abs(x[1]), reverse=True)
    top_feature, top_val = sorted_features[0]
    
    explanation = f"We highly recommend {recommendation} "
    
    if "NPK" in recommendation:
        explanation += "to ensure a balanced nutrient profile. "
    elif "Urea" in recommendation:
        explanation += "to boost your soil's nitrogen levels. "
    
    direction = "high levels" if top_val > 0 else "low levels"
    explanation += f"Our AI strongly factored in the {direction} of {top_feature} in your soil when making this decision."
    
    return explanation

def calculate_quantity(recommendation, N, P, K):
    """Mock rule-based logic to predict quantity per hectare based on fertilizer recommended."""
    if "NPK 19-19-19" in recommendation:
        return max(50, 150 - (N+P+K)/3)
    elif "Urea" in recommendation:
        return max(40, 150 - N)
    elif "DAP" in recommendation:
        return max(40, 150 - P)
    elif "MOP" in recommendation:
        return max(40, 150 - K)
    else:
        return 90

@app.get("/")
def root():
    return {
        "message": "Fertilizer Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "metrics": "/model-metrics",
            "docs": "/docs"
        }
    }

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "ok", "model_loaded": model is not None}

@app.get("/model-metrics")
@app.get("/api/model-metrics")
def get_metrics():
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    return metrics

@app.post("/predict")
@app.post("/api/predict")
def predict_fertilizer(data: SoilData):
    if not model:
        raise HTTPException(status_code=503, detail="Model currently not available.")
        
    input_df = pd.DataFrame([data.model_dump()])
    
    # Scale
    input_scaled = scaler.transform(input_df)
    
    # Predict
    pred_idx = model.predict(input_scaled)[0]
    probabilities = model.predict_proba(input_scaled)[0]
    
    confidence = np.max(probabilities)
    recommendation = encoder.inverse_transform([pred_idx])[0]
    
    # Explainability (SHAP)
    try:
        shap_values = explainer.shap_values(input_scaled)
        
        # Depending on XGB vs RandomForest SHAP formats
        if isinstance(shap_values, list): 
            # Multi-class
            class_shap = shap_values[pred_idx][0]
        else:
            # SHAP returns 3D array for tree explainers on multiclass sometimes
            if len(shap_values.shape) == 3:
                class_shap = shap_values[0, :, pred_idx]
            else:
                class_shap = shap_values[0]
                
        feature_names = input_df.columns.tolist()
        shap_dict = {feature_names[i]: float(class_shap[i]) for i in range(len(feature_names))}
        
        explanation = generate_human_explanation(shap_dict, recommendation)
    except Exception as e:
        print("SHAP Error:", e)
        explanation = f"We highly recommend {recommendation} based on overall soil dynamics."
        shap_dict = {}

    quantity = calculate_quantity(recommendation, data.N, data.P, data.K)

    return {
        "recommendation": recommendation,
        "quantity_kg_per_hectare": round(float(quantity), 2),
        "confidence_score": round(float(confidence), 2),
        "explanation": explanation,
        "feature_importance": shap_dict
    }
