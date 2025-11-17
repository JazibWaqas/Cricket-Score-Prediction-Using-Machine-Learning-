#!/usr/bin/env python3
"""Analyze the fixed player database"""

import json
import os

db_path = '../CURRENT_player_database_977_quality_FIXED.json'

print("\n" + "="*80)
print("FIXED DATABASE ANALYSIS")
print("="*80)

with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

print(f"\nTotal players: {len(db)}")

# Check structure
sample_player = list(db.values())[0]
print(f"\nDatabase structure:")
print(f"  Fields: {list(sample_player.keys())}")

# Check name fixes
print(f"\nSample players (first 10):")
for i, name in enumerate(list(db.keys())[:10]):
    print(f"  {i+1}. {name}")

# Check country field
has_country = sum(1 for p in db.values() if 'country' in p)
print(f"\nCountry field:")
print(f"  Players with country: {has_country}/{len(db)} ({has_country/len(db)*100:.1f}%)")

# Check star ratings
star_ratings = [p.get('star_rating', 0) for p in db.values()]
print(f"\nStar ratings (1-5 scale):")
print(f"  Min: {min(star_ratings)}")
print(f"  Max: {max(star_ratings)}")
print(f"  Distribution:")
for rating in range(1, 6):
    count = sum(1 for r in star_ratings if r == rating)
    print(f"    {rating} stars: {count} players ({count/len(db)*100:.1f}%)")

# Check batting averages
batting_avgs = []
for p in db.values():
    if 'batting' in p and p['batting'] and 'average' in p['batting']:
        avg = p['batting']['average']
        if avg > 0:
            batting_avgs.append(avg)

print(f"\nBatting averages:")
print(f"  Players with batting data: {len(batting_avgs)}/{len(db)}")
if batting_avgs:
    print(f"  Min: {min(batting_avgs):.2f}")
    print(f"  Max: {max(batting_avgs):.2f}")
    print(f"  Mean: {sum(batting_avgs)/len(batting_avgs):.2f}")

# Check bowling economy
bowling_econs = []
for p in db.values():
    if 'bowling' in p and p['bowling'] and 'economy' in p['bowling']:
        econ = p['bowling']['economy']
        if econ > 0:
            bowling_econs.append(econ)

print(f"\nBowling economy:")
print(f"  Players with bowling data: {len(bowling_econs)}/{len(db)}")
if bowling_econs:
    print(f"  Min: {min(bowling_econs):.2f}")
    print(f"  Max: {max(bowling_econs):.2f}")
    print(f"  Mean: {sum(bowling_econs)/len(bowling_econs):.2f}")

# Check roles
roles = {}
for p in db.values():
    role = p.get('role', 'Unknown')
    roles[role] = roles.get(role, 0) + 1

print(f"\nRole distribution:")
for role, count in sorted(roles.items(), key=lambda x: -x[1]):
    print(f"  {role}: {count} players ({count/len(db)*100:.1f}%)")

print("\n" + "="*80)

