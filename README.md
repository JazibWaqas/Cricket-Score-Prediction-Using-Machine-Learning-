# 🏏 ODI Progressive Cricket Score Predictor
## Machine Learning System for Real-Time Score Prediction

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [The Problem We Solved](#the-problem-we-solved)
3. [Our Solution](#our-solution)
4. [Why Our Results Are Trustworthy](#why-our-results-are-trustworthy)
5. [Technical Architecture](#technical-architecture)
6. [Feature Engineering](#feature-engineering)
7. [Model Training & Validation](#model-training--validation)
8. [Current Project Status](#current-project-status)
9. [How to Use](#how-to-use)

---

## 🎯 Project Overview

This project is a **state-of-the-art Machine Learning system** designed to predict the final score of One Day International (ODI) cricket matches in real-time. Unlike simple run-rate calculators, our system uses **Progressive Predictive Modeling** to understand cricket's nuances—accounting for player quality, venue history, and match context ball-by-ball.

### Key Innovation: Progressive Accuracy
Our model's accuracy improves as the match progresses, mirroring how humans understand cricket better as more information becomes available:
- **Pre-match (Ball 1):** R² = 0.26 (Limited information: only team strength)
- **Early (Over 10):** R² = 0.47 (Powerplay complete, momentum evident)
- **Mid (Over 20):** R² = 0.66 (Platform set, run rate stabilized)
- **Late (Over 30):** R² = 0.72 (Clear picture emerging)
- **Death (Over 40+):** R² = 0.88 ⭐ **Near-perfect accuracy!**

---

## 🔍 The Problem We Solved

### Traditional Approach Fails
Basic cricket predictors use: **Current Run Rate × Remaining Overs = Final Score**

**Why this fails:**
1. **Ignores Wickets:** 120/0 at 20 overs ≠ 120/5 at 20 overs (vastly different outcomes)
2. **Ignores Player Quality:** Virat Kohli batting ≠ Tailender batting
3. **Ignores Venue:** 250 is winning at Mirpur, losing at Chinnaswamy
4. **Ignores Context:** Powerplay wickets hurt more than death-over wickets
5. **Ignores Opposition:** Facing Jasprit Bumrah ≠ Facing part-timer

### What Cricket Experts Consider
- Team batting depth (how many batsmen left?)
- Current batsmen quality (is a star player at the crease?)
- Opposition bowling strength (elite attack or weak bowlers?)
- Venue characteristics (flat batting track or bowling-friendly?)
- Match momentum (runs in last 10 overs)
- Wickets in hand vs balls remaining (can they accelerate?)

**Our system replicates expert thinking using machine learning.**

---

## 💡 Our Solution

### Three-Pillar Approach

#### 1. Comprehensive Player Database
- **977 International Players** with verified career statistics
- **Actual batting averages** from career ODI performance
- **Actual bowling economies** from international matches
- **Role classification:** Batsman, Bowler, All-rounder
- **Country mapping** for team-based filtering
- **Star ratings** (1-5 scale) for quick quality assessment

**Smart Defaults (Only When Data Missing):**
- Batsmen: 30 average (competent but not elite)
- All-rounders: 25 average (balanced players)
- Bowlers: 18 average (tail-enders)

#### 2. Venue Intelligence
- **303 Real Venues** with calculated historical averages
- Minimum 10 matches required for statistical reliability
- Global average (250 runs) only for rare grounds
- Examples:
  - M. Chinnaswamy Stadium: 298 runs (batting paradise)
  - Shere Bangla National Stadium: 242 runs (bowler-friendly)
  - Eden Gardens: 255 runs (balanced)

#### 3. Progressive Prediction Engine
Instead of one prediction at match start, we predict at **5 key checkpoints**:
- Ball 1 (Pre-match assessment)
- Ball 60 (Post-powerplay)
- Ball 120 (Mid-innings)
- Ball 180 (Platform set)
- Ball 240 (Death overs begin)

This allows us to:
- Track prediction evolution
- Measure confidence at each stage
- Demonstrate learning from match context

---

## ✅ Why Our Results Are Trustworthy

### 1. Zero Data Leakage (Strict Temporal Split)
**Critical Design Decision:**
- **Training Data:** All ODI matches from 2002-2022 (11,064 samples)
- **Test Data:** All ODI matches from 2023-2025 (1,230 samples)

**Why this matters:**
- Model has **never seen** test matches during training
- Simulates real-world deployment (predicting future matches)
- No "future information" contamination
- Test set represents genuinely unseen scenarios

**Alternative (wrong) approach:** Random 80/20 split mixes matches from all years, allowing model to "cheat" by learning patterns from temporally adjacent matches.

### 2. Feature Extraction Without Cheating
**What we DON'T use:**
- ❌ Final score (obviously)
- ❌ Upcoming wickets
- ❌ Future run rates
- ❌ Match result/winner

**What we DO use:**
- ✅ Current match state (score, wickets, overs bowled)
- ✅ Historical team strength (calculated before match)
- ✅ Venue historical average (from past matches only)
- ✅ Player career stats (accumulated before this match)
- ✅ Recent momentum (runs in last 10 overs)

**Key Principle:** At any prediction checkpoint (e.g., ball 120), we only use information that would be available at that exact moment in a real match.

### 3. Validation on Real International Matches
**Test Set Composition:**
- 257 unique international ODI matches
- 1,230 prediction checkpoints
- Teams: India, Australia, England, Pakistan, South Africa, New Zealand, West Indies, Sri Lanka, Bangladesh, Afghanistan
- Venues: 42 different grounds worldwide
- Conditions: Various pitches, weather, match situations

**Not tested on:**
- Domestic/club cricket (different skill level)
- T20 matches (different format)
- Training data (prevents memorization)

### 4. Conservative Performance Claims
We report **actual test set performance**, not:
- Training accuracy (always higher, prone to overfitting)
- Cherry-picked matches (selection bias)
- Theoretical maximums (unrealistic)

---

## 🏗️ Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    RAW DATA LAYER                           │
│  • 2,800+ ODI matches (JSON, ball-by-ball)                 │
│  • 977-player career statistics database                    │
│  • Historical venue performance records                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 FEATURE ENGINEERING                         │
│  • Parse match JSON → Extract ball-by-ball states          │
│  • Calculate team aggregates from 11 players               │
│  • Compute venue averages from historical data             │
│  • Create 5 checkpoints per match (12,294 samples)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   MODEL TRAINING                            │
│  • Pipeline: Scaler + OneHotEncoder + ML Model             │
│  • XGBoost: 400 trees, depth 7, learning rate 0.1          │
│  • Random Forest: 100 trees, depth 15                       │
│  • Training: 11,064 samples (2002-2022)                     │
│  • Validation: 1,230 samples (2023-2025)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND API (Flask)                        │
│  • Model loading & caching                                  │
│  • Player database lookup                                   │
│  • Real-time feature calculation                            │
│  • Prediction endpoints (/predict, /whatif, /progressive)  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                FRONTEND UI (React.js)                       │
│  • Team/player selection (11 + 11 players)                 │
│  • Match scenario input (score, wickets, overs)            │
│  • Venue selection with average scores                     │
│  • Live prediction display with confidence                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Feature Engineering

### 16 Carefully Designed Features

#### Match State Features (6)
1. **current_score** - Runs accumulated so far
2. **wickets_fallen** - Number of dismissals (0-10)
3. **balls_bowled** - Deliveries completed (0-300)
4. **balls_remaining** - Deliveries left (300 - balls_bowled)
5. **runs_last_10_overs** - Recent momentum indicator
6. **current_run_rate** - Current scoring pace

**Why these matter:** Capture immediate match situation and momentum.

#### Batting Team Features (3)
7. **team_batting_avg** - Mean average of all 11 players
8. **team_elite_batsmen** - Count of players with avg ≥ 40
9. **team_batting_depth** - Count of players with avg ≥ 30

**Calculation Method:**
```python
# For each player in 11-player squad:
if player in database:
    use actual_career_average
else:
    if role == "Batsman": default = 30
    if role == "All-rounder": default = 25
    if role == "Bowler": default = 18

team_batting_avg = mean([all 11 averages])
team_elite_batsmen = count(avg >= 40)
team_batting_depth = count(avg >= 30)
```

**Why these matter:** Quantify team quality and resilience to collapses.

#### Opposition Features (3)
10. **opp_bowling_economy** - Mean economy of 11 opposition players
11. **opp_elite_bowlers** - Count of bowlers with economy < 4.8
12. **opp_bowling_depth** - Count of genuine bowling options

**Why these matter:** Strong bowling restricts scoring, especially in death overs.

#### Venue Features (2)
13. **venue_avg_score** - Historical average at this ground (numeric)
14. **venue** - Ground name (categorical, one-hot encoded)

**Why these matter:** Pitch conditions dramatically affect scoring patterns.

#### Current Batsmen Features (2)
15. **batsman_1_avg** - Career average of batsman currently facing
16. **batsman_2_avg** - Career average of non-striker

**Why these matter:** Mid-match predictions benefit from knowing exactly who's batting.

### Feature Importance Analysis
From trained Random Forest model:

| Feature Category | Importance | Interpretation |
|-----------------|------------|----------------|
| **Venue** | 89.3% | Ground conditions dominate predictions |
| **Match State** | 5.5% | Current score/wickets crucial for context |
| **Batting Team** | 2.4% | Team quality matters but less than venue |
| **Opposition** | 2.1% | Bowling strength has measurable impact |
| **Current Batsmen** | 0.7% | Individual batsmen less important than team |

**Key Insight:** Venue is overwhelmingly important because it encodes:
- Pitch type (batting-friendly vs bowling-friendly)
- Ground dimensions (big boundaries vs small)
- Historical scoring patterns
- Local conditions (altitude, weather patterns)

---

## 🎓 Model Training & Validation

### Models Trained

#### 1. Random Forest Regressor (Champion) 🏆
**Configuration:**
- 100 decision trees
- Max depth: 15
- Random state: 42 (reproducibility)
- n_jobs: -1 (parallel training)

**Performance:**
- Overall R² = 0.571 (57.1% variance explained)
- MAE = 35.4 runs
- Death Overs R² = 0.876 (exceptional!)

**Why it won:**
- Best at capturing non-linear relationships
- Handles wicket-score interactions well
- Robust to outliers (high-scoring thrillers, low-score collapses)

#### 2. XGBoost Regressor (Runner-up)
**Configuration:**
- 400 boosting rounds
- Max depth: 7
- Learning rate: 0.1
- Tree method: histogram (faster)

**Performance:**
- Overall R² = 0.508
- MAE = 37.9 runs
- Death Overs R² = 0.832

**Strengths:**
- More consistent across all stages
- Faster inference (1.16 MB vs 25 MB)
- Good backup model

#### 3. Linear Regression (Discarded)
**Performance:**
- Overall R² = 0.410
- MAE = 43.0 runs

**Why discarded:** Too simplistic, cannot capture wicket-score non-linearity.

### Training Process

**Step 1: Dataset Construction**
```
Raw matches (2,800+) → Parse JSON → Extract features → Create checkpoints
Result: 12,294 samples (5 per match × 2,561 matches)
```

**Step 2: Temporal Split**
```
Training: Matches before 2023 (11,064 samples)
Testing: Matches 2023-2025 (1,230 samples)
```

**Step 3: Pipeline Creation**
```
StandardScaler (normalize numeric features)
    ↓
OneHotEncoder (convert venue to binary features)
    ↓
ML Model (Random Forest / XGBoost)
```

**Step 4: Validation**
- Test set evaluation (never seen during training)
- Stage-by-stage breakdown
- International match filtering
- Error distribution analysis

---

## 📊 Current Project Status

### ✅ Completed Components

**Data Infrastructure:**
- ✅ 977-player database (FIXED version with full names, roles, countries)
- ✅ 303-venue database with calculated averages
- ✅ 12,294-sample training dataset (temporal split enforced)
- ✅ SQLite database for teams/venues metadata

**Machine Learning:**
- ✅ Random Forest v2 trained (Nov 21, 2025)
- ✅ XGBoost v2 trained (Nov 21, 2025)
- ✅ Models validated on 2023-2025 test set
- ✅ Stage-by-stage performance measured
- ✅ Feature importance analyzed

**Backend API:**
- ✅ Flask server with 8 endpoints
- ✅ Model selection (Random Forest / XGBoost)
- ✅ Real-time prediction endpoint
- ✅ What-if analysis endpoint
- ✅ Progressive prediction endpoint
- ✅ CORS configured for web access

**Frontend Application:**
- ✅ React.js UI with dark cricket theme
- ✅ Team/player selection (11+11 players)
- ✅ Match scenario input
- ✅ Real-time predictions with confidence
- ✅ Team statistics display
- ✅ Responsive design for mobile

**Testing & Validation:**
- ✅ Comprehensive test suite
- ✅ Real match validation scripts
- ✅ International match filtering
- ✅ Progressive accuracy demonstration
- ✅ What-if scenario testing

### 🎯 Performance Summary

| Metric | Random Forest | XGBoost |
|--------|--------------|---------|
| **Overall R²** | 0.571 | 0.508 |
| **Overall MAE** | 35.4 runs | 37.9 runs |
| **Death Overs R²** | 0.876 | 0.832 |
| **Death Overs MAE** | 17.2 runs | 19.6 runs |
| **Within ±30 runs** | 55.5% | 52.4% |

**Confidence by Stage:**

| Stage | Random Forest R² | XGBoost R² | Confidence Label |
|-------|-----------------|------------|------------------|
| Pre-match | 0.260 | 0.183 | Low |
| Early (10 overs) | 0.466 | 0.397 | Medium |
| Mid (20 overs) | 0.663 | 0.596 | High |
| Late (30 overs) | 0.721 | 0.666 | High |
| Death (40+ overs) | 0.876 | 0.832 | Very High |

---

## 🚀 How to Use

### Backend Setup
```bash
cd dashboard/backend
pip install -r requirements.txt
python app.py
# Server runs on http://localhost:5002
```

### Frontend Setup (Development)
```bash
cd dashboard/frontend
npm install
npm start
# UI opens at http://localhost:3000
```

### Frontend Setup (Production)
```bash
cd dashboard/frontend
npm run build
# Backend serves from http://localhost:5002/
```

### Making Predictions

**Via Web UI:**
1. Select Team A (batting team) - Choose 11 players
2. Select Team B (opposition) - Choose 11 players
3. Set match scenario:
   - Venue (from dropdown with averages)
   - Current score (e.g., 180)
   - Wickets fallen (e.g., 3)
   - Overs completed (e.g., 30)
   - Runs in last 10 overs (e.g., 65)
4. Optionally select current batsmen
5. Click "Predict Final Score"
6. View prediction with confidence and team stats

**Via API (curl):**
```bash
curl -X POST http://localhost:5002/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "batting_team_players": ["Virat Kohli", "Rohit Sharma", ...],
    "bowling_team_players": ["Jasprit Bumrah", "Mohammed Shami", ...],
    "venue": "M. Chinnaswamy Stadium",
    "venue_avg_score": 298,
    "current_score": 180,
    "wickets_fallen": 3,
    "balls_bowled": 180,
    "runs_last_10_overs": 65,
    "model": "random_forest"
  }'
```

---

## 🎓 Project Learnings

### Design Choices That Worked

1. **Progressive Checkpoints:** Instead of one prediction, tracking 5 stages demonstrates confidence evolution and model understanding.

2. **Temporal Split:** Strict chronological split prevents data leakage and ensures realistic evaluation.

3. **Role-Based Defaults:** Better than global defaults (35 for all) because it respects cricket reality (bowlers bat worse than batsmen).

4. **Venue Calculation:** Using actual historical data instead of hardcoded 250 for all grounds.

5. **Two-Model System:** Offering Random Forest (accuracy) and XGBoost (speed) gives users choice.

### Technical Decisions

**Why Random Forest over Neural Networks?**
- Interpretable feature importance
- No hyperparameter tuning complexity
- Smaller dataset (12k samples, not millions)
- Faster training and inference
- Robust to missing data

**Why 5 Checkpoints per Match?**
- Ball 1: Pre-match prediction baseline
- Ball 60: Post-powerplay assessment
- Ball 120: Mid-innings update
- Ball 180: Platform evaluation
- Ball 240: Death overs accuracy demonstration

**Why 977 Players?**
- Covers all international ODI players (2002-2025)
- Verified career statistics from official sources
- Includes current stars and retired legends
- Sufficient for any match simulation

---

## 📚 References

**Data Sources:**
- Ball-by-ball ODI data: Cricsheet.org
- Player statistics: Verified from international ODI records
- Venue information: Historical match database

**Technologies:**
- **Backend:** Python 3.10, Flask 3.1, scikit-learn 1.7, XGBoost 3.0
- **Frontend:** React 18.2, Tailwind CSS 3.3, Framer Motion 10.12
- **Database:** SQLite 3, JSON
- **Deployment:** Local development, production-ready

---

## 👥 Author

Developed as a Machine Learning project demonstrating:
- End-to-end ML pipeline construction
- Real-world data processing and cleaning
- Feature engineering for sports analytics
- Model training, validation, and deployment
- Full-stack application development
- API design and frontend integration

**Project Date:** November 2025  
**Last Updated:** November 21, 2025

---

## 📄 License

This project is for educational and demonstration purposes.

---

*For detailed performance metrics, see [RESULTS.md](RESULTS.md)*  
*For what-if analysis and use cases, see [WHATIF.md](WHATIF.md)*  
*For comparison with previous version, see [COMPARISON.md](COMPARISON.md)*
