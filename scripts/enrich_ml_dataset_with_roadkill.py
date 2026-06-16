from pathlib import Path
import math

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

ML_PATH = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_wildlife_metadata_with_gps.csv"
ROADKILL_PATH = BASE_DIR / "data" / "external" / "roadkill" / "roadkill_2019_2025_combined.csv"
OUT_PATH = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_wildlife_metadata_enriched.csv"


def read_csv_safely(path: Path) -> pd.DataFrame:
    for enc in ["utf-8-sig", "cp949", "euc-kr", "utf-8"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue

    raise ValueError(f"CSV 파일을 읽을 수 없습니다: {path}")


def haversine_km(lat1, lon1, lat2_arr, lon2_arr):
    """
    한 관측 지점과 여러 로드킬 지점 사이의 거리를 km 단위로 계산한다.
    """
    earth_radius_km = 6371.0

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = np.radians(lat2_arr)
    lon2_rad = np.radians(lon2_arr)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        np.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))
    return earth_radius_km * c


def make_roadkill_features(row, rk_lat, rk_lon, rk_cases):
    lat = row["latitude"]
    lon = row["longitude"]

    if pd.isna(lat) or pd.isna(lon):
        return pd.Series(
            {
                "nearest_roadkill_distance_km": np.nan,
                "roadkill_count_within_5km": 0,
                "roadkill_count_within_10km": 0,
                "roadkill_count_within_20km": 0,
                "roadkill_max_cases_nearby": 0,
                "roadkill_weighted_score": 0.0,
                "near_roadkill_hotspot": 0,
            }
        )

    distances = haversine_km(float(lat), float(lon), rk_lat, rk_lon)

    within_5 = distances <= 5
    within_10 = distances <= 10
    within_20 = distances <= 20

    nearest_distance = float(np.min(distances))

    count_5 = int(rk_cases[within_5].sum())
    count_10 = int(rk_cases[within_10].sum())
    count_20 = int(rk_cases[within_20].sum())

    if within_20.any():
        max_cases_nearby = int(rk_cases[within_20].max())
    else:
        max_cases_nearby = 0

    # 가까운 로드킬 지점일수록 더 큰 영향을 주는 점수
    weighted_score = float(np.sum(rk_cases / (distances + 1.0)))

    near_hotspot = 1 if count_10 > 0 else 0

    return pd.Series(
        {
            "nearest_roadkill_distance_km": round(nearest_distance, 3),
            "roadkill_count_within_5km": count_5,
            "roadkill_count_within_10km": count_10,
            "roadkill_count_within_20km": count_20,
            "roadkill_max_cases_nearby": max_cases_nearby,
            "roadkill_weighted_score": round(weighted_score, 3),
            "near_roadkill_hotspot": near_hotspot,
        }
    )


def add_roadkill_score(row):
    """
    기존 risk_score에 로드킬 다발 구간 위험도를 보정한다.
    """
    base_score = float(row["risk_score"])
    extra = 0

    nearest = row["nearest_roadkill_distance_km"]
    count_10 = row["roadkill_count_within_10km"]
    count_20 = row["roadkill_count_within_20km"]
    weighted = row["roadkill_weighted_score"]

    if pd.notna(nearest):
        if nearest <= 5:
            extra += 6
        elif nearest <= 10:
            extra += 4
        elif nearest <= 20:
            extra += 2

    if count_10 >= 20:
        extra += 5
    elif count_10 >= 10:
        extra += 3
    elif count_10 > 0:
        extra += 1

    if count_20 >= 40:
        extra += 3
    elif count_20 >= 20:
        extra += 2

    if weighted >= 20:
        extra += 4
    elif weighted >= 10:
        extra += 2

    return min(round(base_score + extra, 2), 100)


def make_grade(score):
    if score >= 70:
        return "high"
    if score >= 45:
        return "medium"
    return "low"


def main():
    print("[INFO] Load ML dataset")
    ml_df = read_csv_safely(ML_PATH)

    print("[INFO] Load roadkill dataset")
    rk_df = read_csv_safely(ROADKILL_PATH)

    required_ml_cols = {"latitude", "longitude", "risk_score"}
    missing_ml_cols = required_ml_cols - set(ml_df.columns)
    if missing_ml_cols:
        raise ValueError(f"ML CSV에 필요한 컬럼이 없습니다: {missing_ml_cols}")

    required_rk_cols = {"위도", "경도", "발생건수"}
    missing_rk_cols = required_rk_cols - set(rk_df.columns)
    if missing_rk_cols:
        raise ValueError(f"로드킬 CSV에 필요한 컬럼이 없습니다: {missing_rk_cols}")

    ml_df["latitude"] = pd.to_numeric(ml_df["latitude"], errors="coerce")
    ml_df["longitude"] = pd.to_numeric(ml_df["longitude"], errors="coerce")

    rk_df["위도"] = pd.to_numeric(rk_df["위도"], errors="coerce")
    rk_df["경도"] = pd.to_numeric(rk_df["경도"], errors="coerce")
    rk_df["발생건수"] = pd.to_numeric(rk_df["발생건수"], errors="coerce").fillna(0)

    rk_df = rk_df.dropna(subset=["위도", "경도"])

    rk_lat = rk_df["위도"].to_numpy()
    rk_lon = rk_df["경도"].to_numpy()
    rk_cases = rk_df["발생건수"].to_numpy()

    print("[INFO] Build roadkill features")
    roadkill_features = ml_df.apply(
        make_roadkill_features,
        axis=1,
        rk_lat=rk_lat,
        rk_lon=rk_lon,
        rk_cases=rk_cases,
    )

    enriched_df = pd.concat([ml_df, roadkill_features], axis=1)

    print("[INFO] Update risk_score with roadkill features")
    enriched_df["risk_score_base"] = enriched_df["risk_score"]
    enriched_df["risk_score"] = enriched_df.apply(add_roadkill_score, axis=1)
    enriched_df["risk_grade"] = enriched_df["risk_score"].apply(make_grade)
    enriched_df["risk_level"] = enriched_df["risk_grade"]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    enriched_df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    print("[DONE] Saved:", OUT_PATH)
    print("[INFO] Shape:", enriched_df.shape)

    print("\n[INFO] Risk grade distribution")
    print(enriched_df["risk_grade"].value_counts())

    print("\n[INFO] Roadkill feature summary")
    print(
        enriched_df[
            [
                "nearest_roadkill_distance_km",
                "roadkill_count_within_5km",
                "roadkill_count_within_10km",
                "roadkill_count_within_20km",
                "roadkill_weighted_score",
                "near_roadkill_hotspot",
            ]
        ].describe()
    )


if __name__ == "__main__":
    main()