# WildGuard AI - 야생동물 출현 위험도 예측 및 대응 지원 서비스

서울시 멧돼지 민원신고 현황 데이터와 AI Hub 야생동물 영상 데이터를 활용하여  
야생동물 출현 위험도 예측, 이미지 탐지, 대응 상담 기능을 단계적으로 구현하는 AI 서비스입니다.

---

## 프로젝트 개요

WildGuard AI는 야생동물 출현 위험을 사전에 예측하고, 현장에서 탐지 및 대응 안내까지 지원하는 통합 AI 서비스입니다.

| 단계 | 내용 |
|---|---|
| 1차 ML | 서울시 멧돼지 민원신고 현황 데이터를 기반으로 자치구·월별 출현 위험도 예측 |
| 2차 Vision | AI Hub 야생동물 이미지와 bbox 라벨을 활용한 YOLO 기반 야생동물 탐지 |
| 3차 LLM | 위험도 예측 결과와 탐지 결과를 바탕으로 야생동물 대응 상담 제공 |
| 4차 SLM | 현장 환경에서 사용할 수 있는 경량 야생동물 대응 상담 모델 |

---

## 현재 진행 상황

| 작업 | 상태 |
|---|---|
| GitHub 저장소 생성 | 완료 |
| Flask 기본 구조 구성 | 완료 |
| 서울시 멧돼지 민원신고 CSV 수집 | 완료 |
| 위험도 예측용 파생 feature 생성 | 완료 |
| RandomForest 위험도 예측 모델 학습 | 완료 |
| Flask 위험도 예측 API 연결 | 진행 중 |
| 위험도 예측 웹 화면 구현 | 진행 중 |
| Oracle DB 예측 기록 저장 | 수정 예정 |
| YOLO 라벨 변환 | 예정 |
| YOLO 객체 탐지 API | 예정 |
| LLM 상담 기능 | 예정 |
| SLM 경량화 | 예정 |

---

## 1차 ML 프로젝트

### 목표

서울시 멧돼지 민원신고 현황 데이터를 활용하여  
사용자가 입력한 **자치구와 월** 조건에 따른 멧돼지 출현 위험도를 예측합니다.

### 사용 데이터

원본 데이터는 GitHub에 업로드하지 않습니다.

```text
data/seoul_wildlife/seoul_boar_reports.csv
```

### 원본 컬럼

| 컬럼 | 설명 |
|---|---|
| 연도 | 신고 데이터 기준 연도 |
| 자치구 | 서울시 자치구 |
| 월 | 신고 월 |
| 출현개체수 | 해당 조건에서 신고된 멧돼지 출현 개체수 |
| 포획개체수 | 해당 조건에서 포획된 멧돼지 개체수 |

### 주요 데이터 요약

| 항목 | 값 |
|---|---:|
| 데이터 행 수 | 360 |
| 사용 기간 | 2022년 ~ 2024년 |
| 사용 자치구 수 | 11개 |
| 총 출현개체수 | 1,118건 |

### 자치구별 총 출현개체수

| 자치구 | 출현개체수 |
|---|---:|
| 은평구 | 275 |
| 도봉구 | 274 |
| 성북구 | 146 |
| 강북구 | 79 |
| 종로구 | 73 |
| 서대문구 | 69 |
| 노원구 | 64 |
| 중랑구 | 54 |
| 송파구 | 50 |
| 광진구 | 23 |
| 강동구 | 11 |

---

## Feature 설계

사용자가 직접 입력하는 값은 단순하게 유지했습니다.

```text
자치구
월
```

모델 학습 시에는 원본 CSV에서 다음 파생 feature를 생성하여 사용했습니다.

| 구분 | Feature |
|---|---|
| 기본 feature | 연도, 자치구, 월, 계절 |
| 파생 feature | district_total_count |
| 파생 feature | district_avg_count |
| 파생 feature | month_avg_count |
| 파생 feature | district_month_avg_count |
| 파생 feature | district_total_capture |
| Target | risk_level |

### 위험도 라벨 기준

| 조건 | risk_level |
|---|---|
| 출현개체수 0건 | low |
| 출현개체수 1건 | medium |
| 출현개체수 2건 이상 | high |

---

## 모델 학습 결과

RandomForestClassifier를 사용하여 멧돼지 출현 위험도 분류 모델을 학습했습니다.

```text
Accuracy: 0.7222
```

### Risk Level 분포

| risk_level | count |
|---|---:|
| low | 160 |
| high | 146 |
| medium | 54 |

### Classification Report

```text
              precision    recall  f1-score   support

        high       0.81      0.72      0.76        29
         low       0.74      0.88      0.80        32
      medium       0.38      0.27      0.32        11

    accuracy                           0.72        72
   macro avg       0.64      0.62      0.63        72
weighted avg       0.71      0.72      0.71        72
```

### 성능 해석

