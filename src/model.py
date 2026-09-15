"""
Model: predicts match result (Home win / Draw / Away win) from the engineered features in features.py
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score

FEATURE_COLUMNS = [
    "home_rolling_points_last5",
    "away_rolling_points_last5",
    "home_rolling_points_last10",
    "away_rolling_points_last10",
    "home_gd_trend_last5",
    "away_gd_trend_last5",
    "travel_distance_km",
]

TARGET_COLUMN = "result"  # H / D / A


def prepare_data(df: pd.DataFrame):
    df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).sort_values("date")

    split_idx = int(len(df) * 0.8)
    train, test = df.iloc[:split_idx], df.iloc[split_idx:]

    X_train, y_train = train[FEATURE_COLUMNS], train[TARGET_COLUMN]
    X_test, y_test = test[FEATURE_COLUMNS], test[TARGET_COLUMN]

    return X_train, X_test, y_train, y_test


def train_logistic_regression(X_train, y_train):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_scaled, y_train)

    return model, scaler


def train_gradient_boosting(X_train, y_train):
    model = HistGradientBoostingClassifier(max_iter=100, random_state=42)
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test, scaler=None, label=""):
    X_eval = scaler.transform(X_test) if scaler is not None else X_test
    preds = model.predict(X_eval)

    print(f"\n--- {label} ---")
    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(classification_report(y_test, preds, zero_division=0))


if __name__ == "__main__":
    df = pd.read_csv("data/processed/matches_features.csv", parse_dates=["date"])

    X_train, X_test, y_train, y_test = prepare_data(df)

    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    if len(X_train) < 100:
        print(
            "[warn] small training set — treat results as directional, "
            "not a robust estimate. More seasons of matches data will help."
        )

    logreg_model, scaler = train_logistic_regression(X_train, y_train)
    evaluate(logreg_model, X_test, y_test, scaler=scaler, label="Logistic Regression")

    gbm_model = train_gradient_boosting(X_train, y_train)
    evaluate(gbm_model, X_test, y_test, label="Gradient Boosting")
    
"""
- Training data went from 170 to 965 rows, and tests set from 43 to 186 rows
- Logistic regression accuracy went from 37.2% to 45.5% 

- Model is now learning something about draws rather than just always guessing 'home win'
- Gradient boosting also improved, but logistics regression is the stronger of the two

- Away-win prediction improved: precision/recall on "A" went from 0.50/0.30 to 0.49/0.41 - the model got noticeably better at catching away wins, 
which makes sense: squad value asymmetry is what helps predict an big loss or a dominant away performance

- What this 45.5% means: Professional football prediction models often sit in the 45-55% range for exact result predictions
- What we have now is a good ballpark (above chance)

- Went from: 
1. 170 rows, single season → 37.2%, model collapses to one class to 
2. 743 rows, 4 seasons → 44.6%, draws start being predicted to
3. 965 rows, 6 seasons + squad value → 45.5%, away-win prediction improves
"""
