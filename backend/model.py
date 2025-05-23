import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import json
import shap
import re
from geopy.distance import great_circle

def haversine(lat1, lon1, lat2, lon2):
    return great_circle((lat1, lon1), (lat2, lon2)).miles

def clean_numeric(value):
    """Convert string with units to float"""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(re.sub(r'[^\d.]', '', str(value)))
    except:
        return 0.0

def load_data():
    with open('./appraisals_dataset.json') as f:
        data = json.load(f)
    return data['appraisals']

def process_data(appraisals):
    data = []
    for appraisal in appraisals:
        subject = appraisal['subject']
        candidates = appraisal['properties']
        comp_addresses = [c['address'] for c in appraisal['comps']]
        
        for candidate in candidates:
            try:
                # Clean and convert numeric values
                sub_gla = clean_numeric(subject['gla'])
                cand_gla = clean_numeric(candidate['gla'])
                sub_lot = clean_numeric(subject['lot_size_sf'])
                cand_lot = clean_numeric(candidate.get('lot_size_sf', 0))
                
                # Date handling
                sale_diff = (pd.to_datetime(candidate['close_date']) - 
                            pd.to_datetime(comp_addresses['sale_date'])).days // 30
                
                # Geography
                geo_dist = haversine(
                    clean_numeric(subject['lat']),
                    clean_numeric(subject['lon']),
                    clean_numeric(candidate['latitude']),
                    clean_numeric(candidate['longitude'])
                )
                
                target = 1 if candidate['address'] in comp_addresses else 0
                data.append([
                    abs(sub_gla - cand_gla),
                    abs(sub_lot - cand_lot),
                    sale_diff,
                    geo_dist,
                    target,
                    str(appraisal['orderID'])
                ])
            except Exception as e:
                print(f"Skipping candidate: {e}")
                continue
    
    return pd.DataFrame(data, columns=['gla_diff', 'lot_diff', 'sale_month_diff', 
                                      'geo_dist', 'target', 'appraisal_id'])

def train_model(appraisals):
    df = process_data(appraisals)
    
    if len(df) == 0:
        raise ValueError("No valid data processed - check dataset formatting")
    
    train_ids, val_ids = train_test_split(np.unique(df['appraisal_id']), 
                                         test_size=0.2, 
                                         random_state=42)
    
    X_train = df[df['appraisal_id'].isin(train_ids)].drop(['target', 'appraisal_id'], axis=1)
    y_train = df[df['appraisal_id'].isin(train_ids)]['target']
    
    scaler = StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    
    model = xgb.XGBClassifier()
    model.fit(X_train_scaled, y_train)
    
    return model, scaler