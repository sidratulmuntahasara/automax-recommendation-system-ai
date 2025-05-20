import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import json
import shap
from geopy.distance import great_circle  # Add this import

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two geographic points"""
    return great_circle((lat1, lon1), (lat2, lon2)).miles  # or .km for kilometers

def load_data():
    with open('appraisals_dataset.json') as f:
        appraisals = json.load(f)
    
    print(f"Loaded {len(appraisals)} appraisals")
    # Verify structure
    if len(appraisals) > 0:
        print("Sample subject keys:", appraisals[0]['subject'].keys())
        print("Sample candidate keys:", appraisals[0]['candidates'][0].keys())
    
    return appraisals

# Add your previous model code here
data = []
appraisals = load_data()
for appraisal in appraisals:
    subject = appraisal['subject']
    for i, candidate in enumerate(appraisal['candidates']):
        # Compute feature differences
        features = [
            abs(subject['gla'] - candidate['gla']),
            abs(subject['lot_size'] - candidate['lot_size']),
            (pd.to_datetime(candidate['sale_date']) - pd.to_datetime(subject['sale_date'])).days // 30,
            haversine(subject['lat'], subject['lon'], candidate['lat'], candidate['lon'])
        ]
        target = 1 if i in appraisal['comps'] else 0
        data.append(features + [target, appraisal['id']])

df = pd.DataFrame(data, columns=['gla_diff', 'lot_diff', 'sale_month_diff', 'geo_dist', 'target', 'appraisal_id'])

# Split data
train_ids, val_ids = train_test_split(np.unique(df['appraisal_id']), test_size=0.2)
X_train = df[df['appraisal_id'].isin(train_ids)].drop(['target', 'appraisal_id'], axis=1)
y_train = df[df['appraisal_id'].isin(train_ids)]['target']
X_val = df[df['appraisal_id'].isin(val_ids)].drop(['target', 'appraisal_id'], axis=1)
y_val = df[df['appraisal_id'].isin(val_ids)]['target']

# Normalize
scaler = StandardScaler().fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_val_scaled = scaler.transform(X_val)

# Train model
model = xgb.XGBClassifier()
model.fit(X_train_scaled, y_train)


# Validate model
val_appraisals = [a for a in appraisals if a['id'] in val_ids]
precision, recall = [], []

for appraisal in val_appraisals:
    candidates = appraisal['candidates']
    features = []
    for c in candidates:
        features.append([
            abs(appraisal['subject']['gla'] - c['gla']),
            abs(appraisal['subject']['lot_size'] - c['lot_size']),
            (pd.to_datetime(c['sale_date']) - pd.to_datetime(appraisal['subject']['sale_date'])).days // 30,
            haversine(appraisal['subject']['lat'], appraisal['subject']['lon'], c['lat'], c['lon'])
        ])
    features = scaler.transform(features)
    probs = model.predict_proba(features)[:, 1]
    top3 = np.argsort(probs)[-3:][::-1]
    actual = set(appraisal['comps'])
    tp = len(set(top3) & actual)
    precision.append(tp / 3)
    recall.append(tp / len(actual))

print(f"Validation Precision@3: {np.mean(precision):.2f}")
print(f"Validation Recall@3: {np.mean(recall):.2f}")

# SHAP values

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_val_scaled)

# Example explanation for the first candidate in the first validation appraisal
appraisal = val_appraisals[0]
candidate_idx = 0  # Assuming this is a top recommendation
shap.force_plot(
    explainer.expected_value,
    shap_values[candidate_idx],
    X_val_scaled[candidate_idx],
    feature_names=X_train.columns
)


# Pseudocode for feedback integration
# feedback_data = [...]  # Collect user-approved/rejected comps
# updated_df = pd.concat([df, feedback_data])
# retrain_model(updated_df)