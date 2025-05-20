from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model import load_data, train_model, haversine  # Your model functions
import numpy as np
import pandas as pd

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
async def get_comps(request_data: dict):
    try:
        subject = request_data['subject']
        candidates = request_data['candidates']
        
        # Generate features
        features = []
        for c in candidates:
            # Calculate time difference in months
            sale_date_diff = (pd.to_datetime(c['sale_date']) - pd.to_datetime(subject['sale_date'])).days // 30
            
            features.append([
                abs(subject['gla'] - c['gla']),
                abs(subject['lot_size'] - c['lot_size']),
                sale_date_diff,
                haversine(subject['lat'], subject['lon'], c['lat'], c['lon'])
            ])
            
        # Rest of your prediction code...
        return {"comps": comps, "explanations": explanations}
        
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/get_candidates/{appraisal_id}")
async def get_candidates(appraisal_id: str):
    try:
        appraisal = next(a for a in appraisals if a['id'] == appraisal_id)
        return {
            "subject": appraisal['subject'],
            "candidates": appraisal['candidates']
        }
    except StopIteration:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    
@app.get("/get_appraisal_ids")
async def get_appraisal_ids():
    return [a['id'] for a in appraisals]