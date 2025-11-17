#!/usr/bin/env python3
"""Analyze how many players/venues use defaults vs actual values"""

import json
import pandas as pd
import os

print("\n" + "="*80)
print("ANALYZING DEFAULTS VS ACTUAL VALUES")
print("="*80)

# ==============================================================================
# PLAYER DATABASE ANALYSIS
# ==============================================================================

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '../CURRENT_player_database_977_quality_FIXED.json')
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

print("\n" + "-"*80)
print("PLAYER DATABASE ANALYSIS")
print("-"*80)

# Define role-based defaults
BATTER_DEFAULT = 30.0
ALLROUNDER_DEFAULT = 25.0
BOWLER_DEFAULT = 18.0

BOWLER_ECON_DEFAULT = 5.0
ALLROUNDER_ECON_DEFAULT = 5.5
BATSMAN_ECON_DEFAULT = 6.0

# Analyze batting averages
players_with_actual_batting = 0
players_with_default_batting = 0
players_with_null_batting = 0

batting_defaults_by_role = {'Batsman': 0, 'All-rounder': 0, 'Bowler': 0, 'Wicketkeeper-Batsman': 0}

for name, player in db.items():
    batting = player.get('batting')
    role = player.get('role', 'Batsman')
    
    if not batting:
        players_with_null_batting += 1
        players_with_default_batting += 1
        batting_defaults_by_role[role] = batting_defaults_by_role.get(role, 0) + 1
    else:
        avg = batting.get('average')
        if avg is None or avg == 0:
            players_with_null_batting += 1
            players_with_default_batting += 1
            batting_defaults_by_role[role] = batting_defaults_by_role.get(role, 0) + 1
        else:
            # Check if it matches a default value (might be actual default or coincidence)
            expected_default = BATTER_DEFAULT
            if 'Bowler' in role:
                expected_default = BOWLER_DEFAULT
            elif 'All-rounder' in role:
                expected_default = ALLROUNDER_DEFAULT
            
            if avg == expected_default:
                # Could be default or actual value - check if it's exactly the default
                # For now, count as actual if it's in database (database script would have set it)
                players_with_actual_batting += 1
            else:
                players_with_actual_batting += 1

print(f"\nBATTING AVERAGES:")
print(f"  Players with ACTUAL averages: {players_with_actual_batting}/{len(db)} ({players_with_actual_batting/len(db)*100:.1f}%)")
print(f"  Players with NULL/0 averages: {players_with_null_batting}/{len(db)} ({players_with_null_batting/len(db)*100:.1f}%)")
print(f"  Note: Defaults are applied at PREDICTION TIME, not stored in database")

# Analyze bowling economy
players_with_actual_bowling = 0
players_with_default_bowling = 0
players_with_null_bowling = 0
players_no_bowling_data = 0

for name, player in db.items():
    role = player.get('role', 'Batsman')
    bowling = player.get('bowling')
    
    if not bowling:
        if 'Bowler' in role or 'All-rounder' in role:
            players_with_default_bowling += 1
        players_no_bowling_data += 1
    else:
        economy = bowling.get('economy')
        if economy is None or economy == 0:
            if 'Bowler' in role or 'All-rounder' in role:
                players_with_default_bowling += 1
            players_with_null_bowling += 1
        else:
            players_with_actual_bowling += 1

print(f"\nBOWLING ECONOMY:")
print(f"  Players with ACTUAL economy: {players_with_actual_bowling}/{len(db)} ({players_with_actual_bowling/len(db)*100:.1f}%)")
print(f"  Players with NULL/0 economy: {players_with_null_bowling}/{len(db)} ({players_with_null_bowling/len(db)*100:.1f}%)")
print(f"  Players with no bowling data: {players_no_bowling_data}/{len(db)} ({players_no_bowling_data/len(db)*100:.1f}%)")
print(f"  Note: Defaults (5.0/5.5/6.0) used at PREDICTION TIME for missing data")

# ==============================================================================
# VENUE ANALYSIS
# ==============================================================================

print("\n" + "-"*80)
print("VENUE AVERAGES ANALYSIS")
print("-"*80)

# Load dataset to check venue averages
dataset_path = os.path.join(script_dir, '../data/progressive_full_features_dataset.csv')
if os.path.exists(dataset_path):
    df = pd.read_csv(dataset_path)
    
    # Get unique venues
    venue_stats = df.groupby('venue').agg({
        'final_score': ['mean', 'count'],
        'venue_avg_score': 'first'
    }).reset_index()
    venue_stats.columns = ['venue', 'calculated_avg', 'match_count', 'stored_avg']
    
    # Calculate global average
    global_avg = float(df['final_score'].mean())
    
    venues_with_actual = 0
    venues_with_default = 0
    venues_with_few_matches = 0
    
    for _, row in venue_stats.iterrows():
        match_count = int(row['match_count'])
        calculated = float(row['calculated_avg'])
        stored = float(row['stored_avg'])
        
        if match_count >= 10:
            venues_with_actual += 1
        else:
            venues_with_few_matches += 1
            # Venues with <10 matches use global average (not hardcoded 250)
            if abs(calculated - global_avg) < 1.0:
                venues_with_default += 1
    
    print(f"\nVENUE AVERAGES:")
    print(f"  Total unique venues in dataset: {len(venue_stats)}")
    print(f"  Venues with 10+ matches (use actual avg): {venues_with_actual} ({venues_with_actual/len(venue_stats)*100:.1f}%)")
    print(f"  Venues with <10 matches (use global avg): {venues_with_few_matches} ({venues_with_few_matches/len(venue_stats)*100:.1f}%)")
    print(f"  Global average (calculated from data): {global_avg:.1f}")
    print(f"  Old hardcoded default: 250.0")
    print(f"  Difference: {abs(global_avg - 250.0):.1f} runs")
    
    # Show sample venues
    print(f"\n  Sample venues (first 10):")
    for i, row in venue_stats.head(10).iterrows():
        match_count = int(row['match_count'])
        avg = float(row['calculated_avg'])
        status = "ACTUAL" if match_count >= 10 else f"GLOBAL ({global_avg:.1f})"
        print(f"    {row['venue'][:40]:40s} | {match_count:3d} matches | {avg:6.1f} avg | {status}")
    
else:
    print("  Dataset file not found - cannot analyze venues")

# ==============================================================================
# SUMMARY
# ==============================================================================

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"\nPLAYERS:")
print(f"  Batting averages: {players_with_actual_batting}/{len(db)} actual ({players_with_actual_batting/len(db)*100:.1f}%)")
print(f"  Bowling economy: {players_with_actual_bowling}/{len(db)} actual ({players_with_actual_bowling/len(db)*100:.1f}%)")
print(f"  Defaults used at prediction time when data missing")

print(f"\nVENUES:")
if os.path.exists(dataset_path):
    print(f"  Actual averages (10+ matches): {venues_with_actual}/{len(venue_stats)} ({venues_with_actual/len(venue_stats)*100:.1f}%)")
    print(f"  Use global avg (<10 matches): {venues_with_few_matches}/{len(venue_stats)} ({venues_with_few_matches/len(venue_stats)*100:.1f}%)")
    print(f"  Global avg calculated from data: {global_avg:.1f} (not hardcoded 250)")

print("\n" + "="*80)

