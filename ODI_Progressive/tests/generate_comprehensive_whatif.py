import pickle
import pandas as pd
import json
import numpy as np
import os

print("="*80)
print("GENERATING COMPREHENSIVE WHAT-IF DATA")
print("="*80)

# Load Model and Database
try:
    with open('../models/progressive_model_random_forest_v2.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('../../ODI_Progressive/CURRENT_player_database_977_quality_FIXED.json', 'r') as f:
        player_db = json.load(f)
except Exception as e:
    print(f"Error loading: {e}")
    exit()

def get_player_stats(name):
    if name in player_db:
        return player_db[name].get('batting', {}).get('average', 30.0)
    return 30.0

def predict(updates={}):
    # Baseline: Standard Match (India vs Australia style)
    # 30 overs, 180/3 (Projected ~300)
    data = {
        'current_score': 180,
        'wickets_fallen': 3,
        'balls_bowled': 180,
        'balls_remaining': 120,
        'runs_last_10_overs': 60,
        'current_run_rate': 6.0,
        'team_batting_avg': 38.0,
        'team_elite_batsmen': 4,
        'team_batting_depth': 8,
        'opp_bowling_economy': 5.2,
        'opp_elite_bowlers': 3,
        'opp_bowling_depth': 6,
        'venue_avg_score': 270,
        'batsman_1_avg': 45.0,
        'batsman_2_avg': 35.0,
        'venue': 'Generic Venue'
    }
    data.update(updates)
    return model.predict(pd.DataFrame([data]))[0]

results = {}

# 1. Player Swaps (The "Star Power" Effect)
base_pred = predict()
results['baseline'] = base_pred

# Swap Set Batsman (45 avg) for:
results['swap_legend'] = predict({'batsman_1_avg': 58.0}) # Kohli-like
results['swap_average'] = predict({'batsman_1_avg': 30.0}) # Avg player
results['swap_tailender'] = predict({'batsman_1_avg': 10.0}) # Bowler

# 2. Match Context (The "Collapse" Effect)
# Same score (180), but wickets lost varies
results['collapse_mild'] = predict({'wickets_fallen': 5})
results['collapse_severe'] = predict({'wickets_fallen': 7})
results['collapse_total'] = predict({'wickets_fallen': 9})

# 3. Venue Impact
results['venue_batting'] = predict({'venue_avg_score': 320})
results['venue_bowling'] = predict({'venue_avg_score': 220})

# 4. Team Quality Impact (Batting Depth)
results['team_weak'] = predict({'team_batting_avg': 25.0, 'team_elite_batsmen': 0})
results['team_strong'] = predict({'team_batting_avg': 42.0, 'team_elite_batsmen': 6})

# Print Results for Capture
print(json.dumps(results, indent=2))
