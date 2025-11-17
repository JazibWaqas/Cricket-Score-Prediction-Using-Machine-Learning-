import pickle
import json
import os
from config import Config

class ModelLoader:
    def __init__(self):
        self.models = {}  # Dictionary to store all models
        self.model = None  # Default model (XGBoost for backward compatibility)
        self.player_db = None
        self.venues = {}
        self.load_all_models()
        self.load_player_database()
        self.load_venues()
    
    def load_all_models(self):
        """Load all available models (XGBoost, RandomForest, LinearRegression)"""
        model_files = {
            'XGBoost': Config.MODEL_PATH,  # Original XGBoost model
            'RandomForest': os.path.join(os.path.dirname(Config.MODEL_PATH), 'progressive_model_randomforest.pkl'),
            'LinearRegression': os.path.join(os.path.dirname(Config.MODEL_PATH), 'progressive_model_linearregression.pkl')
        }
        
        # Also try the new XGBoost model
        new_xgb_path = os.path.join(os.path.dirname(Config.MODEL_PATH), 'progressive_model_xgboost.pkl')
        if os.path.exists(new_xgb_path):
            model_files['XGBoost'] = new_xgb_path
        
        for model_name, model_path in model_files.items():
            try:
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    print(f"[OK] {model_name} model loaded from {model_path}")
                else:
                    print(f"[WARNING] {model_name} model not found at {model_path}")
            except Exception as e:
                print(f"[ERROR] Error loading {model_name} model: {e}")
        
        # Set default model (prefer XGBoost, fallback to first available)
        if 'XGBoost' in self.models:
            self.model = self.models['XGBoost']
        elif len(self.models) > 0:
            self.model = list(self.models.values())[0]
            print(f"[INFO] Using {list(self.models.keys())[0]} as default model")
        else:
            raise Exception("No models loaded!")
    
    def get_model(self, model_name='XGBoost'):
        """Get a specific model by name"""
        return self.models.get(model_name, self.model)  # Fallback to default if not found
    
    def load_player_database(self):
        """Load player database with batting/bowling stats"""
        try:
            with open(Config.PLAYER_DB_PATH, 'r') as f:
                self.player_db = json.load(f)
            print(f"[OK] Player database loaded: {len(self.player_db)} players")
        except Exception as e:
            print(f"[ERROR] Error loading player database: {e}")
            raise
    
    def load_venues(self):
        """Load venue averages calculated from actual match data"""
        try:
            import pandas as pd
            # Use full dataset to get better venue averages
            dataset_path = os.path.join(os.path.dirname(__file__), '../../../ODI_Progressive/data/progressive_full_features_dataset.csv')
            if os.path.exists(dataset_path):
                df = pd.read_csv(dataset_path)
            else:
                # Fallback to test data
                df = pd.read_csv(Config.TEST_DATA_PATH)
            
            # Calculate actual venue averages from final_score (real match data)
            venue_data = df.groupby('venue').agg({
                'final_score': ['mean', 'count']  # Calculate mean and count
            }).reset_index()
            venue_data.columns = ['venue', 'avg_score', 'match_count']
            
            # Only use venues with 10+ matches for reliability
            venue_data = venue_data[venue_data['match_count'] >= 10]
            
            # Calculate global average for fallback
            global_avg = float(df['final_score'].mean()) if len(df) > 0 else 250.0
            
            self.venues = {}
            for _, row in venue_data.iterrows():
                self.venues[row['venue']] = {
                    'avg_score': float(row['avg_score']),  # Actual calculated average
                    'actual_avg': float(row['avg_score']),  # Same (calculated from data)
                    'match_count': int(row['match_count'])
                }
            
            # Store global average for venues not in database
            self.global_venue_avg = global_avg
            
            print(f"[OK] Loaded {len(self.venues)} venues (calculated from match data)")
            print(f"   Global average: {global_avg:.1f} (used for venues with <10 matches)")
        except Exception as e:
            print(f"[WARNING] Could not load venues: {e}")
            self.venues = {}
            self.global_venue_avg = 250.0
    
    def get_teams(self):
        """Get list of international teams"""
        teams = [
            'India', 'Australia', 'England', 'Pakistan', 'South Africa',
            'New Zealand', 'West Indies', 'Sri Lanka', 'Bangladesh',
            'Afghanistan', 'Zimbabwe', 'Ireland', 'Scotland', 'Netherlands'
        ]
        return sorted(teams)
    
    def get_players_for_team(self, team):
        """Get players for a specific team from player database"""
        players = []
        for player_name, player_data in self.player_db.items():
            # Simple heuristic: if player has stats, include them
            if 'batting' in player_data or 'bowling' in player_data:
                players.append({
                    'name': player_name,
                    'batting_avg': player_data.get('batting', {}).get('average', 0),
                    'strike_rate': player_data.get('batting', {}).get('strike_rate', 0),
                    'bowling_economy': player_data.get('bowling', {}).get('economy', 0)
                })
        
        # Sort by batting average
        players.sort(key=lambda x: x['batting_avg'], reverse=True)
        return players[:100]  # Return top 100
    
    def get_venues(self):
        """Get list of venues"""
        return [
            {
                'name': venue,
                'avg_score': data['avg_score'],
                'actual_avg': data['actual_avg']
            }
            for venue, data in self.venues.items()
        ]

# Global model loader instance
_model_loader = None

def get_model_loader():
    """Get or create model loader singleton"""
    global _model_loader
    if _model_loader is None:
        _model_loader = ModelLoader()
    return _model_loader

