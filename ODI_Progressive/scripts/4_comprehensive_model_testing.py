#!/usr/bin/env python3
"""
COMPREHENSIVE MODEL TESTING

Tests all three models (XGBoost, Random Forest, Linear Regression) on:
1. Test set performance
2. Real international matches
3. Stage-by-stage breakdown
4. Best/worst predictions
5. What-if scenarios
"""

import numpy as np
import pandas as pd
import pickle
import json
import os
from sklearn.metrics import r2_score, mean_absolute_error
from collections import defaultdict

print("\n" + "="*80)
print("COMPREHENSIVE MODEL TESTING")
print("="*80)

# ==============================================================================
# STEP 1: LOAD ALL MODELS
# ==============================================================================

print("\n[1/7] Loading models...")

models = {}
model_names = ['XGBoost', 'RandomForest', 'LinearRegression']

for model_name in model_names:
    filename = f'../models/progressive_model_{model_name.lower().replace(" ", "_")}.pkl'
    try:
        with open(filename, 'rb') as f:
            models[model_name] = pickle.load(f)
        print(f"   [OK] {model_name} loaded")
    except Exception as e:
        print(f"   [ERROR] {model_name}: {e}")
        models[model_name] = None

# Remove None models
models = {k: v for k, v in models.items() if v is not None}

if len(models) == 0:
    print("\n[ERROR] No models loaded!")
    exit(1)

# ==============================================================================
# STEP 2: LOAD TEST DATA
# ==============================================================================

print("\n[2/7] Loading test data...")

test_df = pd.read_csv('../data/progressive_full_test.csv')
with open('../models/feature_names.json', 'r') as f:
    feature_info = json.load(f)

X_test = test_df[feature_info['all_features']]
y_test = test_df['final_score']

print(f"   Test samples: {len(X_test):,}")

# ==============================================================================
# STEP 3: TEST SET PERFORMANCE
# ==============================================================================

print("\n[3/7] Testing on test set...")

test_results = {}

for model_name, model in models.items():
    y_pred = model.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    errors = np.abs(y_pred - y_test)
    
    test_results[model_name] = {
        'r2': r2,
        'mae': mae,
        'predictions': y_pred,
        'errors': errors,
        'within_10': (errors <= 10).sum(),
        'within_20': (errors <= 20).sum(),
        'within_30': (errors <= 30).sum(),
        'best_prediction': errors.min(),
        'worst_prediction': errors.max(),
        'median_error': np.median(errors)
    }

# ==============================================================================
# STEP 4: STAGE-BY-STAGE PERFORMANCE
# ==============================================================================

print("\n[4/7] Analyzing stage-by-stage performance...")

stages = [
    ("Pre-match (ball 1)", 1),
    ("Early (ball 60)", 60),
    ("Mid (ball 120)", 120),
    ("Late (ball 180)", 180),
    ("Death (ball 240)", 240)
]

stage_results = {}

for model_name in models.keys():
    stage_results[model_name] = {}
    for stage_name, ball_num in stages:
        mask = test_df['balls_bowled'] == ball_num
        if mask.sum() > 0:
            y_pred = test_results[model_name]['predictions']
            r2 = r2_score(y_test[mask], y_pred[mask])
            mae = mean_absolute_error(y_test[mask], y_pred[mask])
            stage_results[model_name][stage_name] = {
                'r2': r2,
                'mae': mae,
                'samples': mask.sum()
            }

# ==============================================================================
# STEP 5: REAL INTERNATIONAL MATCHES
# ==============================================================================

print("\n[5/7] Testing on real international matches...")

# Load player database
player_db_path = '../../ODI_Progressive/CURRENT_player_database_977_quality_FIXED.json'
with open(player_db_path, 'r') as f:
    player_database = json.load(f)

