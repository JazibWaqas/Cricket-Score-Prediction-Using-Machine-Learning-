import sys
sys.path.insert(0, '.')

from utils.database import Database

db = Database()
players = db.get_all_players()

# Find Kohli
kohli = [p for p in players if 'Kohli' in p['player_name']]
if kohli:
    print(f"Kohli role: {kohli[0]['player_role']}")
    print(f"Kohli batting avg: {kohli[0]['batting_avg']}")
    print(f"Kohli bowling economy: {kohli[0]['bowling_economy']}")

# Find Bumrah
bumrah = [p for p in players if 'Bumrah' in p['player_name']]
if bumrah:
    print(f"\nBumrah role: {bumrah[0]['player_role']}")
    print(f"Bumrah batting avg: {bumrah[0]['batting_avg']}")
    print(f"Bumrah bowling economy: {bumrah[0]['bowling_economy']}")

# Find Pandya
pandya = [p for p in players if 'Pandya' in p['player_name'] and 'Hardik' in p['player_name']]
if pandya:
    print(f"\nHardik Pandya role: {pandya[0]['player_role']}")
    print(f"Pandya batting avg: {pandya[0]['batting_avg']}")
    print(f"Pandya bowling economy: {pandya[0]['bowling_economy']}")
