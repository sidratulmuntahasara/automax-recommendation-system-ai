# Property Recommendation System

_A intelligent comparables recommendation engine for real estate valuation_

![System Demo](https://via.placeholder.com/800x400.png?text=System+Demo+GIF) 
*Replace with actual demo image*

## Features

- **Smart Property Matching**  
  Recommends top 3 comparable properties using XGBoost machine learning model

- **Explainable AI Decisions**  
  Shows clear reasons for each recommendation (size, location, recency)

- **Real-World Ready**  
  Handles messy real-world data with robust preprocessing:
  - Address normalization
  - Numeric field cleaning
  - Date formatting
  - Coordinate validation

- **Modern Tech Stack**  
  FastAPI + React + XGBoost combination for optimal performance

- **Self-Contained**  
  Full-stack solution with ready-to-use UI

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Basic terminal skills

### Setup Instructions

**1. Clone Repository**
```bash
git clone https://github.com/yourusername/property-recommendation-system.git
cd property-recommendation-system
```
**2. Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
**3. Frontend Setup**
```bash
cd ../frontend
npm install
```
**4. Running the System**
***Start Backend***
```bash
cd backend
uvicorn app:app --reload --port 8000
```
***Start Frontend (in new terminal)***
```bash
cd frontend
npm run dev
```

### 📂 Project Setup
```bash
.
├── backend
│   ├── app.py               # API endpoints
│   ├── model.py             # ML model training
│   ├── cleaned_appraisals.json  # Sample data
│   └── requirements.txt     # Python dependencies
├── frontend
│   ├── page.js              # Main UI component
│   └── package.json         # Frontend dependencies
└── README.md
```

### 🛠️ Usage Guide
- Select Subject Property
Choose from dropdown showing formatted addresses with IDs:
```bash
123 Maple Street, Springfield (ID: APP-123)
456 Oak Avenue, Shelbyville (ID: APP-456)
```
- View Property Details
System displays key subject property characteristics

- Generate Recommendations
Click "Find Comparable Properties" to get:
Top 3 matching properties
Sale prices and distances
Visual explanations for matches

### Technical Highlights
![deepseek_mermaid_20250524_f28066](https://github.com/user-attachments/assets/232debe0-b41d-4c99-9320-fd21b8855026)

### Key Metrics Considered
&nbsp;&nbsp;&nbsp;Feature&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Weight&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Description
--------------  ------  --------------------------
&nbsp;&nbsp;Living Area&nbsp;&nbsp;&nbsp;&nbsp;30%&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;GLA within 100 sqft
--------------  ------  --------------------------
&nbsp;&nbsp;&nbsp;Recency&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;25%&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sold <90 days preferred
--------------  ------  --------------------------
&nbsp;&nbsp;&nbsp;Location&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;20%&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<1 mile radius ideal
--------------  ------  -------------------
&nbsp;&nbsp;&nbsp;Lot Size&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;15%&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Similar dimensions
--------------  ------  -------------------
&nbsp;&nbsp;&nbsp;Bed/Bath&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;10%&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Exact match preferred


