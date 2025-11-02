#!/usr/bin/env python3
"""
EXTRACT ACTUAL FEATURE IMPORTANCE FROM TRAINED MODEL
===================================================

This script extracts the actual feature importance values from the trained
XGBoost model to see what the model truly learned.
"""

import pickle
import json
import pandas as pd
import numpy as np

print("\n" + "="*80)
print("EXTRACT FEATURE IMPORTANCE FROM TRAINED MODEL")
print("="*80)

# Load model
print("\n[1/3] Loading trained model...")
with open('../models/progressive_model_full_features.pkl', 'rb') as f:
    pipeline = pickle.load(f)

# Get the XGBoost regressor from pipeline
xgb_model = pipeline.named_steps['regressor']

# Load feature names
with open('../models/feature_names.json', 'r') as f:
    feature_info = json.load(f)

print(f"   Model loaded")
print(f"   Number of trees: {xgb_model.n_estimators}")

# Extract feature importance
print("\n[2/3] Extracting feature importance...")

# Get feature names after preprocessing
# Need to handle the fact that categorical features are one-hot encoded
numeric_features = feature_info['numeric_features']
categorical_feature = feature_info['categorical_features'][0]  # 'venue'

# For numeric features, names are preserved
# For categorical (venue), we need to check how many one-hot columns were created
preprocessor = pipeline.named_steps['preprocessor']

# Get feature importance (default is 'weight' - number of times feature used in splits)
importance_weight = xgb_model.feature_importances_

# Get transformed feature names
# Numeric features first, then categorical
transformed_feature_names = []
transformed_feature_names.extend(numeric_features)

# For categorical, we need to see how many categories were encoded
# Get the transformer for categorical
cat_transformer = preprocessor.named_transformers_['cat']
if hasattr(cat_transformer, 'categories_'):
    venue_categories = cat_transformer.categories_[0]
    # Create names for one-hot encoded venue features
    for cat in venue_categories:
        transformed_feature_names.append(f'{categorical_feature}_{cat}')

print(f"   Total features after encoding: {len(transformed_feature_names)}")
print(f"   Feature importance array length: {len(importance_weight)}")

# Create importance DataFrame
importance_df = pd.DataFrame({
    'feature': transformed_feature_names[:len(importance_weight)],
    'importance': importance_weight
}).sort_values('importance', ascending=False)

# Normalize importance to percentages
importance_df['importance_pct'] = (importance_df['importance'] / importance_df['importance'].sum() * 100).round(2)

print("\n[3/3] Feature Importance Analysis")
print("="*80)

print("\nTOP 15 FEATURES BY IMPORTANCE:")
print("-" * 60)
print(f"{'Rank':<5} {'Feature':<35} {'Importance':<15} {'%':<10}")
print("-" * 60)

for idx, (_, row) in enumerate(importance_df.head(15).iterrows(), 1):
    print(f"{idx:<5} {row['feature']:<35} {row['importance']:<15.6f} {row['importance_pct']:<10.2f}%")

# Group by feature categories
print("\n" + "="*80)
print("FEATURE IMPORTANCE BY CATEGORY:")
print("="*80)

# Match State Features
match_state_features = ['current_score', 'wickets_fallen', 'balls_bowled', 
                       'balls_remaining', 'runs_last_10_overs', 'current_run_rate']
match_state_importance = importance_df[importance_df['feature'].isin(match_state_features)]['importance_pct'].sum()

# Batting Team Features
batting_features = ['team_batting_avg', 'team_elite_batsmen', 'team_batting_depth']
batting_importance = importance_df[importance_df['feature'].isin(batting_features)]['importance_pct'].sum()

# Opposition Features
opposition_features = ['opp_bowling_economy', 'opp_elite_bowlers', 'opp_bowling_depth']
opposition_importance = importance_df[importance_df['feature'].isin(opposition_features)]['importance_pct'].sum()

# Venue Features
venue_features = [f for f in importance_df['feature'] if f.startswith('venue') or f == 'venue_avg_score']
venue_importance = importance_df[importance_df['feature'].isin(venue_features)]['importance_pct'].sum()

# Current Batsmen Features
batsmen_features = ['batsman_1_avg', 'batsman_2_avg']
batsmen_importance = importance_df[importance_df['feature'].isin(batsmen_features)]['importance_pct'].sum()

print(f"\nMatch State Features:        {match_state_importance:.2f}%")
print(f"Batting Team Features:      {batting_importance:.2f}%")
print(f"Opposition Features:        {opposition_importance:.2f}%")
print(f"Venue Features:            {venue_importance:.2f}%")
print(f"Current Batsmen Features:   {batsmen_importance:.2f}%")

# Save results
output_path = '../results/feature_importance_analysis.txt'
print(f"\n{'='*80}")
print("SAVING RESULTS")
print(f"{'='*80}")
print(f"   [SAVED] {output_path}")

with open(output_path, 'w') as f:
    f.write("="*80 + "\n")
    f.write("FEATURE IMPORTANCE ANALYSIS\n")
    f.write("="*80 + "\n\n")
    
    f.write("TOP 15 FEATURES BY IMPORTANCE:\n")
    f.write("-" * 80 + "\n")
    for idx, (_, row) in enumerate(importance_df.head(15).iterrows(), 1):
        f.write(f"{idx:2d}. {row['feature']:<40} {row['importance_pct']:>6.2f}%\n")
    
    f.write("\n" + "="*80 + "\n")
    f.write("BY CATEGORY:\n")
    f.write("="*80 + "\n")
    f.write(f"Match State Features:        {match_state_importance:.2f}%\n")
    f.write(f"Batting Team Features:      {batting_importance:.2f}%\n")
    f.write(f"Opposition Features:        {opposition_importance:.2f}%\n")
    f.write(f"Venue Features:            {venue_importance:.2f}%\n")
    f.write(f"Current Batsmen Features:   {batsmen_importance:.2f}%\n")

print(f"\n{'='*80}\n")

