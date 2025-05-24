# Property Recommendation System

_An intelligent comparables recommendation engine for real estate valuation_

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
**4. Running the System**\
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

### 📂 Project Structure
```bash
.
├── backend
│ ├── app.py # FastAPI endpoints and core logic
│ ├── model.py # ML model training and scoring
│ ├── data_cleaner.py # Data normalization/preprocessing
│ ├── appraisals_dataset.json # Raw appraisal data
│ ├── cleaned_appraisals.json # Processed appraisal data
│ ├── requirements.txt Python dependencies
│ └── pycache # Python compiled bytecode
├── frontend
│ ├── src/app
│ │ ├── page.js # Main UI component
│ │ ├── layout.js # Root layout component
│ │ └── globals.css # Global CSS styles
│ ├── public
│ │ └── favicon.ico # Application icon
│ ├── .next # Next.js build output
│ ├── node_modules # Frontend dependencies
│ ├── package.json # Frontend dependencies and scripts
│ ├── jsconfig.json # JavaScript configuration
│ └── next.config.mjs # Next.js configuration
├── .gitignore # Version control ignore rules
├── LICENSE # Software license
└── README.md # This documentation file
```

### 🛠️ Usage Guide
- Select Subject Property : Choose from dropdown showing formatted addresses with IDs
- View Property Details : System displays key subject property characteristics
- Generate Recommendations : Click "Find Comparable Properties" to get:\
Top 3 matching properties\
Sale prices and distances\
Visual explanations for matches

### Technical Highlights
![deepseek_mermaid_20250524_f28066](https://github.com/user-attachments/assets/232debe0-b41d-4c99-9320-fd21b8855026)

### Key Metrics Considered
|   Feature     | Weight  |  Description               |
|---|---|---|
|   Living Area |  30%    |  GLA within 100 sqft       |
|   Recency     |  25%    |  Sold <90 days preferred   |
|   Location    |  20%    |  <1 mile radius ideal      |
|   Lot Size    |  15%    |  Similar dimensions        |
|   Bed/Bath    |  10%    |  Exact match preferred     |



### Future Improvements
- Add map visualization for properties
- Include price/square foot metrics
- Support custom search filters
- Implement historical price trends
- Reiterate user feedback and improve model's learning
