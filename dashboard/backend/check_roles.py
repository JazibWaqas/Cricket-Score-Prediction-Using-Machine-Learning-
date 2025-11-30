import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

db_path = '../../ODI_Progressive/cricket_prediction_odi.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def classify_role(batting_avg, bowling_avg, db_role):
    """Use the NEW bowling average-based classification"""
    if batting_avg == 0 and bowling_avg == 0:
        return db_role or 'All-rounder'
    
    # BATSMAN: Good batting, minimal/no bowling
    if batting_avg >= 30 and (bowling_avg == 0 or bowling_avg > 50):
        return 'Batsman'
    
    # BOWLER: Good bowling, weak batting
    if bowling_avg > 0 and bowling_avg < 35 and batting_avg < 20:
        return 'Bowler'
    
    # ALL-ROUNDER: Can both bat and bowl
    if batting_avg >= 20 and bowling_avg > 0 and bowling_avg < 40:
        return 'All-rounder'
    
    # Edge cases
    if batting_avg >= 25 and bowling_avg == 0:
        return 'Batsman'
    
    if batting_avg < 15 and bowling_avg > 0 and bowling_avg < 35:
        return 'Bowler'
    
    return db_role if db_role else 'All-rounder'

# Check Virat Kohli
cursor.execute("SELECT player_name, batting_avg, bowling_avg, role FROM players WHERE player_name LIKE '%Kohli%'")
print("=== VIRAT KOHLI ===")
for row in cursor.fetchall():
    batting_avg = row[1] or 0
    bowling_avg = row[2] or 0
    print(f"Name: {row[0]}")
    print(f"Batting Avg: {batting_avg}")
    print(f"Bowling Avg: {bowling_avg} (lower is better for bowlers)")
    print(f"DB Role: {row[3]}")
    
    calculated_role = classify_role(batting_avg, bowling_avg, row[3])
    print(f"✅ Calculated Role: {calculated_role}")
    print(f"   Reason: Bat avg {batting_avg} >= 30 AND Bowl avg {bowling_avg} > 50 → Batsman")
    print()

# Check Jasprit Bumrah
cursor.execute("SELECT player_name, batting_avg, bowling_avg, role FROM players WHERE player_name LIKE '%Bumrah%'")
print("=== JASPRIT BUMRAH ===")
for row in cursor.fetchall():
    batting_avg = row[1] or 0
    bowling_avg = row[2] or 0
    print(f"Name: {row[0]}")
    print(f"Batting Avg: {batting_avg}")
    print(f"Bowling Avg: {bowling_avg} (lower is better for bowlers)")
    print(f"DB Role: {row[3]}")
    
    calculated_role = classify_role(batting_avg, bowling_avg, row[3])
    print(f"✅ Calculated Role: {calculated_role}")
    print(f"   Reason: Bowl avg {bowling_avg} < 35 AND Bat avg {batting_avg} < 20 → Bowler")
    print()

# Check Hardik Pandya
cursor.execute("SELECT player_name, batting_avg, bowling_avg, role FROM players WHERE player_name LIKE '%Pandya%'")
print("=== HARDIK PANDYA ===")
for row in cursor.fetchall():
    batting_avg = row[1] or 0
    bowling_avg = row[2] or 0
    print(f"Name: {row[0]}")
    print(f"Batting Avg: {batting_avg}")
    print(f"Bowling Avg: {bowling_avg}")
    print(f"DB Role: {row[3]}")
    
    calculated_role = classify_role(batting_avg, bowling_avg, row[3])
    print(f"✅ Calculated Role: {calculated_role}")
    print(f"   Reason: Bat avg {batting_avg} >= 20 AND Bowl avg {bowling_avg} < 40 → All-rounder")
    print()

conn.close()
