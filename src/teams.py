"""
Team reference table for the Betway Premiership.

Source: Wikipedia season pages (stadiums table). Update each season as
teams change via promotion/relegation. Latitude/longitude are geocoded
manually/once — see geocode_stadiums() below to fill them in.
"""

import os
import pandas as pd

# macOS Python.org/Homebrew builds don't always use the system cert store,
# which makes HTTPS requests (e.g. to Nominatim) fail with
# SSLCertVerificationError. Point requests/geopy at certifi's bundle so this
# works regardless of how the script is run (terminal or an IDE's run button).
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass  # certifi not installed — geocode_stadiums() will surface the real error

# 2026-27 season squad — differs from 2025-26: Orbit College and Magesi
# relegated; Kruger United and Milford FC promoted.
TEAMS_2026_27 = [
    {"team_name": "AmaZulu", "city": "Durban", "stadium": "Moses Mabhida Stadium", "capacity": 55500},
    {"team_name": "Chippa United", "city": "East London", "stadium": "Buffalo City Stadium", "capacity": 16000},
    {"team_name": "Durban City", "city": "Durban", "stadium": "Chatsworth Stadium", "capacity": 22000},
    {"team_name": "Golden Arrows", "city": "Umlazi", "stadium": "King Zwelithini Stadium", "capacity": 10000},
    {"team_name": "Kaizer Chiefs", "city": "Johannesburg (Soweto)", "stadium": "FNB Stadium", "capacity": 94736},
    {"team_name": "Mamelodi Sundowns", "city": "Pretoria (Marabastad)", "stadium": "Loftus Versfeld Stadium", "capacity": 51762},
    {"team_name": "Marumo Gallants", "city": "Bloemfontein", "stadium": "Dr. Petrus Molemela Stadium", "capacity": 22000},
    {"team_name": "Orlando Pirates", "city": "Johannesburg (Soweto)", "stadium": "Orlando Stadium", "capacity": 37139},
    {"team_name": "Polokwane City", "city": "Polokwane", "stadium": "Old Peter Mokaba Stadium", "capacity": 15000},
    {"team_name": "Richards Bay", "city": "Richards Bay", "stadium": "Richards Bay Stadium", "capacity": 8000},
    {"team_name": "Sekhukhune United", "city": "Polokwane", "stadium": "Peter Mokaba Stadium", "capacity": 45500},
    {"team_name": "Siwelele", "city": "Bloemfontein", "stadium": "Dr. Petrus Molemela Stadium", "capacity": 22000},
    {"team_name": "Stellenbosch", "city": "Stellenbosch", "stadium": "Danie Craven Stadium", "capacity": 16000},
    {"team_name": "TS Galaxy", "city": "Mbombela", "stadium": "Mbombela Stadium", "capacity": 43500},
    {"team_name": "Kruger United", "city": "Mbombela", "stadium": "Mbombela Stadium", "capacity": 43500},
    {"team_name": "Milford FC", "city": "Durban", "stadium": "Sugar Ray Xulu Stadium", "capacity": 6500},
]

# 2025-26 season squad, from Wikipedia's season page stadiums table.
# Extend/adjust as you add seasons with different teams (promotion/relegation).
TEAMS_2025_26 = [
    {"team_name": "AmaZulu", "city": "Durban", "stadium": "Moses Mabhida Stadium", "capacity": 55500},
    {"team_name": "Chippa United", "city": "East London", "stadium": "Buffalo City Stadium", "capacity": 16000},
    {"team_name": "Durban City", "city": "Durban", "stadium": "Chatsworth Stadium", "capacity": 22000},
    {"team_name": "Golden Arrows", "city": "Umlazi", "stadium": "King Zwelithini Stadium", "capacity": 10000},
    {"team_name": "Kaizer Chiefs", "city": "Johannesburg (Soweto)", "stadium": "FNB Stadium", "capacity": 94736},
    {"team_name": "Magesi", "city": "Seshego", "stadium": "Seshego Stadium", "capacity": 15000},
    {"team_name": "Mamelodi Sundowns", "city": "Pretoria (Marabastad)", "stadium": "Loftus Versfeld Stadium", "capacity": 51762},
    {"team_name": "Marumo Gallants", "city": "Bloemfontein", "stadium": "Dr. Petrus Molemela Stadium", "capacity": 22000},
    {"team_name": "Orbit College", "city": "Rustenburg", "stadium": "Olympia Park", "capacity": 32000},
    {"team_name": "Orlando Pirates", "city": "Johannesburg (Soweto)", "stadium": "Orlando Stadium", "capacity": 37139},
    {"team_name": "Polokwane City", "city": "Polokwane", "stadium": "Old Peter Mokaba Stadium", "capacity": 15000},
    {"team_name": "Richards Bay", "city": "Richards Bay", "stadium": "Richards Bay Stadium", "capacity": 8000},
    {"team_name": "Sekhukhune United", "city": "Polokwane", "stadium": "Peter Mokaba Stadium", "capacity": 45500},
    {"team_name": "Siwelele", "city": "Bloemfontein", "stadium": "Dr. Petrus Molemela Stadium", "capacity": 22000},
    {"team_name": "Stellenbosch", "city": "Stellenbosch", "stadium": "Danie Craven Stadium", "capacity": 16000},
    {"team_name": "TS Galaxy", "city": "Mbombela", "stadium": "Mbombela Stadium", "capacity": 40929},
]

