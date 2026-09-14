import json
import time
import requests
import pandas as pd

GRAPHQL_URL = "https://netsport.eurosport.io/"

PERSISTED_QUERY_HASH = "b367c2578b314815f61f33d3edd97a19b02540ce2d4a2b43baceb3130e835088"
TAXONOMY_ID = "ec636264-c9a9-458a-96cd-d2cc526e569f"  # Betway Premiership
SEASON_IDS = {
    "2026-2027": "2e7b901e-e988-5fcf-9258-0e2a368b4cf1",
    "2025-2026": "8883d2bb-f909-5c45-af11-6c9678736244",
    "2024-2025": "05bdd73f-3796-58c7-901c-2ef9bcfcd55c",
    "2023-2024": "7a53a75d-fc2a-55ad-b335-23670a5b4477",
    "2022-2023": "7dfde48f-a669-5db7-8b0c-2fd2977d5a3a",
    "2021-2022": "5e9129c1-90cf-547c-a171-2d8f8798f59b",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; sa-football-analysis/0.1)",
    "Referer": "https://www.tntsports.co.uk/",
    "domain": "www.tntsports.co.uk",
}


def build_variables(season_id, stage_id=None):
    """Builds the `variables` param. Pass stage_id=None to get the
    default/current matchday (also returns the full list of all
    matchday ids in the response). Pass a specific STAGES id to get
    that matchday's matches."""
    filters = [{"id": season_id, "type": "SEASONS"}]
    if stage_id:
        filters.append({"id": stage_id, "type": "STAGES"})

    return {
        "taxonomyId": TAXONOMY_ID,
        "genderNetsportId": None,
        "seasonNetsportId": None,
        "filters": filters,
        "first": 20,
        "after": None,
        "last": None,
        "before": None,
        "matchCardHeaderContext": "DEFAULT",
    }


def fetch_matchday(season_id, stage_id=None):
    """Makes the GraphQL request and returns the parsed JSON response."""
    params = {
        "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": PERSISTED_QUERY_HASH}}, separators=(",", ":")),
        "operationName": "scoreCenterCalendarResultsByTaxonomyIdQuery",
        "variables": json.dumps(build_variables(season_id, stage_id), separators=(",", ":")),
    }
    resp = requests.get(GRAPHQL_URL, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


def parse_fixtures(html: str, season: str, matchday: int) -> list[dict]:
    """
    Parse one matchday's HTML into a list of match dicts.

    NOTE: selector logic below is a starting guess based on the page
    structure seen (date header followed by "Home<score><score>Away"
    fixture links). Inspect the actual HTML once you have a working
    matchday URL and adjust selectors — TNT's markup may differ from
    what a plain-text fetch showed us.
    """
    soup = BeautifulSoup(html, "lxml")
    matches = []
    current_date = None

    # Fixture links look like: /.../live-home-team-away-team_mtcXXXXXXX/live.shtml
    # with visible text like "Orlando Pirates21Cape Town City"
    date_pattern = re.compile(r"^\d{2}/\d{2}/\d{4}$")

    for el in soup.find_all(string=True):
        text = el.strip()
        if not text:
            continue
        if date_pattern.match(text):
            current_date = text
            continue

    # Placeholder: actual fixture parsing depends on final HTML structure
    # once MATCHDAY_URL_TEMPLATE is working. Extend this once real pages
    # are available to inspect.

    return matches


def scrape_season(season_label, season_id) -> pd.DataFrame:
    """Fetches all matchdays for a season and returns one combined
    DataFrame of matches."""

    first_response = fetch_matchday(season_id)
    matchdays = extract_matchday_options(first_response)

    all_matches = []
    for label, stage_id in matchdays.items():
        print(f"Fetching {label}...")
        response = fetch_matchday(season_id, stage_id=stage_id)
        matches = extract_matches(response)
        for m in matches:
            m["matchday"] = label
            m["season"] = season_label
        all_matches.extend(matches)
        time.sleep(1)  # be polite to the API

    df = pd.DataFrame(all_matches)
    return df


def extract_matchday_options(response_json):
    """Pulls the {matchday_label: stage_id} map from any response —
    every response includes the full list of 30 matchday filter options,
    regardless of which matchday was requested."""
    picker_items = response_json["data"]["scoreCenterCalendarResultsByTaxonomyId"]["filters"]["picker"]["items"]
    options = picker_items[0]["options"]

    matchdays = {}
    for opt in options:
        label = opt["value"]["value"]  # e.g. "Matchday 1"
        stage_id = opt["id"]
        matchdays[label] = stage_id

    return matchdays


def extract_matches(response_json):
    """Pulls one matchday's matches into a list of dicts."""
    edges = response_json["data"]["scoreCenterCalendarResultsByTaxonomyId"]["matchCards"]["edges"]

    matches = []
    for edge in edges:
        node = edge["node"]

        home_score = node["scoreBox"].get("home", {}).get("score") if node["scoreBox"].get("home") else None
        away_score = node["scoreBox"].get("away", {}).get("score") if node["scoreBox"].get("away") else None

        date_str = None
        sections = node.get("scoreCenterClassification", {}).get("sections", [])
        for section in sections:
            if section.get("type") == "DATE":
                date_str = section.get("title")  # e.g. "21/02/2025"
                break

        matches.append({
            "home_team": node["home"]["name"],
            "away_team": node["away"]["name"],
            "home_score": home_score,
            "away_score": away_score,
            "status": node["status"],
            "date": date_str,
            "netsport_id": node.get("netsportId"),
        })

    return matches

NAME_FIXES = {
    "Chippa United FC": "Chippa United",
    "Siwelele FC": "Siwelele",
    "AmaZulu FC": "AmaZulu",
    "Durban City FC": "Durban City",
    "Orbit College FC": "Orbit College",
}

def clean_matches(df: pd.DataFrame) -> pd.DataFrame:
    """Converts raw scraped columns to proper types:
    - date: DD/MM/YYYY string -> datetime
    - home_score/away_score: string -> nullable integer (some are None
      for postponed/upcoming matches, so a plain int dtype won't work)
    - adds match_id and result (H/D/A) for use in features.py
    """
    df = df.copy()

    df["home_team"] = df["home_team"].replace(NAME_FIXES)
    df["away_team"] = df["away_team"].replace(NAME_FIXES)

    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")

    df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce").astype("Int64")
    df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce").astype("Int64")

    df["match_id"] = df["netsport_id"]

    def get_result(row):
        if pd.isna(row["home_score"]) or pd.isna(row["away_score"]):
            return None
        if row["home_score"] > row["away_score"]:
            return "H"
        elif row["home_score"] < row["away_score"]:
            return "A"
        else:
            return "D"

    df["result"] = df.apply(get_result, axis=1)

    return df

if __name__ == "__main__":
    all_seasons_dfs = []
    for season_label, season_id in SEASON_IDS.items():
        df = scrape_season(season_label, season_id)
        print(f"{season_label}: {len(df)} matches scraped")
        all_seasons_dfs.append(df)

    combined_df = pd.concat(all_seasons_dfs, ignore_index=True)
    print(f"\nTotal matches across all seasons: {len(combined_df)}")

    combined_df.to_csv("data/raw/matches_multi_season.csv", index=False)

    clean_df = clean_matches(combined_df)
    print(clean_df.dtypes)
    clean_df.to_csv("data/processed/matches_multi_season.csv", index=False)

