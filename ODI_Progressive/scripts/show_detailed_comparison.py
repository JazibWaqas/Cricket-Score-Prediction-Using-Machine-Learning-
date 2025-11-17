#!/usr/bin/env python3
"""Show detailed stage-by-stage comparison"""

import json

data = json.load(open('../results/model_comparison.json'))

print("\n" + "="*80)
print("DETAILED STAGE-BY-STAGE COMPARISON")
print("="*80)

print("\nOVERALL METRICS:")
print(f"  OLD Model: R² = {data['old_model']['r2']:.4f}, MAE = {data['old_model']['mae']:.2f} runs")
print(f"  NEW Model: R² = {data['new_model']['r2']:.4f}, MAE = {data['new_model']['mae']:.2f} runs")
print(f"  Difference: R² = {data['difference']['r2']:+.4f} ({data['difference']['r2']/data['old_model']['r2']*100:+.2f}%), MAE = {data['difference']['mae']:+.2f} runs")

print("\nACCURACY COMPARISON:")
print(f"  ±10 runs: OLD {data['old_model']['accuracy_within_10']:.1f}% vs NEW {data['new_model']['accuracy_within_10']:.1f}% (NEW +{data['difference']['accuracy_within_10']:+.1f}%)")
print(f"  ±20 runs: OLD {data['old_model']['accuracy_within_20']:.1f}% vs NEW {data['new_model']['accuracy_within_20']:.1f}% (NEW +{data['difference']['accuracy_within_20']:+.1f}%)")
print(f"  ±30 runs: OLD {data['old_model']['accuracy_within_30']:.1f}% vs NEW {data['new_model']['accuracy_within_30']:.1f}% (OLD +{abs(data['difference']['accuracy_within_30']):.1f}%)")

print("\n" + "="*80)
print("RECOMMENDATION RECONSIDERATION")
print("="*80)

print("\nKey Points:")
print("  1. Overall R² difference: -0.019 (-3.6%) - VERY SMALL")
print("  2. Overall MAE difference: +0.11 runs - NEGLIGIBLE")
print("  3. NEW model BETTER at tight accuracy (±10, ±20 runs)")
print("  4. NEW model has better data quality (full names, star ratings, country)")
print("  5. NEW model uses role-based defaults (more realistic)")

print("\nRECOMMENDATION: Use NEW Model")
print("  - Performance difference is minimal (<4%)")
print("  - Better accuracy at tighter margins")
print("  - Better data quality and consistency")
print("  - More maintainable long-term")

print("\n" + "="*80)

