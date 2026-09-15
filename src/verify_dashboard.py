"""
Cross-checks the numbers shown on the Power BI dashboard against the CSV files, 
using the same logic as the DAX measures

"""

import pandas as pd

matches = pd.read_csv("data/processed/matches_multi_season.csv", parse_dates=["date"])
predictions = pd.read_csv("data/processed/model_predictions.csv", parse_dates=["date"])
features = pd.read_csv("data/processed/matches_features.csv", parse_dates=["date"])

print("=== Page 1: Betway Premiership Performance ===")

# Matches Played
print(f"Matches Played: {len(matches)}  (dashboard: 1440)")

# Goals per Match
goals_per_match = (matches["home_score"] + matches["away_score"]).mean()
print(f"Goals per Match: {goals_per_match:.2f}  (dashboard: 2.05)")

# Home Win %
home_win_pct = (matches["result"] == "H").mean()
print(f"Home Win %: {home_win_pct:.1%}  (dashboard: 34.6%)")

# Seasons
print(f"Seasons: {matches['season'].nunique()}  (dashboard: 6)")

# Goals per match by season (2021-22 vs 2025-26)
matches["total_goals"] = matches["home_score"] + matches["away_score"]
by_season = matches.groupby("season")["total_goals"].mean()
print("\nGoals per match by season:")
print(by_season.round(2))

# Home win rate, longest vs shortest travel (top/bottom 25%)
q75 = features["travel_distance_km"].quantile(0.75)
q25 = features["travel_distance_km"].quantile(0.25)
high_travel = features[features["travel_distance_km"] >= q75]
low_travel = features[features["travel_distance_km"] <= q25]
away_win_high = (high_travel["result"] == "A").mean()
away_win_low = (low_travel["result"] == "A").mean()
print(f"\nAway win %, high travel: {away_win_high:.1%}  (dashboard: 25.0%)")
print(f"Away win %, low travel: {away_win_low:.1%}  (dashboard: 27.4%)")

print("\n=== Page 2: Match Outcome Prediction ===")

accuracy = predictions["correct"].mean()
print(f"Model Accuracy: {accuracy:.1%}  (dashboard: 45.5%)")
print(f"Matches Predicted: {len(predictions)}  (dashboard: 242)")
print(f"Correct Predictions: {predictions['correct'].sum()}  (dashboard: 110)")

print("\nConfusion matrix (Actual rows x Predicted columns):")
confusion = pd.crosstab(predictions["actual_result"], predictions["predicted_result"])
print(confusion.reindex(index=["H", "D", "A"], columns=["H", "D", "A"]))

print("\nPer-class accuracy (recall):")
for outcome in ["H", "D", "A"]:
    subset = predictions[predictions["actual_result"] == outcome]
    recall = (subset["predicted_result"] == outcome).mean()
    print(f"  {outcome}: {recall:.1%}")