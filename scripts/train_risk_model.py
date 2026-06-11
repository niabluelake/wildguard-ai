from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_wildlife_metadata.csv"
MODEL_PATH = BASE_DIR / "models" / "ml" / "risk_regression_model.pkl"


def score_to_grade(score):
    if score < 45:
        return "low"
    if score < 70:
        return "medium"
    return "high"


def main():
    print("[INFO] Load dataset")
    df = pd.read_csv(DATA_PATH)

    target_col = "risk_score"

    categorical_features = [
        "day",
        "camera_type",
        "weather",
        "location",
        "time_zone",
        "season",
        "species",
    ]

    numeric_features = [
        "object_count",
        "max_bbox_area_ratio",
        "avg_bbox_area_ratio",
    ]

    feature_cols = categorical_features + numeric_features

    required_cols = feature_cols + [target_col]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"필수 컬럼이 없습니다: {missing_cols}")

    df = df.dropna(subset=[target_col])

    X = df[feature_cols].copy()
    y = df[target_col].copy()

    for col in categorical_features:
        X[col] = X[col].fillna("unknown").astype(str)

    for col in numeric_features:
        X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=None,
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    print("[INFO] Train regression model")
    pipeline.fit(X_train, y_train)

    print("[INFO] Evaluate model")
    y_pred = pipeline.predict(X_test)
    y_pred = np.clip(y_pred, 0, 100)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2 Score: {r2:.4f}")
    print()

    sample_result = pd.DataFrame({
        "actual_score": y_test.head(10).values,
        "predicted_score": y_pred[:10],
    })

    sample_result["actual_grade"] = sample_result["actual_score"].apply(score_to_grade)
    sample_result["predicted_grade"] = sample_result["predicted_score"].apply(score_to_grade)

    print("[INFO] Sample predictions")
    print(sample_result)
    print()

    artifact = {
        "model": pipeline,
        "model_type": "regression",
        "target_col": target_col,
        "feature_cols": feature_cols,
        "categorical_features": categorical_features,
        "numeric_features": numeric_features,
        "metrics": {
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
        },
        "grade_rule": {
            "low": "0 <= score < 45",
            "medium": "45 <= score < 70",
            "high": "70 <= score <= 100",
        },
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)

    print(f"[INFO] Save model: {MODEL_PATH}")


if __name__ == "__main__":
    main()