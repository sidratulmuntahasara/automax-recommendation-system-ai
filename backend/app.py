from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model import load_data, train_model  # Your model functions
import numpy as np

app = FastAPI()

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data and model at startup
appraisals = load_data()
model, scaler = train_model(appraisals)  # Your training function

@app.post("/get_comps")
async def get_comps(subject: dict):
    try:
        # Process candidates (mock example - adapt to your data)
        candidates = subject.pop('candidates')
        
        # Generate features (use your actual feature engineering)
        features = []
        for c in candidates:
            feat = [
                abs(subject['gla'] - c['gla']),
                abs(subject['lot_size'] - c['lot_size']),
                # ... add other features
            ]
            features.append(feat)
            
        # Scale and predict
        scaled_features = scaler.transform(features)
        probs = model.predict_proba(scaled_features)[:, 1]
        
        # Get top 3 comps
        top3_idx = np.argsort(probs)[-3:][::-1]
        
        return {
            "comps": [candidates[i] for i in top3_idx],
            "explanations": []  # Add SHAP explanations here
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))