# Teams from the 2024-25 season that are no longer in the league
TEAMS_2024_25_HISTORICAL = [
    {"team_name": "Royal AM", "city": "Durban", "stadium": "Chatsworth Stadium", "capacity": 22000},
    {"team_name": "Cape Town City", "city": "Cape Town", "stadium": "Cape Town Stadium", "capacity": 55000},
    {"team_name": "Maritzburg United", "city": "Pietermaritzburg", "stadium": "Harry Gwala Stadium", "capacity": 12000},
    {"team_name": "Swallows FC", "city": "Johannesburg (Soweto)", "stadium": "Dobsonville Stadium", "capacity": 24000},
    {"team_name": "Cape Town Spurs", "city": "Cape Town", "stadium": "Cape Town Stadium", "capacity": 55000},
    {"team_name": "Baroka FC", "city": "Polokwane", "stadium": "Peter Mokaba Stadium", "capacity": 45500},
]


# Nominatim (OpenStreetMap) doesn't have these 5 stadiums indexed by name,
# so they're hardcoded here instead. Coordinates pulled from general
# knowledge, not a live lookup — worth a quick manual spot-check (e.g. on
# Google Maps) before relying on them for the travel-distance feature,
# especially Old Peter Mokaba Stadium vs Peter Mokaba Stadium (same city,
# easy to mix up).
MANUAL_COORDS = {
    "Chatsworth Stadium": (-29.910398, 30.877311),
    "King Zwelithini Stadium": (-29.969496, 30.899996),
    "Seshego Stadium": (-23.855407, 29.388459),
    "Loftus Versfeld Stadium": (-25.753229, 28.222435),
    "Old Peter Mokaba Stadium": (-23.924689, 29.468765),
    "Sugar Ray Xulu Stadium": (-29.768330, 30.884663),
}


def apply_manual_coords(df: pd.DataFrame) -> pd.DataFrame:
    """Fill in latitude/longitude for stadiums Nominatim can't find, using
    MANUAL_COORDS. Only fills rows that are still missing — won't overwrite
    a successful geocode."""
    for idx, row in df.iterrows():
        if pd.isna(row["latitude"]) and row["stadium"] in MANUAL_COORDS:
            lat, lon = MANUAL_COORDS[row["stadium"]]
            df.at[idx, "latitude"] = lat
            df.at[idx, "longitude"] = lon
    return df


def build_teams_table(rows=None) -> pd.DataFrame:
    if rows is None:
        rows = TEAMS_2025_26 + TEAMS_2026_27 + TEAMS_2024_25_HISTORICAL
    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset="team_name", keep="first").reset_index(drop=True)
    df.insert(0, "team_id", range(1, len(df) + 1))
    df["latitude"] = pd.NA
    df["longitude"] = pd.NA
    return df


def geocode_stadiums(df: pd.DataFrame, user_agent: str = "sa_football_analysis") -> pd.DataFrame:
    """
    Fill latitude/longitude columns using geopy + Nominatim.
    Run once, then cache results to data/processed/teams.csv rather than
    re-geocoding on every pipeline run (Nominatim rate-limits to 1 req/sec).
    """
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter

    geolocator = Nominatim(user_agent=user_agent)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    for idx, row in df.iterrows():
        query = f"{row['stadium']}, {row['city']}, South Africa"
        location = geocode(query)
        if location:
            df.at[idx, "latitude"] = location.latitude
            df.at[idx, "longitude"] = location.longitude
        else:
            print(f"[warn] could not geocode: {query}")

    return df


if __name__ == "__main__":
    teams = build_teams_table()
    teams = geocode_stadiums(teams)
    teams = apply_manual_coords(teams)
    print(teams)
    teams.to_csv("data/processed/teams.csv", index=False)