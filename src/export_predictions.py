"""
Trains the model and exports a clean predictions vs actuals table for use in the Power BI dashboard 
"""

import pandas as pd
from model import(
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    prepare_data,
    train_logistic_regression
)

def export_predictions():
    df = pd.read_csv("data/processed/matches_features.csv", parse_dates=["date"])

    df_clean = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).sort_values("date")

    X_train, X_test, y_train, y_test = prepare_data(df)
    model, scaler = train_logistic_regression(X_train, y_train)

    X_test_scaled = scaler.transform(X_test)
    predictions = model.predict(X_test_scaled)

    spllit_idx = int(len(df_clean) * 0.8)
    test_rows = df_clean.iloc[spllit_idx:].copy()

    test_rows["predicted_result"] = predictions
    test_rows["actual_result"] = y_test.values
    test_rows["correct"] = test_rows["predicted_result"] == test_rows["actual_result"]

    output_columns = [
        "date",
        "season",
        "matchday",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "actual_result",
        "predicted_result",
        "correct",
    ]

    output = test_rows[output_columns]
    output.to_csv("data/processed/model_predictions.csv", index=False)

    accuracy = output["correct"].mean()
    print(f"Exported {len(output)} predictions. Test accuracy: {accuracy:.3f}")
    print(output.head(10))

    return output

if __name__ == "__main__":
    export_predictions()