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

# Load new model
try:
    with open('../models/progressive_model_full_features_NEW.pkl', 'rb') as f:
        new_model = pickle.load(f)
    print("   [OK] New model loaded")
except Exception as e:
    print(f"   [ERROR] Could not load new model: {e}")
    new_model = None

if old_model is None or new_model is None:
    print("\n[ERROR] Cannot compare - one or both models missing")
    exit(1)

# ==============================================================================
# STEP 2: LOAD VALIDATION DATA
# ==============================================================================

print("\n[2/4] Loading validation data...")

# Use test set for comparison
test_df = pd.read_csv('../data/progressive_full_test.csv')

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

print("   Predicting with OLD model...")
y_pred_old = old_model.predict(X_test)

print("   Predicting with NEW model...")
y_pred_new = new_model.predict(X_test)

# ==============================================================================
# STEP 4: COMPARE RESULTS
# ==============================================================================

print("\n[4/4] Comparing results...")

# Overall metrics
old_r2 = r2_score(y_test, y_pred_old)
new_r2 = r2_score(y_test, y_pred_new)
old_mae = mean_absolute_error(y_test, y_pred_old)
new_mae = mean_absolute_error(y_test, y_pred_new)

# Accuracy bands
old_errors = np.abs(y_pred_old - y_test)
new_errors = np.abs(y_pred_new - y_test)

old_within_10 = (old_errors <= 10).sum()
old_within_20 = (old_errors <= 20).sum()
old_within_30 = (old_errors <= 30).sum()

new_within_10 = (new_errors <= 10).sum()
new_within_20 = (new_errors <= 20).sum()
new_within_30 = (new_errors <= 30).sum()

# Print comparison
print("\n" + "="*80)
print("COMPARISON RESULTS")
print("="*80)

print(f"\n{'Metric':<30} {'OLD Model':<20} {'NEW Model':<20} {'Difference':<20}")
print("-" * 90)

# R²
r2_diff = new_r2 - old_r2
r2_pct = (r2_diff / old_r2 * 100) if old_r2 > 0 else 0
print(f"{'R² Score':<30} {old_r2:.4f} ({old_r2*100:.2f}%){'':<5} {new_r2:.4f} ({new_r2*100:.2f}%){'':<5} {r2_diff:+.4f} ({r2_pct:+.2f}%)")

# MAE
mae_diff = new_mae - old_mae
mae_pct = (mae_diff / old_mae * 100) if old_mae > 0 else 0
print(f"{'MAE (runs)':<30} {old_mae:.2f}{'':<12} {new_mae:.2f}{'':<12} {mae_diff:+.2f} ({mae_pct:+.2f}%)")

# Accuracy bands
print(f"\n{'Accuracy Band':<30} {'OLD Model':<20} {'NEW Model':<20} {'Difference':<20}")
print("-" * 90)

for threshold, old_count, new_count in [(10, old_within_10, new_within_10),
                                        (20, old_within_20, new_within_20),
                                        (30, old_within_30, new_within_30)]:
    old_pct = 100 * old_count / len(y_test)
    new_pct = 100 * new_count / len(y_test)
    diff_pct = new_pct - old_pct
    print(f"Within ±{threshold} runs{'':<20} {old_pct:.1f}% ({old_count}/{len(y_test)}){'':<5} {new_pct:.1f}% ({new_count}/{len(y_test)}){'':<5} {diff_pct:+.1f}%")

# Performance by stage
print(f"\n{'='*80}")
print("PERFORMANCE BY MATCH STAGE")
print("="*80)

stages = [
    ("Pre-match (0-10 overs)", 240, 300),
    ("Early (10-20 overs)", 180, 240),
    ("Mid (20-30 overs)", 120, 180),
    ("Late (30-40 overs)", 60, 120),
    ("Death (40-50 overs)", 0, 60)
]

print(f"\n{'Stage':<25} {'OLD R²':<12} {'NEW R²':<12} {'OLD MAE':<12} {'NEW MAE':<12}")
print("-" * 80)

for stage_name, min_balls, max_balls in stages:
    mask = (test_df['balls_remaining'] >= min_balls) & (test_df['balls_remaining'] < max_balls)
    if mask.sum() > 0:
        old_stage_r2 = r2_score(y_test[mask], y_pred_old[mask])
        new_stage_r2 = r2_score(y_test[mask], y_pred_new[mask])
        old_stage_mae = mean_absolute_error(y_test[mask], y_pred_old[mask])
        new_stage_mae = mean_absolute_error(y_test[mask], y_pred_new[mask])
        
        print(f"{stage_name:<25} {old_stage_r2:.4f}{'':<6} {new_stage_r2:.4f}{'':<6} {old_stage_mae:.2f}{'':<8} {new_stage_mae:.2f}")

# ==============================================================================
# VERDICT
# ==============================================================================

print(f"\n{'='*80}")
print("VERDICT")
print("="*80)

better_r2 = new_r2 > old_r2
better_mae = new_mae < old_mae
better_accuracy = new_within_30 > old_within_30

improvements = sum([better_r2, better_mae, better_accuracy])

if improvements >= 2:
    verdict = "[BETTER] NEW MODEL IS BETTER"
    recommendation = "Use the NEW model (progressive_model_full_features_NEW.pkl)"
elif improvements == 1:
    verdict = "[MIXED] MIXED RESULTS"
    recommendation = "New model has some improvements but also some regressions. Review detailed metrics."
else:
    verdict = "[BETTER] OLD MODEL IS BETTER"
    recommendation = "Keep using the OLD model (progressive_model_full_features.pkl)"

print(f"\n{verdict}")
print(f"\nRecommendation: {recommendation}")

print(f"\nDetailed comparison:")
print(f"  R²: {'NEW better' if better_r2 else 'OLD better'} ({abs(r2_diff):.4f} difference)")
print(f"  MAE: {'NEW better' if better_mae else 'OLD better'} ({abs(mae_diff):.2f} runs difference)")
print(f"  Accuracy (±30): {'NEW better' if better_accuracy else 'OLD better'} ({abs(new_within_30 - old_within_30)} samples difference)")

# Save comparison results
os.makedirs('../results', exist_ok=True)
comparison = {
    'old_model': {
        'r2': float(old_r2),
        'mae': float(old_mae),
        'accuracy_within_10': float(100 * old_within_10 / len(y_test)),
        'accuracy_within_20': float(100 * old_within_20 / len(y_test)),
        'accuracy_within_30': float(100 * old_within_30 / len(y_test))
    },
    'new_model': {
        'r2': float(new_r2),
        'mae': float(new_mae),
        'accuracy_within_10': float(100 * new_within_10 / len(y_test)),
        'accuracy_within_20': float(100 * new_within_20 / len(y_test)),
        'accuracy_within_30': float(100 * new_within_30 / len(y_test))
    },
    'difference': {
        'r2': float(r2_diff),
        'mae': float(mae_diff),
        'accuracy_within_10': float(100 * (new_within_10 - old_within_10) / len(y_test)),
        'accuracy_within_20': float(100 * (new_within_20 - old_within_20) / len(y_test)),
        'accuracy_within_30': float(100 * (new_within_30 - old_within_30) / len(y_test))
    },
    'verdict': verdict,
    'recommendation': recommendation
}

with open('../results/model_comparison.json', 'w') as f:
    json.dump(comparison, f, indent=2)

print(f"\n[SAVED] ../results/model_comparison.json")

print("\n" + "="*80 + "\n")

