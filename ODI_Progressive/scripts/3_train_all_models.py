#!/usr/bin/env python3
"""
TRAIN ALL MODELS: XGBoost, Random Forest, Linear Regression

Trains all three models and saves them for comparison.
"""

import numpy as np
import pandas as pd
import pickle
import json
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import warnings
import os
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("TRAIN ALL MODELS: XGBoost, Random Forest, Linear Regression")
print("="*80)

# ==============================================================================
# STEP 1: LOAD DATA
# ==============================================================================

print("\n[1/6] Loading training data...")

train_df = pd.read_csv('../data/progressive_full_train.csv')
test_df = pd.read_csv('../data/progressive_full_test.csv')

print(f"   Training: {len(train_df):,} samples")
print(f"   Testing: {len(test_df):,} samples")

# ==============================================================================
# STEP 2: PREPARE FEATURES
# ==============================================================================

print("\n[2/6] Preparing features...")

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

print(f"   Features: {len(all_features)} total")

# ==============================================================================
# STEP 3: BUILD PREPROCESSOR (shared by all models)
# ==============================================================================

print("\n[3/6] Building preprocessor...")

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ])

print("   Preprocessor created")

# ==============================================================================
# STEP 4: TRAIN ALL MODELS
# ==============================================================================

print("\n[4/6] Training models...")

models = {
    'XGBoost': XGBRegressor(
        n_estimators=400,
        max_depth=7,
        learning_rate=0.1,
        random_state=42,
        tree_method='hist',
        n_jobs=-1
    ),
    'RandomForest': RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ),
    'LinearRegression': LinearRegression()
}

trained_models = {}
results = {}

for model_name, model in models.items():
    print(f"\n   Training {model_name}...")
    
    # Create pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', model)
    ])
    
    # Train
    pipeline.fit(X_train, y_train)
    trained_models[model_name] = pipeline
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    results[model_name] = {
        'r2': r2,
        'mae': mae,
        'model': pipeline
    }
    
    print(f"      R² = {r2:.4f}, MAE = {mae:.2f} runs")

# ==============================================================================
# STEP 5: SAVE MODELS
# ==============================================================================

print("\n[5/6] Saving models...")

os.makedirs('../models', exist_ok=True)

for model_name, pipeline in trained_models.items():
    filename = f'progressive_model_{model_name.lower().replace(" ", "_")}.pkl'
    with open(f'../models/{filename}', 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"   [SAVED] {filename}")

# Save feature names (same for all)
feature_info = {
    'numeric_features': numeric_features,
    'categorical_features': categorical_features,
    'all_features': all_features
}
with open('../models/feature_names.json', 'w') as f:
    json.dump(feature_info, f, indent=2)

# ==============================================================================
# STEP 6: SUMMARY
# ==============================================================================

print("\n[6/6] Training Summary...")

print(f"\n{'='*80}")
print("TRAINING RESULTS SUMMARY")
print(f"{'='*80}")

print(f"\n{'Model':<20} {'R² Score':<15} {'MAE (runs)':<15}")
print("-" * 50)

for model_name in ['XGBoost', 'RandomForest', 'LinearRegression']:
    r2 = results[model_name]['r2']
    mae = results[model_name]['mae']
    print(f"{model_name:<20} {r2:.4f} ({r2*100:.2f}%){'':<5} {mae:.2f}")

# Best model
best_model = max(results.items(), key=lambda x: x[1]['r2'])
print(f"\nBest Model: {best_model[0]} (R² = {best_model[1]['r2']:.4f})")

print(f"\n{'='*80}\n")

