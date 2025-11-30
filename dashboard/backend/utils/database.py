import sqlite3
import os

class Database:
    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), '../../../ODI_Progressive/cricket_prediction_odi.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        print(f"[OK] Connected to database: {db_path}")
    
    def get_all_teams(self):
        """Get all teams from database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT team_id, team_name, team_type FROM teams ORDER BY team_name")
        teams = []
        for row in cursor.fetchall():
            teams.append({
                'team_id': row['team_id'],
                'team_name': row['team_name'],
                'team_type': row['team_type']
            })
        return teams
    
    def get_all_players(self):
        """Get all players from database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT player_id, player_name, role, teams, 
                   batting_avg, bowling_avg, total_matches, star_rating
            FROM players 
            ORDER BY batting_avg DESC
        """)
        players = []
        for row in cursor.fetchall():
            # Parse teams to get country
            teams_str = row['teams'] or ''
            country = 'Unknown'
            if teams_str:
                # Extract country from teams string (e.g., "India, Mumbai Indians" -> "India")
                countries = [team.strip() for team in teams_str.split(',')]
                # Find a known country
                known_countries = ['India', 'Australia', 'England', 'Pakistan', 'South Africa', 'New Zealand', 'Sri Lanka', 'Bangladesh', 'West Indies', 'Afghanistan', 'Ireland', 'Zimbabwe']
                for c in countries:
                    if c in known_countries:
                        country = c
                        break
                else:
                    country = countries[0] if countries else 'Unknown'
            
            batting_avg = row['batting_avg'] or 0
            bowling_avg = row['bowling_avg'] or 0
            
            # Smart role classification based on stats
            calculated_role = self._classify_role(
                batting_avg, 
                bowling_avg, 
                row['role']
            )
            
            # For display purposes, estimate economy from bowling average
            # Rough estimate: economy ≈ bowling_avg / 5 (since avg = runs/wickets, economy = runs/overs)
            # But we'll use bowling_avg directly for role classification
            bowling_economy = bowling_avg / 5.0 if bowling_avg > 0 else 0
            
            players.append({
                'player_id': row['player_id'],
                'player_name': row['player_name'],
                'player_role': calculated_role,
                'country': country,
                'batting_avg': batting_avg,
                'bowling_economy': bowling_economy,  # Estimated for display
                'total_matches': row['total_matches'] or 0,
                'tier': 'regular',
                'has_impact': False,
                'batting_impact': 0,
                'bowling_impact': 0
            })
        return players
    
    def _classify_role(self, batting_avg, bowling_avg, db_role):
        """
        Classify player role based on actual stats instead of database label.
        
        NOTE: bowling_avg is BOWLING AVERAGE (runs per wicket), not economy rate!
        - Lower bowling average = better bowler (good bowlers have avg < 35)
        - Higher batting average = better batsman (good batsmen have avg > 30)
        
        Rules:
        - BATSMAN: Good batting (avg >= 30), minimal/no bowling (bowling_avg == 0 or > 50)
        - BOWLER: Good bowling (bowling_avg > 0 and < 35), weak batting (bat_avg < 20)
        - ALL-ROUNDER: Can both bat (avg >= 20) and bowl (bowling_avg > 0 and < 40)
        - Fallback to database role if stats are insufficient
        """
        # If no stats available, use database role
        if batting_avg == 0 and bowling_avg == 0:
            return db_role or 'All-rounder'
        
        # BATSMAN: Good batting, minimal/no bowling
        # Bowling avg > 50 means they rarely bowl or bowl poorly
        if batting_avg >= 30 and (bowling_avg == 0 or bowling_avg > 50):
            return 'Batsman'
        
        # BOWLER: Good bowling, weak batting
        # Bowling avg < 35 is good (takes wickets cheaply)
        if bowling_avg > 0 and bowling_avg < 35 and batting_avg < 20:
            return 'Bowler'
        
        # ALL-ROUNDER: Can both bat and bowl
        # Batting avg >= 20 (decent bat) and bowling avg < 40 (can bowl)
        if batting_avg >= 20 and bowling_avg > 0 and bowling_avg < 40:
            return 'All-rounder'
        
        # Edge cases: Only batting stats available
        if batting_avg >= 25 and bowling_avg == 0:
            return 'Batsman'
        
        # Edge cases: Only bowling stats available
        # Good bowler with very weak batting
        if batting_avg < 15 and bowling_avg > 0 and bowling_avg < 35:
            return 'Bowler'
        
        # Fallback to database role or default
        return db_role if db_role else 'All-rounder'
    
    def get_all_venues(self):
        """Get all venues from database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT venue_id, venue_name, city FROM venues ORDER BY venue_name")
        venues = []
        for row in cursor.fetchall():
            venues.append({
                'venue_id': row['venue_id'],
                'venue_name': row['venue_name'],
                'city': row['city']
            })
        return venues
    
    def close(self):
        """Close database connection"""
        self.conn.close()

# Global database instance
_db = None

def get_database():
    """Get or create database singleton"""
    global _db
    if _db is None:
        _db = Database()
    return _db

