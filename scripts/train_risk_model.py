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

DATA_PATH = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_wildlife_metadata.csv"
MODEL_DIR = BASE_DIR / "models" / "ml"
MODEL_PATH = MODEL_DIR / "risk_model.pkl"

# 일반 사용자가 직접 입력할 수 있는 상황 정보만 사용
CATEGORICAL_FEATURES = [
    "day",
    "weather",
    "location",
    "time_zone",
    "season",
]

NUMERIC_FEATURES = []

TARGET = "risk_level"


def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"학습 데이터가 없습니다: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

    required_columns = CATEGORICAL_FEATURES + NUMERIC_FEATURES + [TARGET]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"필수 컬럼이 없습니다: {missing_columns}")

    df = df.dropna(subset=required_columns).copy()
    return df


def train_model():
    df = load_dataset()

    feature_columns = CATEGORICAL_FEATURES + NUMERIC_FEATURES

    X = df[feature_columns]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    transformers = [
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ]

    if NUMERIC_FEATURES:
        transformers.append(("num", "passthrough", NUMERIC_FEATURES))

    preprocessor = ColumnTransformer(
        transformers=transformers
    )

    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        class_weight="balanced",
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

    print("[INFO] 상황 기반 야생동물 출현 위험도 예측 모델 학습 완료")
    print("[INFO] 사용 feature:", feature_columns)
    print("[INFO] 데이터 크기:", df.shape)
    print("[INFO] 모델 저장 위치:", MODEL_PATH)
    print()
    print("[INFO] Accuracy:", accuracy)
    print()
    print("[INFO] Classification Report")
    print(report)


if __name__ == "__main__":
    train_model()