from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "ml" / "area_risk_model.pkl"


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


def get_risk_message(risk_grade: str, region_name: str, location: str, main_species: str) -> str:
    display_region = region_name or location

    if risk_grade == "high":
        return (
            f"{display_region} 주변은 현재 조건에서 야생동물 출몰 위험이 높게 예측됩니다. "
            f"특히 {main_species} 출현 가능성에 주의하고, 야간 이동이나 단독 접근은 피하는 것이 좋습니다."
        )

    if risk_grade == "medium":
        return (
            f"{display_region} 주변은 현재 조건에서 야생동물 출몰 위험이 보통 수준으로 예측됩니다. "
            f"반복 출현 여부를 확인하고 주변 환경을 주의 깊게 살펴보세요."
        )

    return (
        f"{display_region} 주변은 현재 조건에서 야생동물 출몰 위험이 낮게 예측됩니다. "
        f"다만 야생동물이 반복적으로 관측되는 경우 위험도가 달라질 수 있습니다."
    )


def get_actions(risk_grade: str) -> list[str]:
    if risk_grade == "high":
        return [
            "야간 이동이나 단독 접근을 피하세요.",
            "농장, 창고, 울타리, 음식물 보관 장소를 점검하세요.",
            "야생동물을 발견하면 가까이 가지 말고 안전한 곳으로 이동하세요.",
            "반복 출현하거나 위협이 느껴지면 관계 기관에 신고하세요.",
        ]

    if risk_grade == "medium":
        return [
            "주변을 주의 깊게 살피고 이동 경로를 확인하세요.",
            "같은 장소에 반복해서 나타나는지 기록해두세요.",
            "농작물이나 시설물 피해 가능성이 있는지 확인하세요.",
        ]

    return [
        "즉각적인 위험은 낮지만 관측 기록을 유지하세요.",
        "야생동물에게 일부러 접근하지 마세요.",
        "날씨나 시간대가 바뀌면 위험도가 달라질 수 있습니다.",
    ]


def load_model_artifact():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"모델 파일이 없습니다: {MODEL_PATH}. "
            f"python scripts\\create_area_risk_dataset.py 실행 후 "
            f"python scripts\\train_area_risk_model.py 를 실행하세요."
        )

    return joblib.load(MODEL_PATH)


def normalize_input(input_data: dict) -> dict:
    location = input_data.get("location") or input_data.get("area_type") or "unknown"

    return {
        "region_name": str(input_data.get("region_name", "")).strip(),
        "location": str(location).strip(),
        "weather": str(input_data.get("weather", "unknown")).strip(),
        "time_zone": str(input_data.get("time_zone", "unknown")).strip(),
        "season": str(input_data.get("season", "unknown")).strip(),
    }