# Helper functions
def get_batsman_avg(player_name, player_db):
    if player_name in player_db and 'batting' in player_db[player_name]:
        batting_data = player_db[player_name]['batting']
        avg = batting_data.get('average')
        if avg is not None and avg > 0:
            return float(avg)
    role = player_db.get(player_name, {}).get('role', 'Batsman')
    if 'Bowler' in role:
        return 18.0
    elif 'All-rounder' in role:
        return 25.0
    else:
        return 30.0

def calculate_batting_aggregates(players, player_db):
    avgs = []
    for player in players:
        avg = get_batsman_avg(player, player_db)
        avgs.append(avg)
    return {
        'team_batting_avg': np.mean(avgs),
        'team_elite_batsmen': sum(1 for a in avgs if a >= 40),
        'team_batting_depth': sum(1 for a in avgs if a >= 30)
    }

def calculate_bowling_aggregates(players, player_db):
    economies = []
    for player in players:
        if player in player_db and 'bowling' in player_db[player]:
            bowling_data = player_db[player]['bowling']
            economy = bowling_data.get('economy')
            if economy is not None and economy > 0:
                economies.append(float(economy))
            else:
                role = player_db.get(player, {}).get('role', 'Batsman')
                if 'Bowler' in role:
                    economies.append(5.0)
                elif 'All-rounder' in role:
                    economies.append(5.5)
                else:
                    economies.append(6.0)
        else:
            role = player_db.get(player, {}).get('role', 'Batsman')
            if 'Bowler' in role:
                economies.append(5.0)
            elif 'All-rounder' in role:
                economies.append(5.5)
            else:
                economies.append(6.0)
    
    if len(economies) == 0:
        return {'opp_bowling_economy': 5.5, 'opp_elite_bowlers': 0, 'opp_bowling_depth': 0}
    
    return {
        'opp_bowling_economy': np.mean(economies),
        'opp_elite_bowlers': sum(1 for e in economies if e < 4.8),
        'opp_bowling_depth': len(economies)
    }

# Load match data
ballbyball_dir = '../../raw_data/odis_ballbyBall'
all_files = [os.path.join(ballbyball_dir, f) for f in os.listdir(ballbyball_dir) if f.endswith('.json')]

INTERNATIONAL_TEAMS = [
    'India', 'Australia', 'England', 'Pakistan', 'South Africa',
    'New Zealand', 'Sri Lanka', 'Bangladesh', 'West Indies',
    'Afghanistan', 'Zimbabwe', 'Ireland', 'Scotland', 'Netherlands'
]

# Calculate venue averages
venue_scores = defaultdict(list)
for file in all_files[:200]:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            match = json.load(f)
        if 'innings' not in match or len(match['innings']) == 0:
            continue
        innings = match['innings'][0]
        venue = match['info'].get('venue', 'Unknown')
        final_score = sum(d.get('runs', {}).get('total', 0) for o in innings.get('overs', []) for d in o.get('deliveries', []))
        if final_score > 0:
            venue_scores[venue].append(final_score)
    except:
        continue

global_avg = np.mean([s for scores in venue_scores.values() for s in scores]) if venue_scores else 250.0
venue_avg_map = {v: np.mean(scores) if len(scores) >= 10 else global_avg for v, scores in venue_scores.items()}

# Process matches
real_match_results = {model_name: {'predictions': [], 'actuals': [], 'balls': []} for model_name in models.keys()}

checkpoints = [1, 60, 120, 180, 240]
match_count = 0

print("   Processing international matches...")

