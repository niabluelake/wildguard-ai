from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "ml" / "seoul_boar_risk_model.pkl"
STATS_PATH = BASE_DIR / "models" / "ml" / "seoul_boar_stats.pkl"


def get_season(month: int) -> str:
    if month in [3, 4, 5]:
        return "spring"
    if month in [6, 7, 8]:
        return "summer"
    if month in [9, 10, 11]:
        return "fall"
    return "winter"


def get_korean_season(season: str) -> str:
    season_map = {
        "spring": "봄",
        "summer": "여름",
        "fall": "가을",
        "winter": "겨울",
    }
    return season_map.get(season, season)


def get_risk_message(risk_level: str) -> str:
    if risk_level == "high":
        return "해당 자치구와 월 조건에서는 과거 멧돼지 출현 신고가 많은 편입니다. 산림 인근, 하천 주변, 야간 이동에 주의하세요."
    if risk_level == "medium":
        return "해당 조건에서는 멧돼지 출현 가능성이 보통 수준입니다. 야외 이동 시 주변을 확인하고 단독 접근은 피하는 것이 좋습니다."
    return "해당 조건에서는 과거 멧돼지 출현 신고가 적은 편입니다. 다만 야생동물 출현 가능성은 있으므로 기본적인 주의는 필요합니다."


def find_value(df, filters, column_name, default_value=0):
    result = df.copy()

    for key, value in filters.items():
        result = result[result[key] == value]

    if result.empty:
        return default_value

    return result.iloc[0][column_name]


def predict_risk(input_data: dict) -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"모델 파일이 없습니다: {MODEL_PATH}")

    if not STATS_PATH.exists():
        raise FileNotFoundError(f"통계 파일이 없습니다: {STATS_PATH}")

    model = joblib.load(MODEL_PATH)
    stats = joblib.load(STATS_PATH)

    district = input_data.get("district")
    month = int(input_data.get("month"))
    year = int(input_data.get("year", stats["latest_year"]))

    season = get_season(month)

    district_stats = stats["district_stats"]
    month_stats = stats["month_stats"]
    district_month_stats = stats["district_month_stats"]

    district_total_count = find_value(
        district_stats,
        {"자치구": district},
        "district_total_count",
    )

    district_avg_count = find_value(
        district_stats,
        {"자치구": district},
        "district_avg_count",
    )

    district_total_capture = find_value(
        district_stats,
        {"자치구": district},
        "district_total_capture",
    )

    month_avg_count = find_value(
        month_stats,
        {"월": month},
        "month_avg_count",
    )

    district_month_avg_count = find_value(
        district_month_stats,
        {"자치구": district, "월": month},
        "district_month_avg_count",
    )

    input_df = pd.DataFrame([{
        "연도": year,
        "자치구": district,
        "월": month,
        "계절": season,
        "district_total_count": district_total_count,
        "district_avg_count": district_avg_count,
        "month_avg_count": month_avg_count,
        "district_month_avg_count": district_month_avg_count,
        "district_total_capture": district_total_capture,
    }])

    risk_level = model.predict(input_df)[0]
    message = get_risk_message(risk_level)

    return {
        "risk_level": risk_level,
        "message": message,
        "input": {
            "district": district,
            "month": month,
            "year": year,
            "season": get_korean_season(season),
        },
        "stats": {
            "district_total_count": int(district_total_count),
            "district_avg_count": round(float(district_avg_count), 2),
            "month_avg_count": round(float(month_avg_count), 2),
            "district_month_avg_count": round(float(district_month_avg_count), 2),
            "district_total_capture": int(district_total_capture),
        }
    }