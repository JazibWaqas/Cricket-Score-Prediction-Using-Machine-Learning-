import pandas as pd
import pickle
from sklearn.metrics import r2_score, mean_absolute_error
import os

print("VERIFYING OLD MODEL ON OLD DATA")
print("===============================")

try:
    # Load old test data
    if os.path.exists('../data/progressive_full_test.csv'):
        test_df = pd.read_csv('../data/progressive_full_test.csv')
        print(f"Loaded old test set: {len(test_df)} samples")
    else:
        print("Old test set not found!")
        exit()

    # Load old model
    with open('../models/progressive_model_full_features.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Loaded old model")

    # Features (need to match what the old model expects)
    # We can try to infer or use the standard list
    # Usually it's the same 16 features
    feature_cols = [
        'current_score', 'wickets_fallen', 'balls_bowled', 'balls_remaining',
        'runs_last_10_overs', 'current_run_rate',
        'team_batting_avg', 'team_elite_batsmen', 'team_batting_depth',
        'opp_bowling_economy', 'opp_elite_bowlers', 'opp_bowling_depth',
        'venue_avg_score', 'batsman_1_avg', 'batsman_2_avg', 'venue'
    ]
    
    X_test = test_df[feature_cols]
    y_test = test_df['final_score']

    # Predict
    y_pred = model.predict(X_test)

    # Metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    print(f"\nResults on OLD DATA:")
    print(f"R2: {r2:.4f}")
    print(f"MAE: {mae:.2f}")

except Exception as e:
    print(f"Error: {e}")
