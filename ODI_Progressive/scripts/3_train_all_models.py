#!/usr/bin/env python3
"""
TRAIN RANDOM FOREST AND LINEAR REGRESSION MODELS (V2)

Trains additional models for comparison:
1. Random Forest Regressor
2. Linear Regression
"""

import numpy as np
import pandas as pd
import pickle
import json
import os
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("TRAIN ADDITIONAL MODELS (RF & LR) - V2")
print("="*80)

# ==============================================================================
# STEP 1: LOAD DATA
# ==============================================================================

print("\n[1/4] Loading training data (v2)...")

train_df = pd.read_csv('../data/progressive_full_train_v2.csv')
test_df = pd.read_csv('../data/progressive_full_test_v2.csv')

print(f"   Training: {len(train_df):,} samples")
print(f"   Testing: {len(test_df):,} samples")

# ==============================================================================
# STEP 2: PREPARE FEATURES
# ==============================================================================

print("\n[2/4] Preparing features...")

# Feature columns (same as XGBoost)
numeric_features = [
    'current_score', 'wickets_fallen', 'balls_bowled', 'balls_remaining',
    'runs_last_10_overs', 'current_run_rate',
    'team_batting_avg', 'team_elite_batsmen', 'team_batting_depth',
    'opp_bowling_economy', 'opp_elite_bowlers', 'opp_bowling_depth',
    'venue_avg_score', 'batsman_1_avg', 'batsman_2_avg'
]

categorical_features = ['venue']

all_features = numeric_features + categorical_features

X_train = train_df[all_features]
y_train = train_df['final_score']
X_test = test_df[all_features]
y_test = test_df['final_score']

# ==============================================================================
# STEP 3: TRAIN AND EVALUATE MODELS
# ==============================================================================

print("\n[3/4] Training and evaluating models...")

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ])

models_to_train = {
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
    'Linear Regression': LinearRegression()
}

results = {}

os.makedirs('../models', exist_ok=True)

for name, model in models_to_train.items():
    print(f"\n   Training {name}...")
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', model)
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    results[name] = {'r2': r2, 'mae': mae}
    
    print(f"   {name} Results:")
    print(f"   - R2 Score: {r2:.4f}")
    print(f"   - MAE: {mae:.2f} runs")
    
    # Save model
    filename = f"progressive_model_{name.lower().replace(' ', '_')}_v2.pkl"
    with open(f'../models/{filename}', 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"   [SAVED] ../models/{filename}")

# ==============================================================================
# STEP 4: SUMMARY
# ==============================================================================

print(f"\n{'='*80}")
print("SUMMARY OF NEW MODELS")
print(f"{'='*80}")

for name, metrics in results.items():
    print(f"\n{name}:")
    print(f"   R2: {metrics['r2']:.4f}")
    print(f"   MAE: {metrics['mae']:.2f}")

print(f"\n{'='*80}\n")
