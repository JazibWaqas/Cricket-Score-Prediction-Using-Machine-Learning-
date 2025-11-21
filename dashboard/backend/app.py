from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
from config import Config
from utils.model_loader import get_model_loader
from utils.database import get_database
from utils.predictions import (
    calculate_team_aggregates,
    calculate_bowling_aggregates,
    get_batsman_avg,
    make_prediction,
    calculate_confidence_interval,
    get_match_stage
)

app = Flask(__name__, static_folder='../../dashboard/frontend/build', static_url_path='')
CORS(app, origins=Config.CORS_ORIGINS)

# Load model and database on startup
model_loader = get_model_loader()
db = get_database()


def resolve_model_identifier(identifier):
    """Map a canonical identifier (e.g. 'xgboost' or 'random_forest') to the
    model key used by the ModelLoader (e.g. 'XGBoost' or 'Random Forest').
    """
    if not identifier:
        return identifier
        
    # Normalize input: lowercase, remove all non-alphanumeric chars
    import re
    lookup = re.sub(r'[^a-z0-9]', '', identifier.lower())
    
    # Check against available keys
    for key in model_loader.models.keys():
        # Normalize key similarly
        key_normalized = re.sub(r'[^a-z0-9]', '', key.lower())
        
        if key_normalized == lookup:
            return key
            
    return identifier

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loader.model is not None,
        'players_loaded': model_loader.player_db is not None,
        'available_models': list(model_loader.models.keys())
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get list of available models"""
    # Return models as {label, value} pairs where `value` is a canonical identifier
    models_raw = list(model_loader.models.keys())
    models = []
    for m in models_raw:
        # Friendly label: if camel/caps like 'RandomForest', convert to 'Random Forest'
        label = ''.join([c if c.isupper() and i != 0 and not m[i-1].isupper() else c for i, c in enumerate(m)]).replace('_', ' ')
        # make label nicer (insert space before capitals) more robustly
        import re
        label = re.sub(r'(?<!^)(?=[A-Z])', ' ', m).replace('_', ' ')
        value = m.lower().replace(' ', '_')
        models.append({'label': label, 'value': value})

    default_value = None
    if 'XGBoost' in model_loader.models:
        default_value = 'xgboost'
    elif models:
        default_value = models[0]['value']

    return jsonify({
        'models': models,
        'default': default_value
    })

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get all teams from database"""
    try:
        teams = db.get_all_teams()
        return jsonify({
            'teams': teams,
            'count': len(teams)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players', methods=['GET'])
def get_all_players():
    """Get all players from FIXED JSON database"""
    try:
        # Use FIXED JSON database instead of SQLite for consistency
        players = []
        for player_name, player_data in model_loader.player_db.items():
            if player_data is None:
                continue
            
            batting = player_data.get('batting') or {}
            bowling = player_data.get('bowling') or {}
            
            players.append({
                'player_id': player_name,  # Use name as ID
                'player_name': player_data.get('name', player_name),
                'player_role': player_data.get('role', 'All-rounder'),
                'country': player_data.get('country', 'Unknown'),
                'batting_avg': batting.get('average', 0) if batting else 0,
                'bowling_economy': bowling.get('economy', 0) if bowling else 0,
                'total_matches': player_data.get('total_matches', 0),
                'star_rating': player_data.get('star_rating', 3),
                'tier': 'regular',
                'has_impact': False,
                'batting_impact': 0,
                'bowling_impact': 0
            })
        
        # Sort by batting average descending
        players.sort(key=lambda x: x['batting_avg'], reverse=True)
        
        return jsonify({
            'players': players,
            'count': len(players)
        })
    except Exception as e:
        import traceback
        print(f"ERROR in /api/players: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/venues', methods=['GET'])
def get_venues():
    """Get all venues from database"""
    try:
        venues = db.get_all_venues()
        # Add venue averages from our dataset
        venue_avgs = model_loader.venues if hasattr(model_loader, 'venues') and model_loader.venues else {}
        
        global_avg = getattr(model_loader, 'global_venue_avg', 250.0)
        for venue in venues:
            if venue['venue_name'] in venue_avgs:
                venue['avg_score'] = venue_avgs[venue['venue_name']]['avg_score']
            else:
                venue['avg_score'] = global_avg  # Use calculated global average, not hardcoded 250
        
        return jsonify({
            'venues': venues,
            'count': len(venues)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Make a prediction
    
    Expected input:
    {
        "batting_team_players": [list of 11 player names],
        "bowling_team_players": [list of 11 player names],
        "venue": "venue name",
        "venue_avg_score": 270.0,
        "current_score": 180,
        "wickets_fallen": 3,
        "balls_bowled": 180,
        "runs_last_10_overs": 65,
        "batsman_1": "V Kohli" (optional, for mid-match),
        "batsman_2": "H Pandya" (optional, for mid-match)
    }
    """
    try:
        data = request.json
        
        # Log request for debugging
        print(f"\n=== PREDICT REQUEST ===")
        print(f"Content-Type: {request.content_type}")
        print(f"Data received: {data}")
        print(f"Data type: {type(data)}")
        
        # Validate that we received JSON data
        if data is None:
            print("ERROR: No JSON data received")
            return jsonify({'error': 'No JSON data received. Make sure Content-Type is application/json'}), 400
        
        # Validate required fields
        required_fields = ['batting_team_players', 'bowling_team_players', 'current_score', 
                          'wickets_fallen', 'balls_bowled', 'runs_last_10_overs', 'venue_avg_score']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"ERROR: Missing fields: {missing_fields}")
            print(f"Received fields: {list(data.keys())}")
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Calculate team aggregates
        try:
            batting_agg = calculate_team_aggregates(
                data['batting_team_players'],
                model_loader.player_db
            )
            print(f"Batting aggregates: {batting_agg}")
            
            bowling_agg = calculate_bowling_aggregates(
                data['bowling_team_players'],
                model_loader.player_db
            )
            print(f"Bowling aggregates: {bowling_agg}")
            
            # Validate aggregates
            if batting_agg is None or bowling_agg is None:
                raise ValueError("Team aggregates calculation failed")
                
        except Exception as e:
            print(f"ERROR in team aggregates calculation: {e}")
            return jsonify({'error': f'Team calculation error: {str(e)}'}), 500
        
        # Get model to use (default to XGBoost)
        model_identifier = data.get('model', 'xgboost')
        model_name = resolve_model_identifier(model_identifier)
        model = model_loader.get_model(model_name)
        if model is None:
            return jsonify({'error': f'Model "{model_identifier}" not available. Available: {list(model_loader.models.keys())}'}), 400
        
        # Get current batsmen averages (if provided)
        batsman_1_avg = 0
        batsman_2_avg = 0
        if 'batsman_1' in data and data['batsman_1']:
            batsman_1_avg = get_batsman_avg(data['batsman_1'], model_loader.player_db)
        if 'batsman_2' in data and data['batsman_2']:
            batsman_2_avg = get_batsman_avg(data['batsman_2'], model_loader.player_db)
        
        # Calculate derived features
        balls_remaining = 300 - data['balls_bowled']
        current_run_rate = (data['current_score'] * 6.0 / data['balls_bowled']) if data['balls_bowled'] > 0 else 0
        
        # Build scenario
        try:
            scenario = {
                'current_score': data['current_score'],
                'wickets_fallen': data['wickets_fallen'],
                'balls_bowled': data['balls_bowled'],
                'balls_remaining': balls_remaining,
                'runs_last_10_overs': data['runs_last_10_overs'],
                'current_run_rate': current_run_rate,
                'team_batting_avg': batting_agg['team_batting_avg'],
                'team_elite_batsmen': batting_agg['team_elite_batsmen'],
                'team_batting_depth': batting_agg['team_batting_depth'],
                'opp_bowling_economy': bowling_agg['opp_bowling_economy'],
                'opp_elite_bowlers': bowling_agg['opp_elite_bowlers'],
                'opp_bowling_depth': bowling_agg['opp_bowling_depth'],
                'venue_avg_score': data['venue_avg_score'],
                'batsman_1_avg': batsman_1_avg,
                'batsman_2_avg': batsman_2_avg,
                'venue': data['venue']
            }
            print(f"Scenario built successfully: {list(scenario.keys())}")
        except Exception as e:
            print(f"ERROR building scenario: {e}")
            print(f"Batting agg keys: {list(batting_agg.keys()) if batting_agg else 'None'}")
            print(f"Bowling agg keys: {list(bowling_agg.keys()) if bowling_agg else 'None'}")
            return jsonify({'error': f'Scenario building error: {str(e)}'}), 500
        
        # Make prediction
        predicted_score = make_prediction(model, scenario)
        
        # Calculate confidence
        stage = get_match_stage(data['balls_bowled'])
        mae, r2, confidence_label = calculate_confidence_interval(None, stage)
        
        return jsonify({
            'predicted_score': round(predicted_score, 1),
            'confidence': {
                'mae': mae,
                'r2': r2,
                'label': confidence_label,
                'stage': stage
            },
            'team_stats': {
                'batting': batting_agg,
                'bowling': bowling_agg
            }
        })
        
    except KeyError as e:
        return jsonify({'error': f'Missing or invalid field: {str(e)}'}), 400
    except Exception as e:
        import traceback
        print(f"\n=== PREDICTION ERROR ===")
        print(f"Error: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()
        print(f"Request data: {request.json}")
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500

@app.route('/api/whatif', methods=['POST'])
def whatif():
    """
    Compare two scenarios (what-if analysis)
    
    Expected input:
    {
        "base_scenario": {...},  # Same as /predict
        "new_batsman": "MS Dhoni"  # Player to swap in
    }
    """
    try:
        data = request.json
        base_data = data['base_scenario']
        new_batsman = data.get('new_batsman')
        
        # Get base prediction
        batting_agg = calculate_team_aggregates(
            base_data['batting_team_players'],
            model_loader.player_db
        )
        
        bowling_agg = calculate_bowling_aggregates(
            base_data['bowling_team_players'],
            model_loader.player_db
        )
        
        # Base scenario
        batsman_1_avg = get_batsman_avg(base_data.get('batsman_1', ''), model_loader.player_db) if base_data.get('batsman_1') else 0
        batsman_2_avg = get_batsman_avg(base_data.get('batsman_2', ''), model_loader.player_db) if base_data.get('batsman_2') else 0
        
        balls_remaining = 300 - base_data['balls_bowled']
        current_run_rate = (base_data['current_score'] * 6.0 / base_data['balls_bowled']) if base_data['balls_bowled'] > 0 else 0
        
        base_scenario = {
            'current_score': base_data['current_score'],
            'wickets_fallen': base_data['wickets_fallen'],
            'balls_bowled': base_data['balls_bowled'],
            'balls_remaining': balls_remaining,
            'runs_last_10_overs': base_data['runs_last_10_overs'],
            'current_run_rate': current_run_rate,
            'team_batting_avg': batting_agg['team_batting_avg'],
            'team_elite_batsmen': batting_agg['team_elite_batsmen'],
            'team_batting_depth': batting_agg['team_batting_depth'],
            'opp_bowling_economy': bowling_agg['opp_bowling_economy'],
            'opp_elite_bowlers': bowling_agg['opp_elite_bowlers'],
            'opp_bowling_depth': bowling_agg['opp_bowling_depth'],
            'venue_avg_score': base_data['venue_avg_score'],
            'batsman_1_avg': batsman_1_avg,
            'batsman_2_avg': batsman_2_avg,
            'venue': base_data['venue']
        }
        
        # Get model to use
        model_identifier = base_data.get('model', 'xgboost')
        model_name = resolve_model_identifier(model_identifier)
        model = model_loader.get_model(model_name)
        if model is None:
            return jsonify({'error': f'Model "{model_identifier}" not available'}), 400
        
        base_prediction = make_prediction(model, base_scenario)
        
        # New scenario with swapped batsman
        new_batsman_avg = get_batsman_avg(new_batsman, model_loader.player_db)
        new_scenario = base_scenario.copy()
        new_scenario['batsman_2_avg'] = new_batsman_avg
        
        new_prediction = make_prediction(model, new_scenario)
        
        impact = new_prediction - base_prediction
        
        return jsonify({
            'base_prediction': round(base_prediction, 1),
            'new_prediction': round(new_prediction, 1),
            'impact': round(impact, 1),
            'impact_percentage': round((impact / base_prediction) * 100, 2),
            'new_batsman': new_batsman,
            'new_batsman_avg': round(new_batsman_avg, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progressive', methods=['POST'])
def progressive():
    """
    Show progressive predictions at multiple match stages
    
    Expected input:
    {
        "batting_team_players": [...],
        "bowling_team_players": [...],
        "venue": "...",
        "venue_avg_score": 270,
        "match_progression": [
            {"over": 0, "score": 0, "wickets": 0},
            {"over": 10, "score": 55, "wickets": 1},
            {"over": 20, "score": 115, "wickets": 2},
            {"over": 30, "score": 180, "wickets": 3},
            {"over": 40, "score": 250, "wickets": 5}
        ],
        "final_score": 320 (optional, for comparison)
    }
    """
    try:
        data = request.json
        
        # Calculate team aggregates once
        batting_agg = calculate_team_aggregates(
            data['batting_team_players'],
            model_loader.player_db
        )
        
        bowling_agg = calculate_bowling_aggregates(
            data['bowling_team_players'],
            model_loader.player_db
        )
        
        # Get model to use
        model_identifier = data.get('model', 'xgboost')
        model_name = resolve_model_identifier(model_identifier)
        model = model_loader.get_model(model_name)
        if model is None:
            return jsonify({'error': f'Model "{model_identifier}" not available'}), 400
        
        predictions = []
        
        for checkpoint in data['match_progression']:
            balls_bowled = checkpoint['over'] * 6
            balls_remaining = 300 - balls_bowled
            
            # Estimate last 10 overs runs (rough approximation)
            if balls_bowled >= 60:
                last_10_runs = (checkpoint['score'] / checkpoint['over']) * 10 if checkpoint['over'] > 0 else 0
            else:
                last_10_runs = checkpoint['score']
            
            current_rr = (checkpoint['score'] * 6.0 / balls_bowled) if balls_bowled > 0 else 0
            
            scenario = {
                'current_score': checkpoint['score'],
                'wickets_fallen': checkpoint['wickets'],
                'balls_bowled': balls_bowled,
                'balls_remaining': balls_remaining,
                'runs_last_10_overs': last_10_runs,
                'current_run_rate': current_rr,
                'team_batting_avg': batting_agg['team_batting_avg'],
                'team_elite_batsmen': batting_agg['team_elite_batsmen'],
                'team_batting_depth': batting_agg['team_batting_depth'],
                'opp_bowling_economy': bowling_agg['opp_bowling_economy'],
                'opp_elite_bowlers': bowling_agg['opp_elite_bowlers'],
                'opp_bowling_depth': bowling_agg['opp_bowling_depth'],
                'venue_avg_score': data['venue_avg_score'],
                'batsman_1_avg': 0,
                'batsman_2_avg': 0,
                'venue': data['venue']
            }
            
            predicted = make_prediction(model, scenario)
            stage = get_match_stage(balls_bowled)
            mae, r2, confidence = calculate_confidence_interval(None, stage)
            
            predictions.append({
                'over': checkpoint['over'],
                'current_score': checkpoint['score'],
                'wickets': checkpoint['wickets'],
                'predicted_final': round(predicted, 1),
                'stage': stage,
                'r2': r2,
                'mae': mae,
                'confidence': confidence
            })
        
        result = {
            'predictions': predictions,
            'team_stats': {
                'batting': batting_agg,
                'bowling': bowling_agg
            }
        }
        
        if 'final_score' in data:
            result['actual_final_score'] = data['final_score']
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React frontend"""
    # If it's an API route, let Flask handle it normally
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    # Check if the build folder exists
    build_folder = os.path.join(app.static_folder) if app.static_folder else None
    
    if build_folder and os.path.exists(build_folder):
        # If path exists as a file, serve it
        if path != "" and os.path.exists(os.path.join(build_folder, path)):
            return send_from_directory(build_folder, path)
        # Otherwise serve index.html (for React Router)
        return send_from_directory(build_folder, 'index.html')
    else:
        # If build folder doesn't exist, show instructions
        return jsonify({
            'message': 'Frontend not built yet',
            'instructions': [
                '1. cd dashboard/frontend',
                '2. npm run build',
                '3. Restart this server',
                'OR access frontend separately at http://localhost:3000'
            ],
            'api_working': True
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("ODI Progressive Predictor API")
    print("="*60)
    print(f"Starting server on port {Config.PORT}...")
    print(f"API endpoints:")
    print(f"  - GET  /api/health")
    print(f"  - GET  /api/teams")
    print(f"  - GET  /api/players")
    print(f"  - GET  /api/venues")
    print(f"  - POST /api/predict")
    print(f"  - POST /api/whatif")
    print(f"  - POST /api/progressive")
    print(f"Frontend: http://localhost:{Config.PORT}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)

