from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model import load_data, train_model, clean_numeric
import numpy as np
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
        valid_candidates = []
        
        for c in candidates:
            try:
                # Clean and convert values with error handling
                sub_gla = clean_numeric(subject.get('gla', 0))
                cand_gla = clean_numeric(c.get('gla', 0))
                gla_diff = abs(sub_gla - cand_gla)
                
                sub_lot = clean_numeric(subject.get('lot_size', 0))  # Subject field
                cand_lot = clean_numeric(c.get('lot_size_sf', 0))    # Candidate field
                lot_diff = abs(sub_lot - cand_lot)
                
                # Date handling with format validation
                eff_date = datetime.strptime(subject['effective_date'], "%b/%d/%Y")
                close_date = datetime.strptime(c['close_date'], "%Y-%m-%d")
                month_diff = abs((eff_date - close_date).days) // 30
                
                features.append([gla_diff, lot_diff, month_diff])
                valid_candidates.append(c)
                
            except Exception as e:
                print(f"Skipping candidate {c.get('address')}: {str(e)}")
                continue
        
        if not features:
            return {"comps": []}
            
        # Ensure we have matching candidates and features
        scaled_features = scaler.transform(features)
        probs = model.predict_proba(scaled_features)[:, 1]
        top3 = np.argsort(probs)[-3:][::-1]
        return {"comps": [valid_candidates[i] for i in top3]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))