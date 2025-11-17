#!/usr/bin/env python3
"""
FIX PLAYER DATABASE - Create Unified Database for Frontend & Backend

This script:
1. Expands abbreviated player names to full names
2. Converts star_rating to 1-5 scale (5 = elite like Kohli, 3 = average like Nawaz)
3. Extracts country from teams array
4. Keeps all existing stats (uses actual averages when available)
5. Only adds defaults when truly missing: Batter=30, Bowler=18, All-rounder=25
6. Creates unified database for both frontend and backend
"""

import json
import os
from collections import defaultdict

# Name expansion mapping (common cricket abbreviations to full names)
NAME_EXPANSIONS = {
    "V Kohli": "Virat Kohli",
    "RG Sharma": "Rohit Sharma",
    "MS Dhoni": "MS Dhoni",  # Already full
    "SR Tendulkar": "Sachin Tendulkar",
    "V Sehwag": "Virender Sehwag",
    "CH Gayle": "Chris Gayle",
    "MJ Guptill": "Martin Guptill",
    "SR Watson": "Shane Watson",
    "AK Markram": "Aiden Markram",
    "Q de Kock": "Quinton de Kock",
    "TM Head": "Travis Head",
    "JC Buttler": "Jos Buttler",
    "MR Marsh": "Mitchell Marsh",
    "BA Stokes": "Ben Stokes",
    "TM Dilshan": "Tillakaratne Dilshan",
    "AB de Villiers": "AB de Villiers",
    "SPD Smith": "Steven Smith",
    "KS Williamson": "Kane Williamson",
    "JE Root": "Joe Root",
    "DA Warner": "David Warner",
    "Babar Azam": "Babar Azam",
    "P Kumar": "Praveen Kumar",
    # Add more as needed
}

# Known countries for extraction
KNOWN_COUNTRIES = [
    'India', 'Australia', 'England', 'Pakistan', 'South Africa', 
    'New Zealand', 'Sri Lanka', 'Bangladesh', 'West Indies', 
    'Afghanistan', 'Ireland', 'Zimbabwe', 'Scotland', 'Netherlands',
    'United Arab Emirates', 'Oman', 'Nepal', 'Hong Kong'
]

def extract_country(teams_array):
    """Extract country from teams array"""
    if not teams_array:
        return 'Unknown'
    
    for team in teams_array:
        if team in KNOWN_COUNTRIES:
            return team
    
    # If no known country found, return first team
    return teams_array[0] if teams_array else 'Unknown'

def calculate_star_rating_1_to_5(player_data):
    """
    Calculate 1-5 star rating based on performance
    5 stars = Elite (Kohli level)
    4 stars = Very Good
    3 stars = Average (Nawaz level)
    2 stars = Below Average
    1 star = Poor
    """
    batting = player_data.get('batting', {})
    bowling = player_data.get('bowling')
    
    batting_avg = batting.get('average', 0) if batting else 0
    bowling_wickets = bowling.get('total_wickets', 0) if bowling else 0
    bowling_economy = bowling.get('economy', 999) if bowling else 999
    total_matches = player_data.get('total_matches', 0)
    
    # Calculate rating based on primary skill
    role = player_data.get('role', 'Batsman')
    
    if 'Bowler' in role or (bowling_wickets > 50 and batting_avg < 25):
        # Rate as bowler
        if bowling_economy < 4.5 and bowling_wickets > 100:
            return 5  # Elite bowler
        elif bowling_economy < 5.0 and bowling_wickets > 50:
            return 4  # Very good bowler
        elif bowling_economy < 5.5 and bowling_wickets > 20:
            return 3  # Average bowler
        elif bowling_economy < 6.0:
            return 2  # Below average
        else:
            return 1  # Poor
    
    elif 'All-rounder' in role or (bowling_wickets > 20 and batting_avg >= 25):
        # Rate as all-rounder
        combined_score = (batting_avg * 0.6) + ((50 - bowling_economy) * 2) + (bowling_wickets * 0.1)
        if combined_score > 50:
            return 5
        elif combined_score > 40:
            return 4
        elif combined_score > 30:
            return 3
        elif combined_score > 20:
            return 2
        else:
            return 1
    
    else:
        # Rate as batsman
        if batting_avg >= 45 and total_matches > 50:
            return 5  # Elite (Kohli level)
        elif batting_avg >= 40 and total_matches > 30:
            return 4  # Very good
        elif batting_avg >= 30 and total_matches > 20:
            return 3  # Average (Nawaz level)
        elif batting_avg >= 20:
            return 2  # Below average
        else:
            return 1  # Poor

