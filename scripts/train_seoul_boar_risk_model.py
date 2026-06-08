from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "seoul_wildlife" / "seoul_boar_reports.csv"
MODEL_DIR = BASE_DIR / "models" / "ml"
MODEL_PATH = MODEL_DIR / "seoul_boar_risk_model.pkl"
STATS_PATH = MODEL_DIR / "seoul_boar_stats.pkl"

FEATURES = [
    "연도",
    "자치구",
    "월",
    "계절",
    "district_total_count",
    "district_avg_count",
    "month_avg_count",
    "district_month_avg_count",
    "district_total_capture",
]

TARGET = "risk_level"


def get_season(month: int) -> str:
    if month in [3, 4, 5]:
        return "spring"
    if month in [6, 7, 8]:
        return "summer"
    if month in [9, 10, 11]:
        return "fall"
    return "winter"


def make_risk_level(count: int) -> str:
    if count <= 0:
        return "low"
    if count <= 1:
        return "medium"
    return "high"


def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"학습 데이터가 없습니다: {DATA_PATH}")

    try:
        df = pd.read_csv(DATA_PATH, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

    required_columns = ["연도", "자치구", "월", "출현개체수", "포획개체수"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"필수 컬럼이 없습니다: {missing_columns}")

    df = df.copy()

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)
    df["출현개체수"] = df["출현개체수"].fillna(0).astype(int)
    df["포획개체수"] = df["포획개체수"].fillna(0).astype(int)

    df["계절"] = df["월"].apply(get_season)
    df["risk_level"] = df["출현개체수"].apply(make_risk_level)

    district_stats = df.groupby("자치구").agg(
        district_total_count=("출현개체수", "sum"),
        district_avg_count=("출현개체수", "mean"),
        district_total_capture=("포획개체수", "sum"),
    ).reset_index()

    month_stats = df.groupby("월").agg(
        month_avg_count=("출현개체수", "mean"),
    ).reset_index()

    district_month_stats = df.groupby(["자치구", "월"]).agg(
        district_month_avg_count=("출현개체수", "mean"),
    ).reset_index()

    df = df.merge(district_stats, on="자치구", how="left")
    df = df.merge(month_stats, on="월", how="left")
    df = df.merge(district_month_stats, on=["자치구", "월"], how="left")

    stats = {
        "district_stats": district_stats,
        "month_stats": month_stats,
        "district_month_stats": district_month_stats,
        "district_list": sorted(df["자치구"].unique().tolist()),
        "latest_year": int(df["연도"].max()),
    }

    return df, stats


def train_model():
    df, stats = load_dataset()

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["자치구", "계절"]),
            (
                "num",
                "passthrough",
                [
                    "연도",
                    "월",
                    "district_total_count",
                    "district_avg_count",
                    "month_avg_count",
                    "district_month_avg_count",
                    "district_total_capture",
                ],
            ),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        max_depth=6,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    joblib.dump(stats, STATS_PATH)

    print("[INFO] 서울시 멧돼지 출현 위험도 모델 학습 완료")
    print("[INFO] 데이터 크기:", df.shape)
    print("[INFO] 사용 feature:", FEATURES)
    print("[INFO] 모델 저장 위치:", MODEL_PATH)
    print("[INFO] 통계 저장 위치:", STATS_PATH)
    print()
    print("[INFO] risk_level 분포")
    print(df["risk_level"].value_counts())
    print()
    print("[INFO] 자치구별 총 출현개체수")
    print(df.groupby("자치구")["출현개체수"].sum().sort_values(ascending=False))
    print()
    print("[INFO] Accuracy:", accuracy)
    print()
    print("[INFO] Classification Report")
    print(report)


if __name__ == "__main__":
    train_model()