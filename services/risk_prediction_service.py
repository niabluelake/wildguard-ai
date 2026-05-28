from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "ml" / "risk_model.pkl"


FEATURE_COLUMNS = [
    "day",
    "camera_type",
    "weather",
    "location",
    "time_zone",
    "season",
    "object_count",
    "max_bbox_area_ratio",
    "avg_bbox_area_ratio",
]


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"모델 파일이 없습니다: {MODEL_PATH}")

    return joblib.load(MODEL_PATH)


def get_risk_message(risk_level):
    messages = {
        "low": "현재 조건에서는 야생동물 출현 위험이 낮은 편입니다. 주변 상황을 계속 확인하세요.",
        "medium": "야생동물 출현 가능성이 있어 주의가 필요합니다. 직접 접근하지 말고 주변을 확인하세요.",
        "high": "위험도가 높습니다. 야생동물에게 접근하지 말고 안전한 장소로 이동한 뒤 필요 시 관계 기관에 신고하세요.",
    }

    return messages.get(risk_level, "위험도 판단 결과를 확인할 수 없습니다.")


def validate_input(data):
    missing = [col for col in FEATURE_COLUMNS if col not in data]

    if missing:
        raise ValueError(f"필수 입력값이 없습니다: {missing}")

    return True


def predict_risk(data):
    validate_input(data)

    model = load_model()

    input_df = pd.DataFrame([{
        "day": data["day"],
        "camera_type": data["camera_type"],
        "weather": data["weather"],
        "location": data["location"],
        "time_zone": data["time_zone"],
        "season": data["season"],
        "object_count": int(data["object_count"]),
        "max_bbox_area_ratio": float(data["max_bbox_area_ratio"]),
        "avg_bbox_area_ratio": float(data["avg_bbox_area_ratio"]),
    }])

    risk_level = model.predict(input_df)[0]
    message = get_risk_message(risk_level)

    return {
        "risk_level": risk_level,
        "message": message,
        "input": input_df.iloc[0].to_dict(),
    }