def records_to_df(records: list[dict]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


def select_profile(input_data: dict, profiles_df: pd.DataFrame) -> dict:
    if profiles_df.empty:
        return {
            "historical_count": 0,
            "species_diversity": 0,
            "avg_object_count": 0,
            "avg_max_bbox_area_ratio": 0,
            "avg_avg_bbox_area_ratio": 0,
            "main_risk_species": "unknown",
        }

    location = input_data["location"]
    weather = input_data["weather"]
    time_zone = input_data["time_zone"]
    season = input_data["season"]

    exact = profiles_df[
        (profiles_df["location"] == location)
        & (profiles_df["weather"] == weather)
        & (profiles_df["time_zone"] == time_zone)
        & (profiles_df["season"] == season)
    ]

    if not exact.empty:
        return exact.sort_values("historical_count", ascending=False).iloc[0].to_dict()

    location_time = profiles_df[
        (profiles_df["location"] == location)
        & (profiles_df["time_zone"] == time_zone)
    ]

    if not location_time.empty:
        return make_fallback_profile(location_time, input_data)

    location_only = profiles_df[profiles_df["location"] == location]

    if not location_only.empty:
        return make_fallback_profile(location_only, input_data)

    return make_fallback_profile(profiles_df, input_data)


def get_mode_value(series: pd.Series) -> str:
    values = series.dropna().astype(str)

    if values.empty:
        return "unknown"

    mode_values = values.mode()

    if mode_values.empty:
        return values.iloc[0]

    return mode_values.iloc[0]


def make_fallback_profile(df: pd.DataFrame, input_data: dict) -> dict:
    return {
        "location": input_data["location"],
        "weather": input_data["weather"],
        "time_zone": input_data["time_zone"],
        "season": input_data["season"],
        "historical_count": int(df["historical_count"].sum()),
        "species_diversity": int(df["main_risk_species"].nunique()),
        "avg_object_count": float(df["avg_object_count"].mean()),
        "avg_max_bbox_area_ratio": float(df["avg_max_bbox_area_ratio"].mean()),
        "avg_avg_bbox_area_ratio": float(df["avg_avg_bbox_area_ratio"].mean()),
        "main_risk_species": get_mode_value(df["main_risk_species"]),
    }


def make_feature_row(input_data: dict, profile: dict) -> pd.DataFrame:
    row = {
        "location": input_data["location"],
        "weather": input_data["weather"],
        "time_zone": input_data["time_zone"],
        "season": input_data["season"],
        "main_risk_species": profile.get("main_risk_species", "unknown"),
        "historical_count": profile.get("historical_count", 0),
        "species_diversity": profile.get("species_diversity", 0),
        "avg_object_count": profile.get("avg_object_count", 0),
        "avg_max_bbox_area_ratio": profile.get("avg_max_bbox_area_ratio", 0),
        "avg_avg_bbox_area_ratio": profile.get("avg_avg_bbox_area_ratio", 0),
    }

    return pd.DataFrame([row])


def predict_risk(input_data: dict) -> dict:
    artifact = load_model_artifact()
    normalized_input = normalize_input(input_data)

    profiles_df = records_to_df(artifact.get("area_profiles", []))
    profile = select_profile(normalized_input, profiles_df)

    feature_df = make_feature_row(normalized_input, profile)

    model = artifact["model"]
    predicted_score = float(model.predict(feature_df)[0])
    predicted_score = max(0, min(100, predicted_score))
    predicted_score = round(predicted_score, 2)

    risk_grade = score_to_grade(predicted_score)
    main_species = profile.get("main_risk_species", "unknown")

    metrics = artifact.get("metrics", {})

    return {
        "predicted_score": predicted_score,
        "risk_score": predicted_score,
        "risk_grade": risk_grade,
        "risk_level": risk_grade,
        "risk_grade_korean": grade_to_korean(risk_grade),
        "model_type": artifact.get("model_type", "area_risk_regression"),
        "region_name": normalized_input["region_name"],
        "location": normalized_input["location"],
        "weather": normalized_input["weather"],
        "time_zone": normalized_input["time_zone"],
        "season": normalized_input["season"],
        "main_risk_species": main_species,
        "historical_count": int(profile.get("historical_count", 0)),
        "message": get_risk_message(
            risk_grade,
            normalized_input["region_name"],
            normalized_input["location"],
            main_species,
        ),
        "actions": get_actions(risk_grade),
        "metrics": {
            "mae": round(float(metrics.get("mae", 0)), 4),
            "rmse": round(float(metrics.get("rmse", 0)), 4),
            "r2": round(float(metrics.get("r2", 0)), 4),
        },
        "input": normalized_input,
        "profile": {
            "historical_count": int(profile.get("historical_count", 0)),
            "species_diversity": int(profile.get("species_diversity", 0)),
            "avg_object_count": round(float(profile.get("avg_object_count", 0)), 2),
            "avg_max_bbox_area_ratio": round(float(profile.get("avg_max_bbox_area_ratio", 0)), 6),
            "avg_avg_bbox_area_ratio": round(float(profile.get("avg_avg_bbox_area_ratio", 0)), 6),
        },
    }