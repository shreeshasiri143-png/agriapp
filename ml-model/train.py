import pandas as pd
import numpy as np
import json
import joblib
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Constants
DATA_SIZE = 1500
RANDOM_STATE = 42
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_synthetic_data(num_samples=DATA_SIZE):
    "Generate dummy data based on realistic ag-tech ranges."
    np.random.seed(RANDOM_STATE)
    
    # Inputs
    N = np.random.randint(0, 140, num_samples)
    P = np.random.randint(5, 145, num_samples)
    K = np.random.randint(5, 205, num_samples)
    temperature = np.random.uniform(15.0, 45.0, num_samples)
    humidity = np.random.uniform(20.0, 95.0, num_samples)
    ph = np.random.uniform(3.5, 9.5, num_samples)
    
    # Target (heuristic based logic to generate reasonable synthetic labels)
    fertilizers = []
    quantities = []
    
    for i in range(num_samples):
        if N[i] < 30 and P[i] < 30 and K[i] < 30:
            fert = "NPK 19-19-19"
            qty = np.random.uniform(50, 100)
        elif N[i] > 80:
            fert = "Urea"
            qty = np.random.uniform(100, 150)
        elif P[i] > 80:
            fert = "DAP"
            qty = np.random.uniform(100, 150)
        elif K[i] > 80:
            fert = "MOP"
            qty = np.random.uniform(50, 120)
        else:
            fert = "NPK 20-20-20"
            qty = np.random.uniform(60, 110)
        
        fertilizers.append(fert)
        quantities.append(round(qty, 2))
        
    df = pd.DataFrame({
        'N': N, 'P': P, 'K': K,
        'temperature': temperature,
        'humidity': humidity,
        'ph': ph,
        'quantity': quantities,
        'fertilizer': fertilizers
    })
    
    return df

def train_and_evaluate():
    print("Generating synthetic data...")
    df = generate_synthetic_data()
    
    # Prepare data
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph']]
    y = df['fertilizer']
    
    # Save quantities mapping for simplicity later (or we can predict it, but rules usually dictate qty per HA based on NPK gap)
    # the request states "Quantity (kg/hectare)", we will just create a basic mapping logic in backend instead of secondary ML model to keep MVP simple,
    # OR predict it if we wanted. For now, backend will estimate qty based on recommended fert.
    
    # Encode Target
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=RANDOM_STATE)
    
    # Scale Features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define models & hyperparameter grids
    models = {
        "RandomForest": {
            "model": RandomForestClassifier(random_state=RANDOM_STATE),
            "params": {
                "n_estimators": [50, 100],
                "max_depth": [None, 10, 20],
            }
        },
        "GradientBoosting": {
            "model": GradientBoostingClassifier(random_state=RANDOM_STATE),
            "params": {
                "n_estimators": [50, 100],
                "learning_rate": [0.01, 0.1],
                "max_depth": [3, 5]
            }
        },
        "XGBoost": {
            "model": XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=RANDOM_STATE),
            "params": {
                "n_estimators": [50, 100],
                "learning_rate": [0.01, 0.1],
                "max_depth": [3, 5]
            }
        }
    }
    
    results = {}
    best_model_name = ""
    best_model = None
    best_f1 = 0
    
    for model_name, mp in models.items():
        print(f"Training and tuning {model_name}...")
        
        # Untuned performance (default params)
        untuned_model = mp["model"]
        untuned_model.fit(X_train_scaled, y_train)
        y_pred_untuned = untuned_model.predict(X_test_scaled)
        
        untuned_acc = accuracy_score(y_test, y_pred_untuned)
        untuned_f1 = f1_score(y_test, y_pred_untuned, average='weighted')
        
        # Grid Search with CV
        clf = GridSearchCV(mp["model"], mp["params"], cv=5, scoring='f1_weighted', n_jobs=-1)
        clf.fit(X_train_scaled, y_train)
        
        tuned_model = clf.best_estimator_
        y_pred_tuned = tuned_model.predict(X_test_scaled)
        
        acc = accuracy_score(y_test, y_pred_tuned)
        prec = precision_score(y_test, y_pred_tuned, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred_tuned, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred_tuned, average='weighted')
        cm = confusion_matrix(y_test, y_pred_tuned)
        
        results[model_name] = {
            "untuned": {
                "accuracy": round(untuned_acc, 4),
                "f1_score": round(untuned_f1, 4)
            },
            "tuned": {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "best_params": clf.best_params_,
                "confusion_matrix": cm.tolist()
            }
        }
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = model_name
            best_model = tuned_model
            
    print(f"Best Model: {best_model_name} with F1-Score: {best_f1:.4f}")
    
    # Save artifacts
    artifacts_path = os.path.join(MODEL_DIR, "artifacts")
    os.makedirs(artifacts_path, exist_ok=True)
    
    joblib.dump(best_model, os.path.join(artifacts_path, "best_model.pkl"))
    joblib.dump(scaler, os.path.join(artifacts_path, "scaler.pkl"))
    joblib.dump(le, os.path.join(artifacts_path, "encoder.pkl"))
    
    with open(os.path.join(artifacts_path, "metrics.json"), "w") as f:
        json.dump({
            "best_model": best_model_name,
            "metrics": results,
            "classes": le.classes_.tolist()
        }, f, indent=4)
        
    print("Training complete! Artifacts saved.")

if __name__ == "__main__":
    train_and_evaluate()
