#!/usr/bin/env python3
"""Test if role-based defaults are working correctly"""

import json
import sys
sys.path.append('../../dashboard/backend')
from utils.predictions import get_batsman_avg

# Load database
with open('../CURRENT_player_database_977_quality_FIXED.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print("\n" + "="*80)
print("TESTING ROLE-BASED DEFAULTS LOGIC")
print("="*80)

# Test 1: Player with actual average
print("\n[Test 1] Player with actual average:")
test_player = "Virat Kohli"
if test_player in db:
    actual_avg = db[test_player]['batting']['average']
    calculated_avg = get_batsman_avg(test_player, db)
    print(f"  Player: {test_player}")
    print(f"  Role: {db[test_player]['role']}")
    print(f"  Actual avg in DB: {actual_avg}")
    print(f"  Function returns: {calculated_avg}")
    print(f"  Result: {'✅ CORRECT' if calculated_avg == actual_avg else '❌ WRONG'}")

# Test 2: Player not in database (should use default)
print("\n[Test 2] Player NOT in database:")
test_player = "Unknown Player XYZ"
calculated_avg = get_batsman_avg(test_player, db)
print(f"  Player: {test_player}")
print(f"  Function returns: {calculated_avg}")
print(f"  Expected: 30.0 (Batsman default)")
print(f"  Result: {'✅ CORRECT' if calculated_avg == 30.0 else '❌ WRONG'}")

# Test 3: Find a player with low average to test role-based logic
print("\n[Test 3] Testing role-based defaults:")
# Find a bowler
for name, player in db.items():
    if 'Bowler' in player.get('role', ''):
        role = player['role']
        batting_avg = player.get('batting', {}).get('average', 0)
        calculated = get_batsman_avg(name, db)
        print(f"  Player: {name}")
        print(f"  Role: {role}")
        print(f"  Batting avg in DB: {batting_avg}")
        print(f"  Function returns: {calculated}")
        if batting_avg > 0:
            print(f"  Result: {'✅ Uses actual' if calculated == batting_avg else '❌ Should use actual'}")
        else:
            print(f"  Result: {'✅ Uses default (18.0)' if calculated == 18.0 else '❌ Should use 18.0'}")
        break

# Test 4: Simulate player with null average
print("\n[Test 4] Simulating player with null average:")
test_db = db.copy()
test_db["Test Bowler"] = {
    "role": "Bowler",
    "batting": {"average": None}
}
calculated = get_batsman_avg("Test Bowler", test_db)
print(f"  Player: Test Bowler")
print(f"  Role: Bowler")
print(f"  Batting avg in DB: None")
print(f"  Function returns: {calculated}")
print(f"  Expected: 18.0 (Bowler default)")
print(f"  Result: {'✅ CORRECT' if calculated == 18.0 else '❌ WRONG'}")

# Test 5: Simulate player with 0 average
test_db["Test All-rounder"] = {
    "role": "All-rounder",
    "batting": {"average": 0}
}
calculated = get_batsman_avg("Test All-rounder", test_db)
print(f"\n[Test 5] Simulating player with 0 average:")
print(f"  Player: Test All-rounder")
print(f"  Role: All-rounder")
print(f"  Batting avg in DB: 0")
print(f"  Function returns: {calculated}")
print(f"  Expected: 25.0 (All-rounder default)")
print(f"  Result: {'✅ CORRECT' if calculated == 25.0 else '❌ WRONG'}")

print("\n" + "="*80)

