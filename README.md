# 🌾 Fertilizer Recommendation System (NEP 2020 Aligned)

An interactive, AI-driven recommendation engine tailored for Indian farmers, applying the principles of Experiential Learning and Critical Thinking outlined in NEP 2020. 

## Features
- **Machine Learning**: Random Forest, Gradient Boosting, XGBoost evaluated via cross-validation hyperparameter tuning.
- **FastAPI Backend**: Sub-millisecond inference API coupled with SHAP tree-explainers to translate "black-box" decisions into farmer-friendly plain text insights.
- **React Frontend**: A premium, dynamic UI featuring slider-based experiential learning to test relationships between NP&K and recommendations.

## Directory Structure
- `ml-model/` - Contains the synthetic data generator and ML training pipelines (`train.py`) that exports models.
- `backend/` - FastAPI service exposing `/health`, `/predict`, and `/model-metrics`.
- `frontend/` - React frontend (Vite).

## Setup & Running

**1. Create a Python Virtual Environment & Install:**
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

**2. Train the ML Model:**
```bash
python ml-model/train.py
```

**3. Run the Backend API:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**4. Run the React Frontend:**
Ensure NodeJS is installed.
```bash
cd frontend
npm install
npm run dev
```

## Deployment
- **Frontend** can be deployed directly via Vercel or Netlify simply by uploading the `frontend/` folder.
- **Backend** can be hosted on Render or Railway by pointing it to the root project with build script `pip install -r requirements.txt` and start command `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.

## NEP 2020 Alignment
* **Experiential Learning**: Interactive sliders change metrics in real-time.
* **Critical Thinking**: Metric dashboard pits XGBoost against Random Forests so users understand AI limitations.
* **Skill-Based Learning**: Full transparent pipeline from hyperparameter tuning to API interface.
