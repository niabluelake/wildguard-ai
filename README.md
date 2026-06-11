# WildGuard AI - 야생동물 출현 위험 점수 예측 및 대응 지원 서비스

WildGuard AI는 AI Hub 야생동물 라벨링 JSON 데이터를 기반으로 야생동물 관측 상황의 위험 점수를 예측하고, 이후 이미지 탐지와 대응 상담 기능으로 확장하는 AI 서비스입니다.

현재 1차 ML 프로젝트는 야생동물 이미지 자체를 분석하는 단계가 아니라, AI Hub 라벨링 JSON에 포함된 촬영 환경, 시간대, 날씨, 위치, 동물 종, 객체 수, bbox 면적 비율 등의 메타데이터를 정형 데이터로 변환한 뒤 위험 점수 `risk_score`를 예측하는 회귀 모델로 구현되어 있습니다.

---

## 프로젝트 개요

WildGuard AI는 하나의 야생동물 서비스 주제를 기반으로 1차부터 4차까지 확장하는 통합 AI 프로젝트입니다.

| 단계        | 내용                                           |
| --------- | -------------------------------------------- |
| 1차 ML     | AI Hub 야생동물 라벨링 JSON 메타데이터 기반 위험 점수 예측 회귀 모델 |
| 2차 Vision | 원천 이미지와 bbox 라벨을 활용한 YOLO 기반 야생동물 탐지         |
| 3차 LLM    | 위험 점수 예측 결과와 탐지 결과 기반 야생동물 대응 상담             |
| 4차 SLM    | 현장 환경에서 사용할 수 있는 경량 야생동물 대응 상담 모델            |

---

## 현재 진행 상황

| 작업                             | 상태    |
| ------------------------------ | ----- |
| GitHub 저장소 생성                  | 완료    |
| Flask 기본 구조 구성                 | 완료    |
| AI Hub JSON 데이터 배치             | 완료    |
| AI Hub JSON 메타데이터 CSV 변환       | 완료    |
| 위험 점수 `risk_score` 생성          | 완료    |
| 위험 등급 `risk_grade` 생성          | 완료    |
| RandomForestRegressor 회귀 모델 학습 | 완료    |
| Flask 위험도 예측 API 연결            | 완료    |
| `/api/risk/predict` API 테스트    | 완료    |
| 위험도 예측 웹 화면                    | 수정 예정 |
| YOLO 객체 탐지 API                 | 예정    |
| LLM 상담 기능                      | 예정    |
| SLM 경량화                        | 예정    |

---

## 1차 ML 프로젝트

### 목표

AI Hub 야생동물 라벨링 JSON에서 이미지 메타데이터와 annotation 정보를 추출하여 정형 데이터셋을 만들고, 야생동물 관측 상황의 위험 점수 `risk_score`를 0~100 범위의 숫자로 예측합니다.

기존의 단순 등급 분류 방식이 아니라, 회귀 모델을 사용하여 위험도를 수치화하고, 예측된 점수를 기준으로 `low`, `medium`, `high` 등급을 함께 제공합니다.

---

## 사용 데이터

원본 AI Hub 데이터는 GitHub에 업로드하지 않습니다.

```text
data/aihub/aihub_json/TL-quadruped/
```