for file in all_files:
    if match_count >= 300:  # Limit for speed
        break
    try:
        with open(file, 'r', encoding='utf-8') as f:
            match = json.load(f)
        
        if 'innings' not in match or len(match['innings']) == 0:
            continue
        
        innings = match['innings'][0]
        batting_team = innings.get('team', 'Unknown')
        info = match['info']
        venue = info.get('venue', 'Unknown')
        teams = list(info.get('players', {}).keys())
        
        if len(teams) != 2:
            continue
        
        if batting_team not in INTERNATIONAL_TEAMS:
            continue
        
        batting_team_players = info['players'].get(batting_team, [])
        bowling_team = [t for t in teams if t != batting_team][0]
        bowling_team_players = info['players'].get(bowling_team, [])
        
        batting_agg = calculate_batting_aggregates(batting_team_players, player_database)
        bowling_agg = calculate_bowling_aggregates(bowling_team_players, player_database)
        venue_avg_score = venue_avg_map.get(venue, global_avg)
        
        final_score = sum(d.get('runs', {}).get('total', 0) for o in innings.get('overs', []) for d in o.get('deliveries', []))
        
        if final_score < 100:
            continue
        
        cumulative_runs = 0
        cumulative_wickets = 0
        ball_number = 0
        recent_runs = []
        batsmen_at_crease = []
        
        for over in innings.get('overs', []):
            for delivery in over.get('deliveries', []):
                ball_number += 1
                cumulative_runs += delivery.get('runs', {}).get('total', 0)
                cumulative_wickets += 1 if 'wicket' in delivery else 0
                recent_runs.append(delivery.get('runs', {}).get('total', 0))
                if len(recent_runs) > 60:
                    recent_runs.pop(0)
                
                if ball_number in checkpoints:
                    runs_last_10 = sum(recent_runs[-60:]) if len(recent_runs) >= 60 else sum(recent_runs)
                    current_run_rate = (cumulative_runs / ball_number * 6) if ball_number > 0 else 0
                    
                    batsman_1_avg = get_batsman_avg(batsmen_at_crease[0] if len(batsmen_at_crease) > 0 else 'Unknown', player_database)
                    batsman_2_avg = get_batsman_avg(batsmen_at_crease[1] if len(batsmen_at_crease) > 1 else 'Unknown', player_database)
                    
                    features = {
                        'current_score': cumulative_runs,
                        'wickets_fallen': cumulative_wickets,
                        'balls_bowled': ball_number,
                        'balls_remaining': 300 - ball_number,
                        'runs_last_10_overs': runs_last_10,
                        'current_run_rate': current_run_rate,
                        'team_batting_avg': batting_agg['team_batting_avg'],
                        'team_elite_batsmen': batting_agg['team_elite_batsmen'],
                        'team_batting_depth': batting_agg['team_batting_depth'],
                        'opp_bowling_economy': bowling_agg['opp_bowling_economy'],
                        'opp_elite_bowlers': bowling_agg['opp_elite_bowlers'],
                        'opp_bowling_depth': bowling_agg['opp_bowling_depth'],
                        'venue_avg_score': venue_avg_score,
                        'batsman_1_avg': batsman_1_avg,
                        'batsman_2_avg': batsman_2_avg,
                        'venue': venue
                    }
                    
                    # Make predictions with all models
                    df = pd.DataFrame([features])
                    for model_name, model in models.items():
                        pred = model.predict(df)[0]
                        real_match_results[model_name]['predictions'].append(pred)
                        real_match_results[model_name]['actuals'].append(final_score)
                        real_match_results[model_name]['balls'].append(ball_number)
        
        match_count += 1
        if match_count % 50 == 0:
            print(f"      Processed {match_count} matches...")
    
    except Exception as e:
        continue

print(f"   Total: {match_count} matches processed")

# Calculate real match metrics
real_match_metrics = {}
for model_name in models.keys():
    preds = np.array(real_match_results[model_name]['predictions'])
    actuals = np.array(real_match_results[model_name]['actuals'])
    
    if len(preds) > 0:
        real_match_metrics[model_name] = {
            'r2': r2_score(actuals, preds),
            'mae': mean_absolute_error(actuals, preds),
            'errors': np.abs(preds - actuals),
            'samples': len(preds)
        }

# ==============================================================================
# STEP 6: BEST/WORST PREDICTIONS
# ==============================================================================

print("\n[6/7] Finding best/worst predictions...")

best_worst = {}

