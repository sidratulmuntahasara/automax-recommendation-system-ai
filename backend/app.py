from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model import load_data, train_model, haversine, clean_numeric
import numpy as np
import pandas as pd
from datetime import datetime

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    appraisals = load_data()
    model, scaler = train_model(appraisals)
except Exception as e:
    print(f"FATAL ERROR DURING STARTUP: {str(e)}")
    raise SystemExit(1)

@app.get("/get_appraisal_ids")
async def get_appraisal_ids():
    return [str(a['orderID']) for a in appraisals if 'orderID' in a]

@app.get("/get_candidates/{appraisal_id}")
async def get_candidates(appraisal_id: str):
    try:
        appraisal = next(a for a in appraisals if str(a.get('orderID', '')) == appraisal_id)
        return {
            "subject": appraisal['subject'],
            "candidates": appraisal['properties']
        }
    except StopIteration:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Invalid data structure: {str(e)}")

@app.post("/get_comps")
async def get_comps(request_data: dict):
    try:
        subject = request_data['subject']
        candidates = request_data['candidates']
        
        features = []
        for c in candidates:
            try:
                # Clean and convert all values
                sub_gla = clean_numeric(subject['gla'])
                cand_gla = clean_numeric(c['gla'])
                sub_lot = clean_numeric(subject['lot_size'])
                cand_lot = clean_numeric(c.get('lot_size_sf', 0))
                
                # Date handling
                sale_date = datetime.strptime(subject['sale_date'], "%b/%d/%Y")
                candidate_date = datetime.strptime(c['close_date'], "%Y-%m-%d")
                month_diff = (candidate_date - sale_date).days // 30
                
                # Geography
                geo_dist = haversine(
                    clean_numeric(subject['lat']),
                    clean_numeric(subject['lon']),
                    clean_numeric(c['latitude']),
                    clean_numeric(c['longitude'])
                )
                
                features.append([
                    abs(sub_gla - cand_gla),
                    abs(sub_lot - cand_lot),
                    month_diff,
                    geo_dist
                ])
            except Exception as e:
                print(f"Skipping candidate: {str(e)}")
                continue
        
        if not features:
            return {"comps": []}
            
        scaled_features = scaler.transform(features)
        probs = model.predict_proba(scaled_features)[:, 1]
        top3 = np.argsort(probs)[-3:][::-1]
        return {"comps": [candidates[i] for i in top3]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))