from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_wildlife_metadata.csv"
OUTPUT_PATH = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_area_risk_dataset.csv"


def score_to_grade(score: float) -> str:
    if score < 45:
        return "low"
    if score < 70:
        return "medium"
    return "high"


def get_main_species(series: pd.Series) -> str:
    values = series.dropna().astype(str)

    if values.empty:
        return "unknown"

    mode_values = values.mode()

    if mode_values.empty:
        return values.iloc[0]

    return mode_values.iloc[0]


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"입력 CSV가 없습니다: {INPUT_PATH}")

    print("[INFO] Load metadata CSV")
    df = pd.read_csv(INPUT_PATH)

    required_cols = [
        "location",
        "weather",
        "time_zone",
        "season",
        "species",
        "object_count",
        "max_bbox_area_ratio",
        "avg_bbox_area_ratio",
        "risk_score",
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"필수 컬럼이 없습니다: {missing_cols}")

    print("[INFO] Clean columns")

    categorical_cols = [
        "location",
        "weather",
        "time_zone",
        "season",
        "species",
    ]

    for col in categorical_cols:
        df[col] = df[col].fillna("unknown").astype(str).str.strip()
        df[col] = df[col].replace("", "unknown")

    numeric_cols = [
        "object_count",
        "max_bbox_area_ratio",
        "avg_bbox_area_ratio",
        "risk_score",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    group_cols = [
        "location",
        "weather",
        "time_zone",
        "season",
    ]

    print("[INFO] Create area risk dataset")

    agg_df = (
        df.groupby(group_cols)
        .agg(
            historical_count=("species", "count"),
            species_diversity=("species", "nunique"),
            avg_object_count=("object_count", "mean"),
            avg_max_bbox_area_ratio=("max_bbox_area_ratio", "mean"),
            avg_avg_bbox_area_ratio=("avg_bbox_area_ratio", "mean"),
            area_risk_score=("risk_score", "mean"),
        )
        .reset_index()
    )

    main_species_df = (
        df.groupby(group_cols)["species"]
        .agg(get_main_species)
        .reset_index()
        .rename(columns={"species": "main_risk_species"})
    )

    area_df = agg_df.merge(main_species_df, on=group_cols, how="left")

    area_df["area_risk_score"] = area_df["area_risk_score"].clip(0, 100).round(2)
    area_df["avg_object_count"] = area_df["avg_object_count"].round(2)
    area_df["avg_max_bbox_area_ratio"] = area_df["avg_max_bbox_area_ratio"].round(6)
    area_df["avg_avg_bbox_area_ratio"] = area_df["avg_avg_bbox_area_ratio"].round(6)

    area_df["risk_grade"] = area_df["area_risk_score"].apply(score_to_grade)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    area_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("[INFO] Saved:", OUTPUT_PATH)
    print("[INFO] Shape:", area_df.shape)

    print("\n[INFO] Risk grade distribution")
    print(area_df["risk_grade"].value_counts())

    print("\n[INFO] Main species distribution")
    print(area_df["main_risk_species"].value_counts())

    print("\n[INFO] Preview")
    print(area_df.head())


if __name__ == "__main__":
    main()