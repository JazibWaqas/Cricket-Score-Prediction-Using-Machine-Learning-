#!/usr/bin/env python3
"""Check for players with missing averages"""

import json
import os

db_path = '../CURRENT_player_database_977_quality_FIXED.json'

with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

print("\n" + "="*80)
print("CHECKING FOR MISSING AVERAGES")
print("="*80)

# Check batting averages
missing_batting = []
for name, player in db.items():
    batting = player.get('batting')
    if not batting:
        missing_batting.append((name, player.get('role', 'Unknown'), 'No batting object'))
    elif batting.get('average') is None or batting.get('average', 0) == 0:
        missing_batting.append((name, player.get('role', 'Unknown'), f"avg={batting.get('average')}"))

print(f"\nPlayers with missing/null/0 batting averages: {len(missing_batting)}")
if missing_batting:
    print("\nFirst 10 examples:")
    for name, role, reason in missing_batting[:10]:
        print(f"  {name:30s} | Role: {role:20s} | Issue: {reason}")

# Check bowling economy
missing_bowling = []
for name, player in db.items():
    role = player.get('role', 'Batsman')
    bowling = player.get('bowling')
    if 'Bowler' in role or 'All-rounder' in role:
        if not bowling:
            missing_bowling.append((name, role, 'No bowling object'))
        elif bowling.get('economy') is None or bowling.get('economy', 0) == 0:
            missing_bowling.append((name, role, f"economy={bowling.get('economy')}"))

print(f"\nBowler/All-rounder players with missing/null/0 bowling economy: {len(missing_bowling)}")
if missing_bowling:
    print("\nFirst 10 examples:")
    for name, role, reason in missing_bowling[:10]:
        print(f"  {name:30s} | Role: {role:20s} | Issue: {reason}")

print("\n" + "="*80)