def expand_player_name(abbreviated_name, player_data):
    """Expand abbreviated name to full name"""
    # Check if already in mapping
    if abbreviated_name in NAME_EXPANSIONS:
        return NAME_EXPANSIONS[abbreviated_name]
    
    # Check if name field has full name
    name_field = player_data.get('name', abbreviated_name)
    if len(name_field.split()) > 1 and len(name_field) > len(abbreviated_name):
        return name_field
    
    # If name looks like it might be full (has space and reasonable length), use it
    if ' ' in abbreviated_name and len(abbreviated_name) > 5:
        return abbreviated_name
    
    # Otherwise keep as is (will need manual fixing later)
    return abbreviated_name

def get_role_based_default(role):
    """Get default average based on role (only when truly missing)"""
    if 'Bowler' in role:
        return 18.0
    elif 'All-rounder' in role:
        return 25.0
    else:  # Batsman
        return 30.0

def fix_player_database(input_file, output_file):
    """Fix player database with full names, 1-5 star ratings, and proper defaults"""
    
    print(f"\n{'='*80}")
    print("FIXING PLAYER DATABASE")
    print(f"{'='*80}")
    
    print(f"\n[1/5] Loading player database from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        player_db = json.load(f)
    
    print(f"   Loaded {len(player_db)} players")
    
    print(f"\n[2/5] Fixing names and extracting countries...")
    fixed_db = {}
    name_fixes = 0
    countries_added = 0
    
    for old_key, player_data in player_db.items():
        # Expand name
        full_name = expand_player_name(old_key, player_data)
        if full_name != old_key:
            name_fixes += 1
        
        # Extract country
        teams = player_data.get('teams', [])
        country = extract_country(teams)
        if country != 'Unknown':
            countries_added += 1
        
        # Create fixed player entry
        fixed_player = player_data.copy()
        fixed_player['name'] = full_name
        fixed_player['country'] = country
        
        # Use full name as new key
        fixed_db[full_name] = fixed_player
    
    print(f"   Fixed {name_fixes} names")
    print(f"   Extracted {countries_added} countries")
    
    print(f"\n[3/5] Calculating 1-5 star ratings...")
    star_ratings = defaultdict(int)
    
    for player_name, player_data in fixed_db.items():
        old_rating = player_data.get('star_rating', 0)
        new_rating = calculate_star_rating_1_to_5(player_data)
        player_data['star_rating'] = new_rating
        star_ratings[new_rating] += 1
    
    print(f"   Star rating distribution:")
    for rating in sorted(star_ratings.keys(), reverse=True):
        print(f"     {rating} stars: {star_ratings[rating]} players")
    
    print(f"\n[4/5] Checking for missing averages (will use defaults only when truly missing)...")
    missing_batting = 0
    missing_bowling = 0
    
    for player_name, player_data in fixed_db.items():
        # Check batting average
        batting = player_data.get('batting')
        if not batting or not batting.get('average') or batting.get('average', 0) == 0:
            role = player_data.get('role', 'Batsman')
            default_avg = get_role_based_default(role)
            if 'batting' not in player_data:
                player_data['batting'] = {}
            player_data['batting']['average'] = default_avg
            missing_batting += 1
        
        # Check bowling economy (only if player has bowling role or stats)
        bowling = player_data.get('bowling')
        role = player_data.get('role', 'Batsman')
        if ('Bowler' in role or 'All-rounder' in role) and (not bowling or not bowling.get('economy') or bowling.get('economy', 0) == 0):
            if 'bowling' not in player_data:
                player_data['bowling'] = {}
            # Default economy based on role
            if 'Bowler' in role:
                player_data['bowling']['economy'] = 5.0
            else:
                player_data['bowling']['economy'] = 5.5
            missing_bowling += 1
    
    print(f"   Added default batting averages for {missing_batting} players")
    print(f"   Added default bowling economy for {missing_bowling} players")
    
    print(f"\n[5/5] Saving fixed database to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_db, f, indent=2, ensure_ascii=False)
    
    print(f"   Saved {len(fixed_db)} players")
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total players: {len(fixed_db)}")
    print(f"Names fixed: {name_fixes}")
    print(f"Countries extracted: {countries_added}")
    print(f"Star ratings: 1-5 scale (5 = elite, 3 = average)")
    print(f"Missing averages filled: {missing_batting} batting, {missing_bowling} bowling")
    print(f"\n[OK] Fixed database saved to: {output_file}")
    print(f"{'='*80}\n")
    
    return fixed_db

if __name__ == '__main__':
    input_file = '../../ODI_Progressive/CURRENT_player_database_977_quality.json'
    output_file = '../../ODI_Progressive/CURRENT_player_database_977_quality_FIXED.json'
    
    fix_player_database(input_file, output_file)
    print("\n[OK] Player database fixed successfully!")
    print("\nNext steps:")
    print("1. Review the fixed database")
    print("2. Update config.py to use the new database")
    print("3. Update prediction code to use role-based defaults")