for model_name in models.keys():
    errors = test_results[model_name]['errors']
    best_idx = errors.argmin()
    worst_idx = errors.argmax()
    
    best_worst[model_name] = {
        'best': {
            'actual': y_test.iloc[best_idx],
            'predicted': test_results[model_name]['predictions'][best_idx],
            'error': errors[best_idx],
            'ball': test_df.iloc[best_idx]['balls_bowled'],
            'team': test_df.iloc[best_idx]['batting_team']
        },
        'worst': {
            'actual': y_test.iloc[worst_idx],
            'predicted': test_results[model_name]['predictions'][worst_idx],
            'error': errors[worst_idx],
            'ball': test_df.iloc[worst_idx]['balls_bowled'],
            'team': test_df.iloc[worst_idx]['batting_team']
        }
    }

# ==============================================================================
# STEP 7: GENERATE COMPREHENSIVE REPORT
# ==============================================================================

print("\n[7/7] Generating comprehensive report...")

report = f"""
# 🏏 COMPREHENSIVE MODEL COMPARISON RESULTS

**Test Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Test Samples:** {len(X_test):,}  
**Real International Matches:** {match_count} matches

---

## 📊 EXECUTIVE SUMMARY

"""

# Overall comparison
report += "\n### Overall Performance (Test Set)\n\n"
report += "| Model | R² Score | MAE (runs) | Accuracy ±10 | Accuracy ±20 | Accuracy ±30 |\n"
report += "|-------|----------|------------|--------------|--------------|--------------|\n"

for model_name in ['XGBoost', 'RandomForest', 'LinearRegression']:
    if model_name in test_results:
        r = test_results[model_name]
        report += f"| {model_name} | {r['r2']:.4f} ({r['r2']*100:.2f}%) | {r['mae']:.2f} | {r['within_10']/len(y_test)*100:.1f}% | {r['within_20']/len(y_test)*100:.1f}% | {r['within_30']/len(y_test)*100:.1f}% |\n"

# Best model
best_test = max(test_results.items(), key=lambda x: x[1]['r2'])
report += f"\n**Best Model (Test Set):** {best_test[0]} (R² = {best_test[1]['r2']:.4f})\n"

# Real matches
if real_match_metrics:
    report += "\n### Real International Matches Performance\n\n"
    report += "| Model | R² Score | MAE (runs) | Samples |\n"
    report += "|-------|----------|------------|----------|\n"
    
    for model_name in ['XGBoost', 'RandomForest', 'LinearRegression']:
        if model_name in real_match_metrics:
            m = real_match_metrics[model_name]
            report += f"| {model_name} | {m['r2']:.4f} ({m['r2']*100:.2f}%) | {m['mae']:.2f} | {m['samples']} |\n"
    
    best_real = max(real_match_metrics.items(), key=lambda x: x[1]['r2'])
    report += f"\n**Best Model (Real Matches):** {best_real[0]} (R² = {best_real[1]['r2']:.4f})\n"

# Stage-by-stage
report += "\n## 📈 Stage-by-Stage Performance\n\n"
report += "### Test Set Performance by Stage\n\n"

for stage_name, _ in stages:
    report += f"#### {stage_name}\n\n"
    report += "| Model | R² Score | MAE (runs) | Samples |\n"
    report += "|-------|----------|------------|----------|\n"
    
    for model_name in ['XGBoost', 'RandomForest', 'LinearRegression']:
        if model_name in stage_results and stage_name in stage_results[model_name]:
            s = stage_results[model_name][stage_name]
            report += f"| {model_name} | {s['r2']:.4f} ({s['r2']*100:.2f}%) | {s['mae']:.2f} | {s['samples']} |\n"
    
    report += "\n"

# Best/Worst predictions
report += "\n## 🎯 Best and Worst Predictions\n\n"

