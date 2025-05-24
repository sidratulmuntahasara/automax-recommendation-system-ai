import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import json
import re
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c * 0.621371  # Convert to miles

def clean_numeric(value):
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(re.sub(r'[^\d.]', '', str(value)))
    except:
        return 0.0

def load_data():
    try:
        with open('cleaned_appraisals.json') as f:
            data = json.load(f)
        return data.get('appraisals', [])
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return []

def process_data(appraisals):
    data = []
    for appraisal in appraisals:
        try:
            subject = appraisal.get('subject', {})
            candidates = appraisal.get('properties', [])
            comp_addresses = [c.get('address', '').strip().lower() 
                            for c in appraisal.get('comps', [])]
            
            for candidate in candidates:
                # Feature calculations
                gla_diff = abs(clean_numeric(subject.get('gla', 0)) - 
                          clean_numeric(candidate.get('gla', 0)))
                
                lot_diff = abs(clean_numeric(subject.get('lot_size', 0)) - 
                          clean_numeric(candidate.get('lot_size_sf', 0)))
                
                try:
                    eff_date = datetime.strptime(
                        subject.get('effective_date', 'Jan/1/2000'), "%b/%d/%Y")
                    close_date = datetime.strptime(
                        candidate.get('close_date', '2000-01-01'), "%Y-%m-%d")
                    month_diff = abs((eff_date - close_date).days) // 30
                except:
                    month_diff = 36  # Default to 3 years if invalid date
                
                distance = haversine(
                    subject.get('lat', 0),
                    subject.get('lon', 0),
                    candidate.get('lat', 0),
                    candidate.get('lon', 0)
                )
                
                # Target variable
                target = 1 if candidate.get('address', '').strip().lower() in comp_addresses else 0
                
                data.append([
                    gla_diff,
                    lot_diff,
                    month_diff,
                    distance,
                    target,
                    str(appraisal.get('orderID', ''))
                ])
        except Exception as e:
            print(f"Skipping appraisal: {str(e)}")
            continue
            
    return pd.DataFrame(
        data,
        columns=['gla_diff', 'lot_diff', 'month_diff', 'distance', 'target', 'appraisal_id']
    )

def train_model(appraisals):
    df = process_data(appraisals)
    
    if df.empty:
        raise ValueError("No valid data processed")
    
    # Split data without leakage
    unique_ids = df['appraisal_id'].unique()
    train_ids, test_ids = train_test_split(unique_ids, test_size=0.2, random_state=42)
    
    X_train = df[df.appraisal_id.isin(train_ids)].drop(
        ['target', 'appraisal_id'], axis=1)
    y_train = df[df.appraisal_id.isin(train_ids)].target
    
    # Feature scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    
    # Model training
    model = xgb.XGBClassifier(
        objective='binary:logistic',
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1
    )
    model.fit(X_scaled, y_train)
    
    return model, scaler