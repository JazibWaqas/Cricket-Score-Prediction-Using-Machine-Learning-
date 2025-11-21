#!/usr/bin/env python3
"""
COMPARE OLD vs NEW MODEL PERFORMANCE

Tests both models on the same validation dataset and compares results.
"""

import numpy as np
import pandas as pd
import pickle
import json
from sklearn.metrics import r2_score, mean_absolute_error
import os

print("\n" + "="*80)
print("MODEL COMPARISON: OLD vs NEW")
print("="*80)

# ==============================================================================
# STEP 1: LOAD BOTH MODELS
# ==============================================================================

print("\n[1/4] Loading models...")

# Load old model
try:
    with open('../models/progressive_model_full_features.pkl', 'rb') as f:
        old_model = pickle.load(f)
    print("   [OK] Old model loaded")
except Exception as e:
    print(f"   [ERROR] Could not load old model: {e}")
    old_model = None

# Load new XGBoost model (v2)
try:
    with open('../models/progressive_model_xgboost_v2.pkl', 'rb') as f:
        xgb_model = pickle.load(f)
    print("   [OK] XGBoost v2 model loaded")
except Exception as e:
    print(f"   [ERROR] Could not load XGBoost v2 model: {e}")
    xgb_model = None

# Load Random Forest model (v2)
try:
    with open('../models/progressive_model_random_forest_v2.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    print("   [OK] Random Forest v2 model loaded")
except Exception as e:
    print(f"   [WARNING] Could not load Random Forest v2 model: {e}")
    rf_model = None

# Load Linear Regression model (v2)
try:
    with open('../models/progressive_model_linear_regression_v2.pkl', 'rb') as f:
        lr_model = pickle.load(f)
    print("   [OK] Linear Regression v2 model loaded")
except Exception as e:
    print(f"   [WARNING] Could not load Linear Regression v2 model: {e}")
    lr_model = None



# ==============================================================================
# STEP 2: LOAD VALIDATION DATA
# ==============================================================================

print("\n[2/4] Loading validation data...")

# Use v2 test set for comparison
test_df = pd.read_csv('../data/progressive_full_test_v2.csv')

# Load feature names
with open('../models/feature_names.json', 'r') as f:
    feature_info = json.load(f)

all_features = feature_info['all_features']

X_test = test_df[all_features]
y_test = test_df['final_score']

print(f"   Test samples: {len(X_test):,}")

# ==============================================================================
# STEP 3: MAKE PREDICTIONS WITH BOTH MODELS
# ==============================================================================

print("\n[3/4] Making predictions...")

models = {}
if old_model: models['Old XGBoost'] = old_model
if xgb_model: models['XGBoost v2'] = xgb_model
if rf_model: models['Random Forest v2'] = rf_model
if lr_model: models['Linear Regression v2'] = lr_model

predictions = {}
for name, model in models.items():
    print(f"   Predicting with {name}...")
    predictions[name] = model.predict(X_test)

# ==============================================================================
# STEP 4: COMPARE RESULTS
# ==============================================================================

print("\n[4/4] Comparing results...")

results = {}
for name, y_pred in predictions.items():
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    errors = np.abs(y_pred - y_test)
    within_30 = (errors <= 30).sum()
    
    results[name] = {
        'r2': float(r2),
        'mae': float(mae),
        'within_30': int(within_30),
        'within_30_pct': float(100 * within_30 / len(y_test))
    }

# Print comparison
print("\n" + "="*100)
print("COMPARISON RESULTS")
print("="*100)

print(f"\n{'Model':<25} {'R² Score':<15} {'MAE (runs)':<15} {'Accuracy (±30)':<20}")
print("-" * 80)

for name, metrics in results.items():
    print(f"{name:<25} {metrics['r2']:.4f}{'':<9} {metrics['mae']:.2f}{'':<9} {metrics['within_30_pct']:.1f}%")

# Save comparison results
os.makedirs('../results', exist_ok=True)
with open('../results/model_comparison_v2.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n[SAVED] ../results/model_comparison_v2.json")

print("\n" + "="*80 + "\n")