`high`와 `low`는 비교적 안정적으로 분류되었지만, `medium`은 표본 수가 적고 경계값에 위치하기 때문에 성능이 낮게 나타났습니다.  
향후 추가 연도 데이터, 기상 데이터, 산림·하천 인접도, 공원 면적, 인구밀도 등을 결합하면 예측 성능을 개선할 수 있습니다.

---

## 주요 파일

| 구분 | 파일 |
|---|---|
| 멧돼지 위험도 모델 학습 | `scripts/train_seoul_boar_risk_model.py` |
| 위험도 예측 서비스 | `services/risk_prediction_service.py` |
| 위험도 예측 API | `routes/risk_routes.py` |
| 위험도 예측 화면 라우트 | `routes/risk_page_routes.py` |
| 위험도 예측 화면 | `templates/risk.html` |
| 메인 화면 | `templates/index.html` |
| Oracle DB 예측 기록 서비스 | `services/risk_log_service.py` |

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
│   └── risk_history_routes.py
│
├── services/
│   ├── risk_prediction_service.py
│   ├── risk_log_service.py
│   ├── db_service.py
│   └── auth_service.py
│
├── scripts/
│   ├── train_seoul_boar_risk_model.py
│   ├── convert_aihub_metadata.py
│   └── convert_aihub_json_to_csv.py
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
│   └── seoul_wildlife/
│       └── seoul_boar_reports.csv
│
└── models/
    └── ml/
        ├── seoul_boar_risk_model.pkl
        └── seoul_boar_stats.pkl
```

---

## 실행 방법

### 1. 가상환경 활성화

CMD 기준:

```cmd
cd /d E:\Projects\wildguard-ai
.venv\Scripts\activate
```

### 2. 패키지 설치

```cmd
pip install -r requirements.txt
```

### 3. 모델 학습

```cmd
python scripts\train_seoul_boar_risk_model.py
```

학습이 완료되면 아래 파일이 생성됩니다.

```text
models/ml/seoul_boar_risk_model.pkl
models/ml/seoul_boar_stats.pkl
```

### 4. Flask 서버 실행

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

### 위험도 예측 API

```text
POST /api/risk/predict
```

### Request 예시

```json
{
  "district": "은평구",
  "month": 10
}
```

### Response 예시

```json
{
  "success": true,
  "result": {
    "risk_level": "high",
    "message": "해당 자치구와 월 조건에서는 과거 멧돼지 출현 신고가 많은 편입니다. 산림 인근, 하천 주변, 야간 이동에 주의하세요.",
    "input": {
      "district": "은평구",
      "month": 10,
      "year": 2024,
      "season": "가을"
    },
    "stats": {
      "district_total_count": 275,
      "district_avg_count": 7.64,
      "month_avg_count": 3.2,
      "district_month_avg_count": 9.0,
      "district_total_capture": 272
    }
  },
  "saved": false,
  "saved_to_db": false
}
```

---

## GitHub 업로드 제외 대상

원본 데이터와 학습 결과물은 GitHub에 업로드하지 않습니다.

`.gitignore` 예시:

```gitignore
.venv/
__pycache__/
*.pyc
.env

data/
models/ml/
*.pkl
*.joblib

.idea/
.vscode/
```

---

## 2차 Vision 계획

2차 프로젝트에서는 AI Hub 야생동물 이미지와 bbox 라벨을 활용하여 YOLO 기반 객체 탐지 기능을 구현합니다.

| 항목 | 내용 |
|---|---|
| 사용 데이터 | AI Hub 야생동물 활동 영상 데이터 |
| 주요 입력 | 야생동물 이미지 |
| 라벨 | bbox annotation |
| 모델 | YOLO |
| 결과 | 야생동물 탐지 여부, bbox, confidence, 위험 안내 |

---

## 3차 LLM 계획

위험도 예측 결과와 이미지 탐지 결과를 바탕으로 사용자의 상황에 맞는 야생동물 대응 상담을 제공합니다.

예시:

```text
은평구 10월 멧돼지 출현 위험도가 높게 예측되었습니다.
야간 산림 인근 이동을 피하고, 멧돼지를 발견하면 접근하지 말고 안전한 장소로 이동하세요.
```

---

## 4차 SLM 계획

현장 환경에서 빠르게 동작할 수 있는 경량 상담 모델을 구성합니다.  
인터넷 연결이 불안정한 상황에서도 기본적인 대응 안내를 제공하는 것을 목표로 합니다.

---

## 문서

| 문서 | 설명 |
|---|---|
| `docs/REQUIREMENTS_ANALYSIS.md` | 요구사항 분석서 |
| `docs/FUNCTION_SPEC.md` | 기능명세서 |
| `docs/PRD.md` | 제품 요구사항 문서 |
| `docs/ERD.md` | ERD |
| `docs/WEB_SERVICE_SPEC.md` | 웹 서비스 명세서 |
| `docs/TROUBLESHOOTING.md` | 오류 해결 기록 |
