from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "ml" / "risk_regression_model.pkl"


def score_to_grade(score: float) -> str:
    if score < 45:
        return "low"
    if score < 70:
        return "medium"
    return "high"


def get_risk_message(risk_grade: str) -> str:
    if risk_grade == "high":
        return "위험 점수가 높습니다. 야생동물 근접 출현 가능성이 있으므로 현장 접근을 주의하고 주변 시설물을 점검하세요."

    if risk_grade == "medium":
        return "중간 수준의 위험입니다. 출현 조건을 확인하고 반복 관측 여부를 모니터링하세요."

    return "낮은 수준의 위험입니다. 즉각적인 대응보다는 관측 기록을 유지하는 것이 좋습니다."


def load_model_artifact():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"모델 파일이 없습니다: {MODEL_PATH}")

    artifact = joblib.load(MODEL_PATH)

    if isinstance(artifact, dict):
        return artifact

    # 혹시 예전 방식처럼 모델만 저장된 경우를 대비
    return {
        "model": artifact,
        "model_type": "regression",
        "metrics": {},
        "feature_cols": [
            "day",
            "camera_type",
            "weather",
            "location",
            "time_zone",
            "season",
            "species",
            "object_count",
            "max_bbox_area_ratio",
            "avg_bbox_area_ratio",
        ],
    }


def normalize_input(input_data: dict, feature_cols: list) -> pd.DataFrame:
    row = {}

    default_values = {
        "day": "unknown",
        "camera_type": "unknown",
        "weather": "unknown",
        "location": "unknown",
        "time_zone": "unknown",
        "season": "unknown",
        "species": "unknown",
        "object_count": 1,
        "max_bbox_area_ratio": 0,
        "avg_bbox_area_ratio": 0,
    }

    for col in feature_cols:
        row[col] = input_data.get(col, default_values.get(col, "unknown"))

    numeric_cols = [
        "object_count",
        "max_bbox_area_ratio",
        "avg_bbox_area_ratio",
    ]

    for col in numeric_cols:
        if col in row:
            try:
                row[col] = float(row[col])
            except (TypeError, ValueError):
                row[col] = 0

    return pd.DataFrame([row])


def predict_risk(input_data: dict) -> dict:
    artifact = load_model_artifact()

    model = artifact["model"]
    feature_cols = artifact.get(
        "feature_cols",
        [
            "day",
            "camera_type",
            "weather",
            "location",
            "time_zone",
            "season",
            "species",
            "object_count",
            "max_bbox_area_ratio",
            "avg_bbox_area_ratio",
        ],
    )

    input_df = normalize_input(input_data, feature_cols)

    predicted_score = float(model.predict(input_df)[0])
    predicted_score = max(0, min(100, predicted_score))
    predicted_score = round(predicted_score, 2)

    risk_grade = score_to_grade(predicted_score)
    metrics = artifact.get("metrics", {})

    return {
        "predicted_score": predicted_score,
        "risk_score": predicted_score,
        "risk_grade": risk_grade,
        "risk_level": risk_grade,
        "model_type": artifact.get("model_type", "regression"),
        "message": get_risk_message(risk_grade),
        "metrics": {
            "mae": round(float(metrics.get("mae", 0)), 4),
            "rmse": round(float(metrics.get("rmse", 0)), 4),
            "r2": round(float(metrics.get("r2", 0)), 4),
        },
        "input": input_data,
    }