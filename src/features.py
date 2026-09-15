"""
Feature engineering: turns a clean 'matches' table into the rolling-form and other engineered features used by the model
"""

import pandas as pd


def add_rolling_form(matches: pd.DataFrame, n_games: int = 5) -> pd.DataFrame:
    matches = matches.sort_values("date").reset_index(drop=True)

    home = matches[["match_id", "date", "home_team", "home_score", "away_score", "result"]].copy()
    home = home.rename(columns={"home_team": "team"})
    home["points"] = home["result"].map({"H": 3, "D": 1, "A": 0})

    away = matches[["match_id", "date", "away_team", "home_score", "away_score", "result"]].copy()
    away = away.rename(columns={"away_team": "team"})
    away["points"] = away["result"].map({"H": 0, "D": 1, "A": 3})

    long_form = pd.concat([home, away], ignore_index=True).sort_values(["team", "date"])
    long_form[f"rolling_points_last{n_games}"] = (
        long_form.groupby("team")["points"]
        .transform(lambda s: s.shift(1).rolling(n_games, min_periods=1).sum())
    )

    home_roll = long_form[["match_id", "team", f"rolling_points_last{n_games}"]].rename(
        columns={"team": "home_team", f"rolling_points_last{n_games}": f"home_rolling_points_last{n_games}"}
    )
    away_roll = long_form[["match_id", "team", f"rolling_points_last{n_games}"]].rename(
        columns={"team": "away_team", f"rolling_points_last{n_games}": f"away_rolling_points_last{n_games}"}
    )

    matches = matches.merge(home_roll, on=["match_id", "home_team"], how="left")
    matches = matches.merge(away_roll, on=["match_id", "away_team"], how="left")

    return matches


def add_goal_diff_trend(matches: pd.DataFrame, n_games: int = 5) -> pd.DataFrame:
    matches = matches.sort_values("date").reset_index(drop=True)

    home = matches[["match_id", "date", "home_team", "home_score", "away_score"]].copy()
    home["gd"] = home["home_score"] - home["away_score"]
    home = home.rename(columns={"home_team": "team"})[["match_id", "date", "team", "gd"]]

    away = matches[["match_id", "date", "away_team", "home_score", "away_score"]].copy()
    away["gd"] = away["away_score"] - away["home_score"]
    away = away.rename(columns={"away_team": "team"})[["match_id", "date", "team", "gd"]]

    long_form = pd.concat([home, away], ignore_index=True).sort_values(["team", "date"])
    long_form[f"gd_trend_last{n_games}"] = (
        long_form.groupby("team")["gd"]
        .transform(lambda s: s.shift(1).rolling(n_games, min_periods=1).mean())
    )

    home_trend = long_form[["match_id", "team", f"gd_trend_last{n_games}"]].rename(
        columns={"team": "home_team", f"gd_trend_last{n_games}": f"home_gd_trend_last{n_games}"}
    )
    away_trend = long_form[["match_id", "team", f"gd_trend_last{n_games}"]].rename(
        columns={"team": "away_team", f"gd_trend_last{n_games}": f"away_gd_trend_last{n_games}"}
    )

    matches = matches.merge(home_trend, on=["match_id", "home_team"], how="left")
    matches = matches.merge(away_trend, on=["match_id", "away_team"], how="left")

    return matches


def add_travel_distance(matches: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:

    from math import radians, sin, cos, sqrt, atan2

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # km
        dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        return 2 * R * atan2(sqrt(a), sqrt(1 - a))

    coords = teams.set_index("team_name")[["latitude", "longitude"]]

    def dist_row(row):
        try:
            h = coords.loc[row["home_team"]]
            a = coords.loc[row["away_team"]]
            return haversine(h["latitude"], h["longitude"], a["latitude"], a["longitude"])
        except KeyError:
            return pd.NA

    matches["travel_distance_km"] = matches.apply(dist_row, axis=1)
    return matches

def add_squad_value_features(matches: pd.DataFrame, squad_values: pd.DataFrame) -> pd.DataFrame:
    values = squad_values.set_index("team_name")["squad_market_value_eur"]

    matches = matches.copy()
    matches["home_squad_value"] = matches["home_team"].map(values)
    matches["away_squad_value"] = matches["away_team"].map(values)

    matches["squad_value_ratio"] = matches["home_squad_value"] / matches["away_squad_value"]

    return matches

def build_feature_set(matches: pd.DataFrame, teams: pd.DataFrame, squad_values: pd.DataFrame = None) -> pd.DataFrame:
    matches = add_rolling_form(matches, n_games=5)
    matches = add_rolling_form(matches, n_games=10)
    matches = add_goal_diff_trend(matches, n_games=5)
    matches = add_travel_distance(matches, teams)
    if squad_values is not None:
        matches = add_squad_value_features(matches, squad_values)
    return matches

if __name__ == "__main__":
    import pandas as pd

    matches = pd.read_csv("data/processed/matches_multi_season.csv", parse_dates=["date"])
    teams = pd.read_csv("data/processed/teams.csv")
    squad_values = pd.read_csv("data/processed/squad_values.csv")

    features_df = build_feature_set(matches, teams, squad_values)

    print(features_df.shape)
    print(features_df[[
        "date", "home_team", "away_team", "result",
        "home_rolling_points_last5", "away_rolling_points_last5",
        "home_gd_trend_last5", "travel_distance_km",
        "home_squad_value", "away_squad_value", "squad_value_ratio"
    ]].head(15))

    features_df.to_csv("data/processed/matches_features.csv", index=False)