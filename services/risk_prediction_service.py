from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "ml" / "risk_regression_model.pkl"


CATEGORICAL_FEATURES = [
    "day",
    "camera_type",
    "weather",
    "location",
    "time_zone",
    "season",
    "species",
]

NUMERIC_FEATURES = [
    "object_count",
    "max_bbox_area_ratio",
    "avg_bbox_area_ratio",
    "nearest_roadkill_distance_km",
    "roadkill_count_within_5km",
    "roadkill_count_within_10km",
    "roadkill_count_within_20km",
    "roadkill_max_cases_nearby",
    "roadkill_weighted_score",
    "near_roadkill_hotspot",
]

MODEL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES


REQUIRED_FIELDS = [
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
]


DEFAULT_ROADKILL_FEATURES = {
    "nearest_roadkill_distance_km": 13.516,
    "roadkill_count_within_5km": 0,
    "roadkill_count_within_10km": 0,
    "roadkill_count_within_20km": 4,
    "roadkill_max_cases_nearby": 4,
    "roadkill_weighted_score": 17.447,
    "near_roadkill_hotspot": 0,
}


_model = None


def load_model():
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {MODEL_PATH}")

        loaded = joblib.load(MODEL_PATH)

        if isinstance(loaded, dict):
            _model = loaded["model"]
        else:
            _model = loaded

    return _model


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def score_to_grade(score: float) -> str:
    if score < 45:
        return "low"
    if score < 70:
        return "medium"
    return "high"


def grade_to_korean(risk_grade: str) -> str:
    if risk_grade == "high":
        return "높음"
    if risk_grade == "medium":
        return "보통"
    return "낮음"


def make_action_message(risk_grade: str) -> str:
    if risk_grade == "high":
        return "위험 수준이 높습니다. 현장 접근을 주의하고 주변 시설물과 농작물 피해 여부를 점검하세요."

    if risk_grade == "medium":
        return "중간 수준의 위험입니다. 반복 출현 여부를 모니터링하고 필요 시 현장 확인을 진행하세요."

    return "위험 수준이 낮습니다. 일반적인 관찰 상태를 유지하세요."


def make_risk_reasons(input_data: dict) -> list[str]:
    reasons = []

    if input_data.get("time_zone") == "night" or input_data.get("day") == "night":
        reasons.append("야간 시간대 관측으로 인해 위험도가 상승했습니다.")

    species = input_data.get("species")
    if species in ["멧돼지", "반달가슴곰"]:
        reasons.append(f"{species}는 현장 접근 시 주의가 필요한 종입니다.")

    object_count = to_int(input_data.get("object_count"))
    if object_count >= 3:
        reasons.append("동시에 관측된 객체 수가 많아 위험도가 상승했습니다.")

    max_bbox_area_ratio = to_float(input_data.get("max_bbox_area_ratio"))
    if max_bbox_area_ratio >= 0.05:
        reasons.append("객체가 화면에서 차지하는 비율이 높아 근접 관측 가능성이 있습니다.")

    nearest_roadkill_distance = to_float(input_data.get("nearest_roadkill_distance_km"), default=9999)
    roadkill_count_10km = to_int(input_data.get("roadkill_count_within_10km"))
    roadkill_weighted_score = to_float(input_data.get("roadkill_weighted_score"))

    if nearest_roadkill_distance <= 10:
        reasons.append("관측 지점 주변 10km 이내에 로드킬 다발 구간이 존재합니다.")
    elif nearest_roadkill_distance <= 20:
        reasons.append("관측 지점 주변 20km 이내에 로드킬 다발 구간이 존재합니다.")

    if roadkill_count_10km > 0:
        reasons.append("주변 로드킬 발생건수가 위험도 산정에 반영되었습니다.")

    if roadkill_weighted_score >= 10:
        reasons.append("가까운 로드킬 다발 구간의 발생건수가 위험도 산정에 반영되었습니다.")

    if not reasons:
        reasons.append("입력된 관측 조건을 기준으로 위험도를 산정했습니다.")

    return reasons


def validate_input(input_data: dict):
    missing_fields = []

    for field in REQUIRED_FIELDS:
        value = input_data.get(field)
        if value is None or value == "":
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(f"필수 입력값이 누락되었습니다: {missing_fields}")


def build_model_input(input_data: dict) -> pd.DataFrame:
    validate_input(input_data)

    row = {
        "day": input_data.get("day"),
        "camera_type": input_data.get("camera_type"),
        "weather": input_data.get("weather"),
        "location": input_data.get("location"),
        "time_zone": input_data.get("time_zone"),
        "season": input_data.get("season"),
        "species": input_data.get("species"),
        "object_count": to_int(input_data.get("object_count")),
        "max_bbox_area_ratio": to_float(input_data.get("max_bbox_area_ratio")),
        "avg_bbox_area_ratio": to_float(input_data.get("avg_bbox_area_ratio")),
    }

    for key, default_value in DEFAULT_ROADKILL_FEATURES.items():
        row[key] = input_data.get(key, default_value)

    for key in NUMERIC_FEATURES:
        row[key] = to_float(row.get(key), default=0.0)

    return pd.DataFrame([row], columns=MODEL_FEATURES)


def predict_risk(input_data: dict) -> dict:
    model = load_model()
    model_input = build_model_input(input_data)

    predicted_score = float(model.predict(model_input)[0])
    predicted_score = round(max(0, min(predicted_score, 100)), 2)

    predicted_grade = score_to_grade(predicted_score)
    full_input = model_input.iloc[0].to_dict()

    return {
        "predicted_score": predicted_score,
        "predicted_grade": predicted_grade,
        "predicted_grade_ko": grade_to_korean(predicted_grade),
        "risk_reasons": make_risk_reasons(full_input),
        "action_message": make_action_message(predicted_grade),
        "message": make_action_message(predicted_grade),
        "roadkill_features": {
            "nearest_roadkill_distance_km": full_input["nearest_roadkill_distance_km"],
            "roadkill_count_within_5km": full_input["roadkill_count_within_5km"],
            "roadkill_count_within_10km": full_input["roadkill_count_within_10km"],
            "roadkill_count_within_20km": full_input["roadkill_count_within_20km"],
            "roadkill_weighted_score": full_input["roadkill_weighted_score"],
            "near_roadkill_hotspot": full_input["near_roadkill_hotspot"],
        },
    }


def predict(input_data: dict) -> dict:
    return predict_risk(input_data)


def predict_risk_score(input_data: dict) -> dict:
    return predict_risk(input_data)