변환된 CSV도 GitHub에 업로드하지 않으며, 아래 스크립트로 로컬에서 생성합니다.

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
```

---

## 데이터 변환 결과

현재 AI Hub JSON 30,700개를 변환했습니다.

| 항목        |     결과 |
| --------- | -----: |
| JSON 파일 수 | 30,700 |
| CSV 행 수   | 30,700 |
| CSV 컬럼 수  |     15 |

### 주요 종 분포

| species |  count |
| ------- | -----: |
| 멧돼지     | 30,613 |
| 고라니     |     64 |
| 반달가슴곰   |     21 |
| 멧토끼     |      2 |

### 위험 등급 분포

| risk_grade |  count |
| ---------- | -----: |
| medium     | 19,685 |
| high       | 10,343 |
| low        |    672 |

### 위험 점수 통계

| 항목   |     값 |
| ---- | ----: |
| mean | 62.59 |
| std  |  8.29 |
| min  | 26.33 |
| max  | 88.00 |

---

## 주요 Feature

| 구분          | 컬럼                                                              |
| ----------- | --------------------------------------------------------------- |
| 범주형 Feature | day, camera_type, weather, location, time_zone, season, species |
| 수치형 Feature | object_count, max_bbox_area_ratio, avg_bbox_area_ratio          |
| Target      | risk_score                                                      |

---

## 위험 점수 설계 기준

AI Hub 원본 JSON에는 실제 사고 피해 점수나 서비스용 위험도 점수가 포함되어 있지 않습니다.
따라서 본 프로젝트에서는 야생동물 관측 상황을 점수화하기 위해 도메인 가중치 기반의 `risk_score`를 설계했습니다.

위험 점수는 다음 요소를 기준으로 계산합니다.

| 요소          | 반영 이유                           |
| ----------- | ------------------------------- |
| 동물 종        | 종에 따라 사람, 농작물, 시설물에 미치는 위험도가 다름 |
| 시간대         | 야간과 새벽은 시야 확보와 대응이 어려움          |
| 날씨          | 비, 눈 등은 현장 대응 난도를 높일 수 있음       |
| 객체 수        | 여러 개체가 동시에 관측되면 위험도가 높아질 수 있음   |
| bbox 면적 비율  | 화면에서 크게 잡힌 객체는 카메라와 가까울 가능성이 있음 |
| IR 야간 촬영 여부 | 야간 출현 상황일 가능성이 높음               |

위험 점수는 0~100 범위로 제한되며, 서비스 화면에서는 다음 기준으로 등급을 함께 표시합니다.

| risk_score   | risk_grade |
| ------------ | ---------- |
| 0 이상 45 미만   | low        |
| 45 이상 70 미만  | medium     |
| 70 이상 100 이하 | high       |

---

## 모델 학습 결과

1차 ML 모델은 `RandomForestRegressor`를 사용하여 위험 점수 `risk_score`를 예측하도록 학습했습니다.

| 지표       |     결과 |
| -------- | -----: |
| MAE      | 0.0183 |
| RMSE     | 0.2324 |
| R2 Score | 0.9992 |

### 성능 해석

현재 `risk_score`는 실제 사고 피해 데이터가 아니라 AI Hub 메타데이터를 바탕으로 설계한 도메인 가중치 기반 점수입니다.
따라서 모델 성능은 실제 현장 사고 위험을 얼마나 정확히 예측했는지가 아니라, 설계된 위험 점수 체계를 회귀 모델이 얼마나 잘 학습했는지를 의미합니다.

향후 실제 신고 데이터, 피해 기록, 기상 데이터, 위치 기반 환경 데이터가 확보되면 현재의 `risk_score`를 실제 현장 데이터 기반 라벨로 교체하여 모델을 고도화할 수 있습니다.

---

## 주요 파일

| 구분             | 파일                                     |
| -------------- | -------------------------------------- |
| AI Hub JSON 변환 | `scripts/convert_aihub_json_to_csv.py` |
| 회귀 모델 학습       | `scripts/train_risk_model.py`          |
| 위험 점수 예측 서비스   | `services/risk_prediction_service.py`  |
| 위험 점수 예측 API   | `routes/risk_routes.py`                |
| 위험도 예측 화면 라우트  | `routes/risk_page_routes.py`           |
| 위험도 예측 화면      | `templates/risk.html`                  |
| 메인 화면          | `templates/index.html`                 |

---

## 프로젝트 구조

```text
wildguard-ai/
│
├── app.py
├── README.md
├── requirements.txt
│
├── docs/
│   ├── REQUIREMENTS_ANALYSIS.md
│   ├── FUNCTION_SPEC.md
│   ├── PRD.md
│   ├── ERD.md
│   ├── WEB_SERVICE_SPEC.md
│   └── TROUBLESHOOTING.md
│
├── routes/
│   ├── main_routes.py
│   ├── risk_routes.py
│   ├── risk_page_routes.py
│   ├── risk_history_routes.py
│   └── vision_routes.py
│
├── services/
│   ├── risk_prediction_service.py
│   ├── risk_log_service.py
│   ├── db_service.py
│   ├── auth_service.py
│   └── vision_service.py
│
├── scripts/
│   ├── convert_aihub_json_to_csv.py
│   ├── convert_aihub_metadata.py
│   ├── train_risk_model.py
│   └── train_seoul_boar_risk_model.py
│
├── templates/
│   ├── index.html
│   ├── risk.html
│   ├── login.html
│   ├── register.html
│   └── risk_history.html
│
├── static/
│
├── data/
│   └── aihub/
│       ├── aihub_json/
│       │   └── TL-quadruped/
│       └── ml_dataset/
│           └── aihub_wildlife_metadata.csv
│
└── models/
    └── ml/
        └── risk_regression_model.pkl
```

---

## 실행 방법

### 1. 프로젝트 이동

CMD 기준:

```cmd
cd /d E:\Projects\wildguard-ai
```

### 2. 가상환경 활성화

```cmd
.venv\Scripts\activate
```

### 3. 패키지 설치

```cmd
pip install -r requirements.txt
```

### 4. AI Hub JSON 메타데이터 변환

```cmd
python scripts\convert_aihub_json_to_csv.py
```

실행 후 아래 CSV가 생성됩니다.

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
```

