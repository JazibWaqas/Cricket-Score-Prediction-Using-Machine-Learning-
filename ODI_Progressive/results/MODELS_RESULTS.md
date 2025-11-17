
# 🏏 COMPREHENSIVE MODEL COMPARISON RESULTS

**Test Date:** 2025-11-17 12:38:50  
**Test Samples:** 1,230  
**Real International Matches:** 300 matches

---

## 📊 EXECUTIVE SUMMARY


### Overall Performance (Test Set)

| Model | R² Score | MAE (runs) | Accuracy ±10 | Accuracy ±20 | Accuracy ±30 |
|-------|----------|------------|--------------|--------------|--------------|
| XGBoost | 0.5075 (50.75%) | 37.94 | 21.5% | 39.9% | 52.4% |
| RandomForest | 0.5710 (57.10%) | 35.41 | 22.4% | 40.5% | 55.5% |
| LinearRegression | 0.4105 (41.05%) | 43.04 | 15.9% | 32.0% | 45.0% |

**Best Model (Test Set):** RandomForest (R² = 0.5710)

### Real International Matches Performance

| Model | R² Score | MAE (runs) | Samples |
|-------|----------|------------|----------|
| XGBoost | 0.0499 (4.99%) | 47.73 | 1477 |
| RandomForest | -0.1042 (-10.42%) | 51.36 | 1477 |
| LinearRegression | -0.2248 (-22.48%) | 56.37 | 1477 |

**Best Model (Real Matches):** XGBoost (R² = 0.0499)

## 📈 Stage-by-Stage Performance

### Test Set Performance by Stage

#### Pre-match (ball 1)

| Model | R² Score | MAE (runs) | Samples |
|-------|----------|------------|----------|
| XGBoost | 0.1833 (18.33%) | 53.18 | 257 |
| RandomForest | 0.2599 (25.99%) | 51.13 | 257 |
| LinearRegression | 0.0922 (9.22%) | 57.47 | 257 |

#### Early (ball 60)

| Model | R² Score | MAE (runs) | Samples |
|-------|----------|------------|----------|
| XGBoost | 0.3971 (39.71%) | 44.83 | 257 |
| RandomForest | 0.4664 (46.64%) | 42.02 | 257 |
| LinearRegression | 0.3172 (31.72%) | 49.28 | 257 |

#### Mid (ball 120)

| Model | R² Score | MAE (runs) | Samples |
|-------|----------|------------|----------|
| XGBoost | 0.5964 (59.64%) | 36.97 | 256 |
| RandomForest | 0.6629 (66.29%) | 34.32 | 256 |
| LinearRegression | 0.4790 (47.90%) | 43.07 | 256 |

#### Late (ball 180)

| Model | R² Score | MAE (runs) | Samples |
|-------|----------|------------|----------|
| XGBoost | 0.6661 (66.61%) | 31.93 | 244 |
| RandomForest | 0.7208 (72.08%) | 29.21 | 244 |
| LinearRegression | 0.5841 (58.41%) | 35.69 | 244 |

#### Death (ball 240)

| Model | R² Score | MAE (runs) | Samples |
|-------|----------|------------|----------|
| XGBoost | 0.8324 (83.24%) | 19.57 | 216 |
| RandomForest | 0.8760 (87.60%) | 17.16 | 216 |
| LinearRegression | 0.7028 (70.28%) | 26.72 | 216 |


## 🎯 Best and Worst Predictions

### XGBoost

**Best Prediction:**
- Team: Surrey
- Ball: 120
- Actual: 181 runs
- Predicted: 181 runs
- Error: 0.00 runs

**Worst Prediction:**
- Team: Maldives
- Ball: 1
- Actual: 73 runs
- Predicted: 275 runs
- Error: 201.71 runs

### RandomForest

**Best Prediction:**
- Team: Northern Diamonds
- Ball: 180
- Actual: 183 runs
- Predicted: 183 runs
- Error: 0.02 runs

**Worst Prediction:**
- Team: Tanzania
- Ball: 60
- Actual: 100 runs
- Predicted: 279 runs
- Error: 179.43 runs

### LinearRegression

**Best Prediction:**
- Team: Netherlands
- Ball: 180
- Actual: 204 runs
- Predicted: 204 runs
- Error: 0.02 runs

**Worst Prediction:**
- Team: Maldives
- Ball: 1
- Actual: 73 runs
- Predicted: 346 runs
- Error: 273.34 runs


## 🔍 Detailed Analysis

### XGBoost

- **R² Score:** 0.5075 (50.75%)
- **MAE:** 37.94 runs
- **Median Error:** 28.57 runs
- **Best Prediction Error:** 0.00 runs
- **Worst Prediction Error:** 201.71 runs
- **Accuracy ±10 runs:** 21.5% (264/1230)
- **Accuracy ±20 runs:** 39.9% (491/1230)
- **Accuracy ±30 runs:** 52.4% (645/1230)

### RandomForest

- **R² Score:** 0.5710 (57.10%)
- **MAE:** 35.41 runs
- **Median Error:** 26.18 runs
- **Best Prediction Error:** 0.02 runs
- **Worst Prediction Error:** 179.43 runs
- **Accuracy ±10 runs:** 22.4% (276/1230)
- **Accuracy ±20 runs:** 40.5% (498/1230)
- **Accuracy ±30 runs:** 55.5% (683/1230)

### LinearRegression

- **R² Score:** 0.4105 (41.05%)
- **MAE:** 43.04 runs
- **Median Error:** 33.99 runs
- **Best Prediction Error:** 0.02 runs
- **Worst Prediction Error:** 273.34 runs
- **Accuracy ±10 runs:** 15.9% (196/1230)
- **Accuracy ±20 runs:** 32.0% (394/1230)
- **Accuracy ±30 runs:** 45.0% (554/1230)


## ✅ Recommendations

**Note:** Different models perform best on test set vs real matches. Consider using the model that performs best on real matches for production.


---
**Generated:** 2025-11-17 12:38:50
