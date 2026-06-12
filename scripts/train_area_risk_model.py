from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_area_risk_dataset.csv"
MODEL_PATH = BASE_DIR / "models" / "ml" / "area_risk_model.pkl"


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"지역 기반 데이터셋이 없습니다: {DATA_PATH}")

    print("[INFO] Load area risk dataset")
    df = pd.read_csv(DATA_PATH)

    target_col = "area_risk_score"

    categorical_features = [
        "location",
        "weather",
        "time_zone",
        "season",
        "main_risk_species",
    ]

    numeric_features = [
        "historical_count",
        "species_diversity",
        "avg_object_count",
        "avg_max_bbox_area_ratio",
        "avg_avg_bbox_area_ratio",
    ]

    feature_cols = categorical_features + numeric_features

    missing_cols = [
        col for col in feature_cols + [target_col]
        if col not in df.columns
    ]

    if missing_cols:
        raise ValueError(f"필수 컬럼이 없습니다: {missing_cols}")

    for col in categorical_features:
        df[col] = df[col].fillna("unknown").astype(str)

    for col in numeric_features + [target_col]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    X = df[feature_cols]
    y = df[target_col]

    test_size = 0.2 if len(df) >= 10 else 0.3

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=42,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            (
                "num",
                "passthrough",
                numeric_features,
            ),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=500,
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    print("[INFO] Train area risk regression model")
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds) ** 0.5
    r2 = r2_score(y_test, preds)

    print("[RESULT] MAE:", round(mae, 4))
    print("[RESULT] RMSE:", round(rmse, 4))
    print("[RESULT] R2 Score:", round(r2, 4))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": pipeline,
        "model_type": "area_risk_regression",
        "feature_cols": feature_cols,
        "categorical_features": categorical_features,
        "numeric_features": numeric_features,
        "target_col": target_col,
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
        },
        "area_profiles": df.to_dict(orient="records"),
    }

    joblib.dump(artifact, MODEL_PATH)

    print("[INFO] Saved model:", MODEL_PATH)
    print("[INFO] Area profile count:", len(df))


if __name__ == "__main__":
    main()