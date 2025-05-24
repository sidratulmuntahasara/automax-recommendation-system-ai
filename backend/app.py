from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model import load_data, train_model, clean_numeric, haversine
import numpy as np
from datetime import datetime
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data and model during startup
try:
    appraisals = load_data()
    model, scaler = train_model(appraisals)
except Exception as e:
    logging.error(f"FATAL ERROR DURING STARTUP: {str(e)}")
    raise SystemExit(1)

@app.get("/get_appraisal_ids")
async def get_appraisal_ids():
    try:
        return [{
            "id": str(a['orderID']),
            "address": a.get('subject', {}).get('address', 'Address not available')
        } for a in appraisals if 'orderID' in a]
    except Exception as e:
        logging.error(f"Error getting IDs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading appraisal IDs")

@app.get("/get_candidates/{appraisal_id}")
async def get_candidates(appraisal_id: str):
    try:
        appraisal = next(
            a for a in appraisals 
            if str(a.get('orderID', '')).strip() == appraisal_id.strip()
        )
        
        if not all(key in appraisal for key in ['subject', 'properties']):
            raise ValueError("Invalid appraisal structure")
            
        return {
            "subject": appraisal['subject'],
            "candidates": appraisal['properties']
        }
        
    except StopIteration:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    except Exception as e:
        logging.error(f"Error loading appraisal {appraisal_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading property data")

@app.post("/get_comps")
async def get_comps(request_data: dict):
    try:
        subject = request_data.get('subject', {})
        candidates = request_data.get('candidates', [])
        
        features = []
        valid_candidates = []
        
        # Get subject coordinates
        sub_lat = subject.get('lat', 0)
        sub_lon = subject.get('lon', 0)
        
        for idx, candidate in enumerate(candidates):
            try:
                # Feature 1: GLA Difference
                sub_gla = clean_numeric(subject.get('gla', 0))
                cand_gla = clean_numeric(candidate.get('gla', 0))
                gla_diff = abs(sub_gla - cand_gla)
                
                # Feature 2: Lot Size Difference
                sub_lot = clean_numeric(subject.get('lot_size', 0))
                cand_lot = clean_numeric(candidate.get('lot_size_sf', 0))
                lot_diff = abs(sub_lot - cand_lot)
                
                # Feature 3: Sale Date Difference
                eff_date = datetime.strptime(
                    subject.get('effective_date', 'Jan/1/2000'), "%b/%d/%Y")
                close_date = datetime.strptime(
                    candidate.get('close_date', '2000-01-01'), "%Y-%m-%d")
                month_diff = abs((eff_date - close_date).days) // 30
                
                # Feature 4: Distance
                distance = haversine(
                    sub_lat, sub_lon,
                    candidate.get('lat', 0),
                    candidate.get('lon', 0)
                )
                
                features.append([gla_diff, lot_diff, month_diff, distance])
                valid_candidates.append(candidate)
                
            except Exception as e:
                logging.warning(f"Skipping candidate {idx}: {str(e)}")
                continue
                
        if not features:
            return {"comps": []}
            
        # Predict and sort
        scaled_features = scaler.transform(features)
        probs = model.predict_proba(scaled_features)[:, 1]
        top_indices = np.argsort(probs)[-3:][::-1]
        
        # Prepare response with explanations
        comps = []
        for i in top_indices:
            candidate = valid_candidates[i]
            reasons = []
            
            # Generate explanations
            gla_diff = abs(clean_numeric(subject.get('gla', 0)) - clean_numeric(candidate.get('gla', 0)))
            if abs(gla_diff) < 100:
                reasons.append(f"Similar size ({gla_diff} sqft difference)")
                
            if month_diff <= 1:
                reasons.append("Sold within last month")
            elif month_diff <= 3:
                reasons.append("Sold within last 3 months")
                
            distance = haversine(sub_lat, sub_lon, candidate.get('lat',0), candidate.get('lon',0))
            if distance < 1:
                reasons.append(f"Nearby ({distance:.1f} miles)")
                
            comps.append({
                **candidate,
                "distance": distance,
                "reasons": reasons[:3]  # Return top 3 reasons
            })
            
        return {"comps": comps[:3]}  # Ensure only top 3
        
    except Exception as e:
        logging.error(f"Error finding comps: {str(e)}")
        raise HTTPException(status_code=500, detail="Error finding comparables")