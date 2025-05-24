import json
import re
import pandas as pd
from datetime import datetime

def clean_numeric(value):
    """Extract numeric values from strings with units"""
    if pd.isna(value) or value in ['', 'n/a', 'N/A']:
        return 0.0
    try:
        # Remove all non-numeric characters except decimal points
        return float(re.sub(r'[^\d.]', '', str(value)))
    except:
        return 0.0

def clean_date(date_str):
    """Convert various date formats to ISO format (YYYY-MM-DD)"""
    if pd.isna(date_str) or date_str in ['', 'n/a', 'N/A']:
        return None
    
    date_str = str(date_str).replace(' ', '')
    
    # Try different date formats
    formats = [
        '%b/%d/%Y',    # May/05/2025
        '%B/%d/%Y',    # May/05/2025 (full month name)
        '%Y-%m-%d',    # ISO format
        '%m/%d/%Y',    # 05/05/2025
        '%d-%b-%y',    # 05-May-25
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return None  # Return None if all formats fail

def clean_dataset(input_file, output_file):
    # Load raw data
    with open(input_file) as f:
        data = json.load(f)
    
    # Process each appraisal
    for appraisal in data['appraisals']:
        # Clean subject data
        subject = appraisal['subject']
        subject['gla'] = clean_numeric(subject['gla'])
        subject['lot_size'] = clean_numeric(subject['lot_size_sf'])
        subject['year_built'] = int(clean_numeric(subject['year_built']))
        subject['sale_date'] = clean_date(subject['sale_date'])
        
        # Clean candidates (properties)
        for prop in appraisal['properties']:
            prop['gla'] = clean_numeric(prop['gla'])
            prop['lot_size_sf'] = clean_numeric(prop.get('lot_size_sf', 0))
            prop['close_price'] = clean_numeric(prop['close_price'])
            prop['close_date'] = clean_date(prop['close_date'])
            
            # Convert numeric fields to floats
            if 'latitude' in prop: prop['latitude'] = float(prop['latitude'])
            if 'longitude' in prop: prop['longitude'] = float(prop['longitude'])
        
        # Clean comps
        for comp in appraisal['comps']:
            comp['gla'] = clean_numeric(comp['gla'])
            comp['lot_size'] = clean_numeric(comp['lot_size'])
            comp['sale_price'] = clean_numeric(comp['sale_price'])
            comp['sale_date'] = clean_date(comp['sale_date'])
    
    # Save cleaned data
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Cleaned data saved to {output_file}")

# Usage - run this once to clean your dataset
clean_dataset('C:/Users/sidra/OneDrive/Desktop/Sara/Github/automax-recommendation-system-ai/backend/appraisals_dataset.json', 'cleaned_appraisals.json')