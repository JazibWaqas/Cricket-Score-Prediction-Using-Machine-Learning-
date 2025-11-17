#!/usr/bin/env python3
"""Compare OLD vs NEW model on REAL international matches"""

import numpy as np
import pandas as pd
import json
import pickle
import os
from sklearn.metrics import r2_score, mean_absolute_error
from collections import defaultdict

print("\n" + "="*80)
print("COMPARE BOTH MODELS ON REAL INTERNATIONAL MATCHES")
print("="*80)

# Load both models
print("\n[1/6] Loading models...")
with open('../models/progressive_model_full_features.pkl', 'rb') as f:
    old_model = pickle.load(f)
with open('../models/progressive_model_full_features_NEW.pkl', 'rb') as f:
    new_model = pickle.load(f)
print("   Both models loaded")

# Load player database
print("\n[2/6] Loading player database...")
player_db_path = '../../ODI_Progressive/CURRENT_player_database_977_quality_FIXED.json'
with open(player_db_path, 'r') as f:
    player_database = json.load(f)
print(f"   Loaded {len(player_database):,} players")

# Helper functions (same as validation script)
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
print("\n[3/6] Loading match data...")
ballbyball_dir = '../../raw_data/odis_ballbyBall'
all_files = [os.path.join(ballbyball_dir, f) for f in os.listdir(ballbyball_dir) if f.endswith('.json')]

INTERNATIONAL_TEAMS = [
    'India', 'Australia', 'England', 'Pakistan', 'South Africa',
    'New Zealand', 'Sri Lanka', 'Bangladesh', 'West Indies',
    'Afghanistan', 'Zimbabwe', 'Ireland', 'Scotland', 'Netherlands'
]

# Calculate venue averages
print("\n[4/6] Calculating venue averages...")
venue_scores = defaultdict(list)
for file in all_files[:100]:  # Sample for speed
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
print("\n[5/6] Processing international matches...")
results_old = []
results_new = []

checkpoints = [1, 60, 120, 180, 240]
match_count = 0

for file in all_files:
    if match_count >= 600:  # Limit for speed
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
                    
                    # Make predictions
                    df = pd.DataFrame([features])
                    old_pred = old_model.predict(df)[0]
                    new_pred = new_model.predict(df)[0]
                    
                    results_old.append({
                        'ball': ball_number,
                        'actual': final_score,
                        'predicted': old_pred
                    })
                    results_new.append({
                        'ball': ball_number,
                        'actual': final_score,
                        'predicted': new_pred
                    })
        
        match_count += 1
        if match_count % 100 == 0:
            print(f"   Processed {match_count} matches, {len(results_old)} predictions...")
    
    except Exception as e:
        continue

print(f"\n   Total: {match_count} matches, {len(results_old)} predictions")

# Compare results
print("\n[6/6] Comparing results...")

results_old_df = pd.DataFrame(results_old)
results_new_df = pd.DataFrame(results_new)

print("\n" + "="*80)
print("COMPARISON ON REAL INTERNATIONAL MATCHES")
print("="*80)

print(f"\nOverall Performance:")
old_r2 = r2_score(results_old_df['actual'], results_old_df['predicted'])
new_r2 = r2_score(results_new_df['actual'], results_new_df['predicted'])
old_mae = mean_absolute_error(results_old_df['actual'], results_old_df['predicted'])
new_mae = mean_absolute_error(results_new_df['actual'], results_new_df['predicted'])

print(f"  OLD: R² = {old_r2:.4f} ({old_r2*100:.2f}%), MAE = {old_mae:.2f} runs")
print(f"  NEW: R² = {new_r2:.4f} ({new_r2*100:.2f}%), MAE = {new_mae:.2f} runs")
print(f"  Difference: R² = {new_r2 - old_r2:+.4f}, MAE = {new_mae - old_mae:+.2f} runs")

print(f"\nStage-by-Stage (Checkpoints):")
stages = [
    ("Pre-match (ball 1)", 1),
    ("Early (ball 60)", 60),
    ("Mid (ball 120)", 120),
    ("Late (ball 180)", 180),
    ("Death (ball 240)", 240)
]

print(f"\n{'Stage':<25} {'OLD R²':<12} {'NEW R²':<12} {'OLD MAE':<12} {'NEW MAE':<12} {'Samples':<10}")
print("-" * 90)

for stage_name, ball_num in stages:
    old_mask = results_old_df['ball'] == ball_num
    new_mask = results_new_df['ball'] == ball_num
    
    if old_mask.sum() > 0:
        old_stage_r2 = r2_score(results_old_df[old_mask]['actual'], results_old_df[old_mask]['predicted'])
        new_stage_r2 = r2_score(results_new_df[new_mask]['actual'], results_new_df[new_mask]['predicted'])
        old_stage_mae = mean_absolute_error(results_old_df[old_mask]['actual'], results_old_df[old_mask]['predicted'])
        new_stage_mae = mean_absolute_error(results_new_df[new_mask]['actual'], results_new_df[new_mask]['predicted'])
        
        print(f"{stage_name:<25} {old_stage_r2:.4f}      {new_stage_r2:.4f}      {old_stage_mae:.2f}        {new_stage_mae:.2f}        {old_mask.sum():<10}")

print("\n" + "="*80)

