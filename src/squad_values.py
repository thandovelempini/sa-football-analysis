"""
Squad market values (manually collected, not scraped)
- Source: Transfermarkt (transfermarkt.co.za) read manually 
- Each club's page shows squad size average age, and total market value directly 
- Values reflect Transfermarkt's current (2026-27) squad snapshot, not a season-specific historical value 
- The same squad_market_value_eur is used across all seasons in matches_multi_season.csv as a rough "current squad strength" proxy
"""

import pandas as pd

SQUAD_VALUES = [
    {"team_name": "Mamelodi Sundowns", "season": "2026-27", "squad_market_value_eur": 40_400_000, "squad_size": 44, "avg_age": 28.1},
    {"team_name": "AmaZulu", "season": "2026-27", "squad_market_value_eur": 10_880_000, "squad_size": 37 , "avg_age": 25.4},
    {"team_name": "Chippa United", "season": "2026-27", "squad_market_value_eur": 5_180_000, "squad_size": 35, "avg_age": 27.2},
    {"team_name": "Durban City", "season": "2026-27", "squad_market_value_eur": 6_830_000, "squad_size": 42, "avg_age": 28.0},
    {"team_name": "Golden Arrows", "season": "2026-27", "squad_market_value_eur": 6_830_000, "squad_size": 42, "avg_age": 26.8},
    {"team_name": "Kaizer Chiefs", "season": "2026-27", "squad_market_value_eur": 16_230_000, "squad_size": 33, "avg_age": 26.9},
    {"team_name": "Marumo Gallants", "season": "2026-27", "squad_market_value_eur": 2_930_000, "squad_size": 36, "avg_age": 28.6},
    {"team_name": "Orlando Pirates", "season": "2026-27", "squad_market_value_eur": 22_330_000, "squad_size": 38, "avg_age": 26.1},
    {"team_name": "Polokwane City", "season": "2026-27", "squad_market_value_eur": 4_680_000, "squad_size": 38, "avg_age": 27.7},
    {"team_name": "Richards Bay", "season": "2026-27", "squad_market_value_eur": 6_880_000, "squad_size": 35, "avg_age": 26.9},
    {"team_name": "Sekhukhune United", "season": "2026-27", "squad_market_value_eur": 9_700_000, "squad_size": 36, "avg_age": 26.8},
    {"team_name": "Siwelele", "season": "2026-27", "squad_market_value_eur": 5_250_000, "squad_size": 38, "avg_age": 27.0},
    {"team_name": "Stellenbosch", "season": "2026-27", "squad_market_value_eur": 6_080_000, "squad_size": 25, "avg_age": 27.5},
    {"team_name": "TS Galaxy", "season": "2026-27", "squad_market_value_eur": 3_680_000, "squad_size": 39, "avg_age": 26.3},
    {"team_name": "Kruger United", "season": "2026-27", "squad_market_value_eur": 2_080_000, "squad_size": 51, "avg_age": 28.4},
    {"team_name": "Milford FC", "season": "2026-27", "squad_market_value_eur": None, "squad_size": 39, "avg_age": 29.4},
]

def build_squad_values_table(rows = SQUAD_VALUES) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=[
        "team_name", "season", "squad_market_value_eur", "squad_size", "avg_age"
    ])
    return df

if __name__ == "__main__":
    df = build_squad_values_table()
    print(df)
    df.to_csv("data/processed/squad_values.csv", index=False)


