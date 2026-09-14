import pandas as pd
clean_df = pd.read_csv("data/processed/matches_multi_season.csv")
teams = pd.read_csv("data/processed/teams.csv")

print("Duplicate match_ids:", clean_df["match_id"].duplicated().sum())

match_team_names = set(clean_df["home_team"]) | set(clean_df["away_team"])
teams_csv_names = set(teams["team_name"])
print("Missing from teams.csv:", match_team_names - teams_csv_names)