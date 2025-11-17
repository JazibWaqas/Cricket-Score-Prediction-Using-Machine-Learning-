#!/usr/bin/env python3
"""Compare both models on REAL international matches with proper stage-by-stage breakdown"""

import numpy as np
import pandas as pd
import json
import pickle
import os
from sklearn.metrics import r2_score, mean_absolute_error

print("\n" + "="*80)
print("MODEL COMPARISON ON REAL INTERNATIONAL MATCHES")
print("="*80)

# Load both models
print("\n[1/4] Loading models...")
with open('../models/progressive_model_full_features.pkl', 'rb') as f:
    old_model = pickle.load(f)
with open('../models/progressive_model_full_features_NEW.pkl', 'rb') as f:
    new_model = pickle.load(f)
print("   Both models loaded")

# Load test data
print("\n[2/4] Loading test data...")
test_df = pd.read_csv('../data/progressive_full_test.csv')
with open('../models/feature_names.json', 'r') as f:
    feature_info = json.load(f)

X_test = test_df[feature_info['all_features']]
y_test = test_df['final_score']

print(f"   Test samples: {len(X_test):,}")

# Make predictions
print("\n[3/4] Making predictions...")
old_pred = old_model.predict(X_test)
new_pred = new_model.predict(X_test)

# Compare by specific checkpoints (like validation script)
print("\n[4/4] Comparing by match stage checkpoints...")

stages = [
    ("Pre-match (ball 1)", 1),
    ("Early (ball 60, over 10)", 60),
    ("Mid (ball 120, over 20)", 120),
    ("Late (ball 180, over 30)", 180),
    ("Death (ball 240, over 40)", 240)
]

print("\n" + "="*80)
print("STAGE-BY-STAGE COMPARISON (Specific Checkpoints)")
print("="*80)
print(f"\n{'Stage':<30} {'OLD R²':<12} {'NEW R²':<12} {'OLD MAE':<12} {'NEW MAE':<12} {'Samples':<10}")
print("-" * 100)

for stage_name, ball_num in stages:
    mask = test_df['balls_bowled'] == ball_num
    if mask.sum() > 0:
        old_r2 = r2_score(y_test[mask], old_pred[mask])
        new_r2 = r2_score(y_test[mask], new_pred[mask])
        old_mae = mean_absolute_error(y_test[mask], old_pred[mask])
        new_mae = mean_absolute_error(y_test[mask], new_pred[mask])
        
        r2_diff = new_r2 - old_r2
        mae_diff = new_mae - old_mae
        
        print(f"{stage_name:<30} {old_r2:.4f}      {new_r2:.4f}      {old_mae:.2f}        {new_mae:.2f}        {mask.sum():<10}")
        print(f"{'':<30} ({r2_diff:+.4f})     ({mae_diff:+.2f})")

# Overall comparison
print("\n" + "="*80)
print("OVERALL COMPARISON")
print("="*80)

old_overall_r2 = r2_score(y_test, old_pred)
new_overall_r2 = r2_score(y_test, new_pred)
old_overall_mae = mean_absolute_error(y_test, old_pred)
new_overall_mae = mean_absolute_error(y_test, new_pred)

print(f"\nOverall R²: OLD = {old_overall_r2:.4f}, NEW = {new_overall_r2:.4f} (diff: {new_overall_r2 - old_overall_r2:+.4f})")
print(f"Overall MAE: OLD = {old_overall_mae:.2f}, NEW = {new_overall_mae:.2f} (diff: {new_overall_mae - old_overall_mae:+.2f})")

# Accuracy bands
old_errors = np.abs(old_pred - y_test)
new_errors = np.abs(new_pred - y_test)

print(f"\nAccuracy (±10 runs): OLD = {(old_errors <= 10).sum()/len(y_test)*100:.1f}%, NEW = {(new_errors <= 10).sum()/len(y_test)*100:.1f}%")
print(f"Accuracy (±20 runs): OLD = {(old_errors <= 20).sum()/len(y_test)*100:.1f}%, NEW = {(new_errors <= 20).sum()/len(y_test)*100:.1f}%")
print(f"Accuracy (±30 runs): OLD = {(old_errors <= 30).sum()/len(y_test)*100:.1f}%, NEW = {(new_errors <= 30).sum()/len(y_test)*100:.1f}%")

# Death overs specifically
print("\n" + "="*80)
print("DEATH OVERS (40-50) - WHERE R² SHOULD BE ~94%")
print("="*80)

death_mask = test_df['balls_bowled'] >= 240
if death_mask.sum() > 0:
    old_death_r2 = r2_score(y_test[death_mask], old_pred[death_mask])
    new_death_r2 = r2_score(y_test[death_mask], new_pred[death_mask])
    old_death_mae = mean_absolute_error(y_test[death_mask], old_pred[death_mask])
    new_death_mae = mean_absolute_error(y_test[death_mask], new_pred[death_mask])
    
    print(f"\nOLD Model (Death overs): R² = {old_death_r2:.4f} ({old_death_r2*100:.2f}%), MAE = {old_death_mae:.2f} runs")
    print(f"NEW Model (Death overs): R² = {new_death_r2:.4f} ({new_death_r2*100:.2f}%), MAE = {new_death_mae:.2f} runs")
    print(f"Difference: R² = {new_death_r2 - old_death_r2:+.4f}, MAE = {new_death_mae - old_death_mae:+.2f} runs")
    print(f"Samples: {death_mask.sum()}")

print("\n" + "="*80)