### 5. 위험 점수 회귀 모델 학습

```cmd
python scripts\train_risk_model.py
```

실행 후 아래 모델 파일이 생성됩니다.

```text
models/ml/risk_regression_model.pkl
```

### 6. Flask 서버 실행

```cmd
python app.py
```

브라우저 접속:

```text
http://127.0.0.1:5000/
```

위험도 예측 화면:

```text
http://127.0.0.1:5000/risk
```

---

## API

### 위험 점수 예측 API

```text
POST /api/risk/predict
```

### Request 예시

```json
{
  "day": "night",
  "camera_type": "IR",
  "weather": "cloudy",
  "location": "산림",
  "time_zone": "night",
  "season": "fall",
  "species": "멧돼지",
  "object_count": 2,
  "max_bbox_area_ratio": 0.03,
  "avg_bbox_area_ratio": 0.02
}
```

### Response 예시

```json
{
  "success": true,
  "result": {
    "predicted_score": 68.77,
    "risk_score": 68.77,
    "risk_grade": "medium",
    "risk_level": "medium",
    "model_type": "regression",
    "message": "중간 수준의 위험입니다. 출현 조건을 확인하고 반복 관측 여부를 모니터링하세요.",
    "metrics": {
      "mae": 0.0183,
      "rmse": 0.2324,
      "r2": 0.9992
    },
    "input": {
      "day": "night",
      "camera_type": "IR",
      "weather": "cloudy",
      "location": "산림",
      "time_zone": "night",
      "season": "fall",
      "species": "멧돼지",
      "object_count": 2,
      "max_bbox_area_ratio": 0.03,
      "avg_bbox_area_ratio": 0.02
    }
  },
  "saved": false,
  "saved_to_db": false
}
```

### High 위험도 테스트 예시

```json
{
  "day": "night",
  "camera_type": "IR",
  "weather": "rain",
  "location": "산림",
  "time_zone": "night",
  "season": "fall",
  "species": "멧돼지",
  "object_count": 4,
  "max_bbox_area_ratio": 0.08,
  "avg_bbox_area_ratio": 0.05
}
```

예상 결과:

```json
{
  "predicted_score": 84.37,
  "risk_grade": "high",
  "model_type": "regression"
}
```

---

## GitHub 업로드 제외 대상

원본 데이터, 변환 CSV, 학습 모델 파일은 GitHub에 업로드하지 않습니다.

제외 대상:

```text
data/
models/ml/
*.pkl
*.joblib
```

모델 파일은 약 98MB 크기이며, 코드 실행으로 재생성할 수 있으므로 저장소에는 포함하지 않습니다.

모델이 필요한 경우 아래 순서로 로컬에서 생성합니다.

```cmd
python scripts\convert_aihub_json_to_csv.py
python scripts\train_risk_model.py
```

---

## 2차 Vision 계획

2차 프로젝트에서는 AI Hub 야생동물 이미지와 bbox 라벨을 활용하여 YOLO 기반 객체 탐지 기능을 구현합니다.

| 항목     | 내용                                  |
| ------ | ----------------------------------- |
| 사용 데이터 | AI Hub 야생동물 활동 영상 데이터               |
| 주요 입력  | 야생동물 이미지                            |
| 라벨     | bbox annotation                     |
| 모델     | YOLO                                |
| 결과     | 야생동물 탐지 여부, bbox, confidence, 위험 안내 |

---

## 3차 LLM 계획

위험 점수 예측 결과와 이미지 탐지 결과를 바탕으로 사용자의 상황에 맞는 야생동물 대응 상담을 제공합니다.

예시:

```text
야간 산림 인근에서 멧돼지가 크게 관측되어 위험 점수가 높게 예측되었습니다.
현장 접근을 피하고, 주변 시설물과 이동 경로를 확인하세요.
반복 출현이 확인되면 관계 기관에 신고하거나 차단 장치를 점검하세요.
```

---

## 4차 SLM 계획

현장 환경에서 빠르게 동작할 수 있는 경량 상담 모델을 구성합니다.
인터넷 연결이 불안정한 상황에서도 기본적인 야생동물 대응 안내를 제공하는 것을 목표로 합니다.

---

## 문서

| 문서                              | 설명         |
| ------------------------------- | ---------- |
| `docs/REQUIREMENTS_ANALYSIS.md` | 요구사항 분석서   |
| `docs/FUNCTION_SPEC.md`         | 기능명세서      |
| `docs/PRD.md`                   | 제품 요구사항 문서 |
| `docs/ERD.md`                   | ERD        |
| `docs/WEB_SERVICE_SPEC.md`      | 웹 서비스 명세서  |
| `docs/TROUBLESHOOTING.md`       | 오류 해결 기록   |