for model_name in ['XGBoost', 'RandomForest', 'LinearRegression']:
    if model_name in best_worst:
        report += f"### {model_name}\n\n"
        bw = best_worst[model_name]
        report += f"**Best Prediction:**\n"
        report += f"- Team: {bw['best']['team']}\n"
        report += f"- Ball: {bw['best']['ball']}\n"
        report += f"- Actual: {bw['best']['actual']:.0f} runs\n"
        report += f"- Predicted: {bw['best']['predicted']:.0f} runs\n"
        report += f"- Error: {bw['best']['error']:.2f} runs\n\n"
        
        report += f"**Worst Prediction:**\n"
        report += f"- Team: {bw['worst']['team']}\n"
        report += f"- Ball: {bw['worst']['ball']}\n"
        report += f"- Actual: {bw['worst']['actual']:.0f} runs\n"
        report += f"- Predicted: {bw['worst']['predicted']:.0f} runs\n"
        report += f"- Error: {bw['worst']['error']:.2f} runs\n\n"

# Detailed analysis
report += "\n## 🔍 Detailed Analysis\n\n"

for model_name in ['XGBoost', 'RandomForest', 'LinearRegression']:
    if model_name in test_results:
        r = test_results[model_name]
        report += f"### {model_name}\n\n"
        report += f"- **R² Score:** {r['r2']:.4f} ({r['r2']*100:.2f}%)\n"
        report += f"- **MAE:** {r['mae']:.2f} runs\n"
        report += f"- **Median Error:** {r['median_error']:.2f} runs\n"
        report += f"- **Best Prediction Error:** {r['best_prediction']:.2f} runs\n"
        report += f"- **Worst Prediction Error:** {r['worst_prediction']:.2f} runs\n"
        report += f"- **Accuracy ±10 runs:** {r['within_10']/len(y_test)*100:.1f}% ({r['within_10']}/{len(y_test)})\n"
        report += f"- **Accuracy ±20 runs:** {r['within_20']/len(y_test)*100:.1f}% ({r['within_20']}/{len(y_test)})\n"
        report += f"- **Accuracy ±30 runs:** {r['within_30']/len(y_test)*100:.1f}% ({r['within_30']}/{len(y_test)})\n\n"

# Recommendations
report += "\n## ✅ Recommendations\n\n"

if best_test[0] == best_real[0] if real_match_metrics else True:
    report += f"**Recommended Model:** {best_test[0]}\n\n"
    report += f"- Best overall performance on test set\n"
    if real_match_metrics:
        report += f"- Best performance on real international matches\n"
    report += f"- R² Score: {best_test[1]['r2']:.4f}\n"
    report += f"- MAE: {best_test[1]['mae']:.2f} runs\n"
else:
    report += "**Note:** Different models perform best on test set vs real matches. Consider using the model that performs best on real matches for production.\n\n"

report += "\n---\n"
report += f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

# Save report
os.makedirs('../results', exist_ok=True)
with open('../results/MODELS_RESULTS.md', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"   [SAVED] ../results/MODELS_RESULTS.md")

# Also save JSON data
json_data = {
    'test_results': {k: {m: float(v) if isinstance(v, (np.integer, np.floating)) else int(v) if isinstance(v, np.integer) else v for m, v in r.items() if m != 'predictions' and m != 'errors'} for k, r in test_results.items()},
    'real_match_metrics': {k: {m: float(v) if isinstance(v, (np.integer, np.floating)) else int(v) if isinstance(v, np.integer) else v for m, v in r.items() if m != 'errors'} for k, r in real_match_metrics.items()},
    'stage_results': {k: {s: {m: float(v) if isinstance(v, (np.integer, np.floating)) else int(v) if isinstance(v, np.integer) else v for m, v in stage.items()} for s, stage in stages.items()} for k, stages in stage_results.items()},
    'best_worst': best_worst
}

with open('../results/models_comparison_data.json', 'w') as f:
    json.dump(json_data, f, indent=2)

print(f"   [SAVED] ../results/models_comparison_data.json")

print("\n" + "="*80)
print("COMPREHENSIVE TESTING COMPLETE")
print("="*80)
print(f"\nResults saved to:")
print(f"  - ../results/MODELS_RESULTS.md")
print(f"  - ../results/models_comparison_data.json")
print("\n" + "="*80 + "\n")

