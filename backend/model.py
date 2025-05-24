import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import json
import re
from datetime import datetime

def clean_numeric(value):
    """Convert string with units to float, handling missing values."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(re.sub(r'[^\d.]', '', str(value)))
    except:
        return 0.0

def load_data():
    with open('cleaned_appraisals.json') as f:
        data = json.load(f)
    return data['appraisals']

def process_data(appraisals):
    data = []
    for appraisal in appraisals:
        subject = appraisal['subject']
        candidates = appraisal['properties']
        # Normalize comp addresses for comparison
        comp_addresses = [c['address'].strip().lower() for c in appraisal['comps']]
        
        for candidate in candidates:
            try:
                # --- Feature 1: GLA Difference ---
                sub_gla = clean_numeric(subject.get('gla', 0))
                cand_gla = clean_numeric(candidate.get('gla', 0))
                gla_diff = abs(sub_gla - cand_gla)
                
                # --- Feature 2: Lot Size Difference ---
                sub_lot = clean_numeric(subject.get('lot_size', 0))  # Subject uses 'lot_size'
                cand_lot = clean_numeric(candidate.get('lot_size_sf', 0))  # Candidate uses 'lot_size_sf'
                lot_diff = abs(sub_lot - cand_lot)
                
                # --- Feature 3: Sale Date Difference (Months) ---
                # Parse subject's effective date
                eff_date = datetime.strptime(subject['effective_date'], '%b/%d/%Y')
                # Parse candidate's close date
                close_date = datetime.strptime(candidate['close_date'], '%Y-%m-%d')
                sale_month_diff = abs((eff_date - close_date).days) // 30
                
                # --- Target Variable ---
                # Check if candidate is a comp (address match)
                cand_addr = candidate['address'].strip().lower()
                target = 1 if cand_addr in comp_addresses else 0
                
                data.append([
                    gla_diff,
                    lot_diff,
                    sale_month_diff,
                    target,
                    str(appraisal['orderID'])
                ])
            except Exception as e:
                print(f"Skipping candidate due to error: {str(e)}")
                continue
    
    return pd.DataFrame(
        data, 
        columns=['gla_diff', 'lot_diff', 'sale_month_diff', 'target', 'appraisal_id']
    )

def train_model(appraisals):
    df = process_data(appraisals)
    
    if len(df) == 0:
        raise ValueError("No valid data processed - check dataset formatting")
    
    # Split by appraisal ID to avoid data leakage
    unique_ids = df['appraisal_id'].unique()
    train_ids, val_ids = train_test_split(unique_ids, test_size=0.2, random_state=42)
    
    # Prepare data
    X_train = df[df['appraisal_id'].isin(train_ids)].drop(['target', 'appraisal_id'], axis=1)
    y_train = df[df['appraisal_id'].isin(train_ids)]['target']
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Train model
    model = xgb.XGBClassifier()
    model.fit(X_train_scaled, y_train)
    
    return model, scaler