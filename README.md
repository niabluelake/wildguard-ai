# WildGuard AI

WildGuard AI는 AI Hub 야생동물 관측 데이터와 한국도로공사 로드킬 다발 구간 데이터를 결합하여 야생동물 관측 상황의 현장 위험도를 평가하고, 이미지/영상 탐지 및 대응 상담까지 제공하는 Flask 기반 AI 서비스입니다.

본 프로젝트는 단순히 야생동물 출몰 여부를 예측하는 것이 아니라, 관측된 야생동물 상황을 기반으로 위험 점수, 위험 등급, 위험 요인, 현장 대응 가이드를 제공하는 것을 목표로 합니다.

---

## 1. 프로젝트 개요

### 프로젝트명

WildGuard AI

### 주제

야생동물 출몰 위험 예측 및 대응 지원 AI 서비스

### 핵심 목적

야생동물 관측 데이터, 위치 정보, 로드킬 다발 구간 정보를 활용하여 현장 위험도를 정량화하고, 사용자가 위험 상황을 빠르게 판단할 수 있도록 지원합니다.

### 주요 사용자

- 농장주
- 산림 및 공원 관리원
- 야생동물 출몰 지역 거주자
- 현장 안전 관리자

---

## 2. 주요 기능

| 기능 | 설명 | 상태 |
|---|---|---|
| 위험도 예측 | AI Hub 야생동물 관측 메타데이터와 로드킬 다발 구간 데이터를 기반으로 위험 점수 예측 | 구현 |
| 위험 요인 설명 | 예측 결과에 영향을 준 주요 조건을 사용자에게 설명 | 구현 |
| 현장 대응 가이드 | 위험 등급에 따른 행동 안내 메시지 제공 | 구현 |
| 로드킬 외부 feature 반영 | 관측 지점과 로드킬 다발 구간 간 거리 및 발생건수 기반 feature 생성 | 구현 |
| 이미지/영상 탐지 | YOLO 기반 야생동물 이미지 및 짧은 영상 탐지 | 구현 |
| 대응 상담 챗봇 | 위험도 예측 결과를 바탕으로 상황별 대응 상담 제공 | 구현 |
| 예측 기록 관리 | 로그인 사용자의 위험도 예측 결과 저장 및 조회 | 구현/연동 중 |

---

## 3. 서비스 흐름

```text
사용자 입력
  ├─ 지역
  ├─ 날씨
  ├─ 시간대
  └─ 계절

AI Hub 야생동물 관측 메타데이터 활용
  ├─ day
  ├─ camera_type
  ├─ weather
  ├─ location
  ├─ time_zone
  ├─ season
  ├─ species
  ├─ object_count
  ├─ max_bbox_area_ratio
  └─ avg_bbox_area_ratio

외부 공공데이터 결합
  └─ 한국도로공사 로드킬 다발 구간 데이터
      ├─ 위도
      ├─ 경도
      └─ 발생건수

로드킬 hotspot feature 생성
  ├─ nearest_roadkill_distance_km
  ├─ roadkill_count_within_5km
  ├─ roadkill_count_within_10km
  ├─ roadkill_count_within_20km
  ├─ roadkill_max_cases_nearby
  ├─ roadkill_weighted_score
  └─ near_roadkill_hotspot

RandomForestRegressor 회귀 모델 예측
  ├─ predicted_score
  ├─ predicted_grade
  ├─ risk_reasons
  ├─ action_message
  └─ roadkill_features

웹 서비스 제공
  ├─ /risk 위험도 예측 화면
  ├─ /vision 이미지/영상 탐지 화면
  └─ /chat 대응 상담 챗봇
```

---

## 4. 사용 데이터

### 4.1 AI Hub 야생동물 관측 데이터

본 프로젝트는 AI Hub 야생동물 활동 영상 데이터의 라벨링 JSON을 활용합니다.

원본 데이터는 용량 및 라이선스 문제로 GitHub에 업로드하지 않습니다.

로컬 데이터 위치 예시:

```text
data/aihub/aihub_json/TL-quadruped/
```

현재 프로젝트 기준 변환 대상 JSON 수는 약 30,700개입니다.

### 4.2 한국도로공사 로드킬 데이터

본 프로젝트는 한국도로공사 로드킬 다발 구간 데이터를 외부 feature로 활용합니다.

활용 범위:

```text
2019년 상반기 ~ 2025년 5월 기준
```

통합 파일 예시:

```text
data/external/roadkill/roadkill_2019_2025_combined.csv
```

로드킬 원본 및 통합 CSV는 GitHub에 업로드하지 않습니다.

### 4.3 생성되는 주요 데이터 파일

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
data/aihub/ml_dataset/aihub_wildlife_metadata_with_gps.csv
data/aihub/ml_dataset/aihub_wildlife_metadata_enriched.csv
```

| 파일 | 설명 |
|---|---|
| `aihub_wildlife_metadata.csv` | AI Hub JSON에서 기본 메타데이터를 추출한 CSV |
| `aihub_wildlife_metadata_with_gps.csv` | 기존 메타데이터에 latitude, longitude를 추가한 CSV |
| `aihub_wildlife_metadata_enriched.csv` | GPS 기반 로드킬 feature를 결합한 최종 학습 데이터셋 |

---

## 5. 위험도 예측 모델

### 5.1 모델 목적

AI Hub 야생동물 관측 메타데이터와 로드킬 다발 구간 정보를 활용하여 관측 상황의 위험 점수를 예측합니다.

이 모델은 실제 사고 발생 여부를 직접 예측하는 모델이 아니라, 관측 조건과 외부 위험 요인을 바탕으로 설계한 위험 점수 체계를 학습하는 회귀 모델입니다.

### 5.2 모델 유형

```text
RandomForestRegressor
```

### 5.3 모델 파일

```text
models/ml/risk_regression_model.pkl
```

모델 파일은 GitHub에 업로드하지 않으며, 로컬에서 학습 스크립트를 실행해 생성합니다.

### 5.4 입력 feature

#### 범주형 feature

| feature | 설명 |
|---|---|
| `day` | 주간/야간 |
| `camera_type` | IR/RGB 카메라 유형 |
| `weather` | 날씨 |
| `location` | 관측 지역 |
| `time_zone` | 시간대 |
| `season` | 계절 |
| `species` | 관측 종 |

#### 수치형 feature

| feature | 설명 |
|---|---|
| `object_count` | 관측 객체 수 |
| `max_bbox_area_ratio` | 가장 큰 객체의 bbox 면적 비율 |
| `avg_bbox_area_ratio` | 평균 bbox 면적 비율 |
| `nearest_roadkill_distance_km` | 가장 가까운 로드킬 다발 구간까지 거리 |
| `roadkill_count_within_5km` | 반경 5km 내 로드킬 발생건수 |
| `roadkill_count_within_10km` | 반경 10km 내 로드킬 발생건수 |
| `roadkill_count_within_20km` | 반경 20km 내 로드킬 발생건수 |
| `roadkill_max_cases_nearby` | 주변 로드킬 지점 중 최대 발생건수 |
| `roadkill_weighted_score` | 거리와 발생건수를 반영한 로드킬 가중 점수 |
| `near_roadkill_hotspot` | 10km 이내 로드킬 hotspot 존재 여부 |

### 5.5 예측 결과

| 출력값 | 설명 |
|---|---|
| `predicted_score` | 0~100 범위 위험 점수 |
| `predicted_grade` | low / medium / high 위험 등급 |
| `predicted_grade_ko` | 한국어 위험 등급 |
| `risk_reasons` | 주요 위험 요인 목록 |
| `action_message` | 현장 대응 가이드 |
| `roadkill_features` | 예측에 사용된 로드킬 외부 feature |

### 5.6 모델 성능

로드킬 feature를 결합한 최종 회귀 모델 학습 결과입니다.

| 지표 | 값 |
|---|---:|
| MAE | 0.0276 |
| RMSE | 0.2472 |
| R2 Score | 0.9991 |

해당 성능 지표는 실제 사고 발생 여부를 맞힌 정확도가 아니라, 설계된 위험 점수 체계를 회귀 모델이 얼마나 잘 학습했는지를 의미합니다.

---

## 6. 로드킬 feature 생성 방식

로드킬 데이터는 연도별 개별 사고 로그가 아니라 고속도로 구간별 로드킬 다발 지점 데이터입니다.

따라서 본 프로젝트에서는 관측 지점과 로드킬 다발 구간의 위도·경도를 활용하여 거리 기반 feature를 생성했습니다.

### 생성 방식

```text
AI Hub 관측 지점 GPS
  └─ latitude, longitude

한국도로공사 로드킬 다발 구간
  └─ 위도, 경도, 발생건수

거리 계산
  └─ Haversine Distance

반경별 집계
  ├─ 5km 이내 발생건수
  ├─ 10km 이내 발생건수
  └─ 20km 이내 발생건수

가중 점수 생성
  └─ 가까운 로드킬 다발 구간일수록 더 큰 위험 점수 부여
```

### 반영 이유

단순히 현재 관측된 야생동물 정보만 사용하는 경우 위험도 산정 근거가 약할 수 있습니다.

로드킬 다발 구간 데이터를 결합하면 특정 관측 지점 주변에 과거 야생동물 사고가 자주 발생한 구간이 있는지 반영할 수 있으므로, 현장 위험도 평가 모델의 설명력이 높아집니다.

---

## 7. 주요 API

### 7.1 위험도 예측 API

```text
POST /api/risk/predict
```

#### Request 예시

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

#### Response 예시

```json
{
  "success": true,
  "result": {
    "predicted_score": 86.98,
    "predicted_grade": "high",
    "predicted_grade_ko": "높음",
    "risk_reasons": [
      "야간 시간대 관측으로 인해 위험도가 상승했습니다.",
      "멧돼지는 현장 접근 시 주의가 필요한 종입니다.",
      "동시에 관측된 객체 수가 많아 위험도가 상승했습니다.",
      "객체가 화면에서 차지하는 비율이 높아 근접 관측 가능성이 있습니다.",
      "관측 지점 주변 20km 이내에 로드킬 다발 구간이 존재합니다.",
      "가까운 로드킬 다발 구간의 발생건수가 위험도 산정에 반영되었습니다."
    ],
    "action_message": "위험 수준이 높습니다. 현장 접근을 주의하고 주변 시설물과 농작물 피해 여부를 점검하세요.",
    "roadkill_features": {
      "nearest_roadkill_distance_km": 13.516,
      "roadkill_count_within_5km": 0.0,
      "roadkill_count_within_10km": 0.0,
      "roadkill_count_within_20km": 4.0,
      "roadkill_weighted_score": 17.447,
      "near_roadkill_hotspot": 0.0
    }
  }
}
```

### 7.2 대응 상담 API

```text
POST /api/chat/message
```

#### Request 예시

```json
{
  "region_name": "집 근처",
  "location": "진전면",
  "weather": "rain",
  "time_zone": "night",
  "season": "fall",
  "consultation_mode": "detail",
  "message": "오늘 밤에 나가도 괜찮을까?"
}
```

### 7.3 상담 모드

| 값 | 설명 |
|---|---|
| `detail` | 상세 상담 모드 |
| `field` | 현장 대응 모드 |

---

## 8. 주요 화면

| URL | 설명 |
|---|---|
| `/` | 메인 화면 |
| `/risk` | 야생동물 위험도 예측 화면 |
| `/vision` | 이미지/영상 기반 야생동물 탐지 |
| `/chat` | 위험도 기반 대응 상담 챗봇 |
| `/risk/history` | 로그인 사용자 예측 기록 조회 |

---

## 9. 주요 파일 구조

```text
wildguard-ai/
├─ app.py
├─ routes/
│  ├─ main_routes.py
│  ├─ risk_routes.py
│  ├─ risk_page_routes.py
│  ├─ risk_history_routes.py
│  └─ vision_routes.py
├─ services/
│  ├─ risk_prediction_service.py
│  ├─ risk_log_service.py
│  └─ vision_service.py
├─ scripts/
│  ├─ convert_aihub_json_to_csv.py
│  ├─ add_gps_to_ml_dataset.py
│  ├─ enrich_ml_dataset_with_roadkill.py
│  └─ train_risk_model.py
├─ templates/
│  ├─ index.html
│  ├─ risk.html
│  ├─ vision.html
│  └─ chat.html
├─ data/
│  ├─ aihub/
│  └─ external/
├─ models/
│  ├─ ml/
│  └─ vision/
└─ README.md
```

---

## 10. 주요 파일 설명

| 구분 | 파일 |
|---|---|
| Flask 앱 진입점 | `app.py` |
| 위험도 예측 API | `routes/risk_routes.py` |
| 위험도 예측 페이지 | `routes/risk_page_routes.py` |
| 예측 기록 라우트 | `routes/risk_history_routes.py` |
| 위험도 예측 서비스 | `services/risk_prediction_service.py` |
| 예측 기록 서비스 | `services/risk_log_service.py` |
| AI Hub JSON 변환 | `scripts/convert_aihub_json_to_csv.py` |
| GPS 추가 스크립트 | `scripts/add_gps_to_ml_dataset.py` |
| 로드킬 feature 결합 | `scripts/enrich_ml_dataset_with_roadkill.py` |
| 위험도 회귀 모델 학습 | `scripts/train_risk_model.py` |
| 위험도 예측 화면 | `templates/risk.html` |

---

## 11. 실행 방법

### 11.1 프로젝트 이동

```cmd
cd /d E:\Projects\wildguard-ai
```

### 11.2 가상환경 활성화

```cmd
.venv\Scripts\activate
```

### 11.3 패키지 설치

```cmd
pip install -r requirements.txt
```

### 11.4 AI Hub JSON 메타데이터 변환

이미 `aihub_wildlife_metadata.csv`가 있다면 생략할 수 있습니다.

```cmd
python scripts\convert_aihub_json_to_csv.py
```

### 11.5 GPS 컬럼 추가

```cmd
python scripts\add_gps_to_ml_dataset.py
```

생성 파일:

```text
data/aihub/ml_dataset/aihub_wildlife_metadata_with_gps.csv
```

### 11.6 로드킬 feature 결합

```cmd
python scripts\enrich_ml_dataset_with_roadkill.py
```

생성 파일:

```text
data/aihub/ml_dataset/aihub_wildlife_metadata_enriched.csv
```

### 11.7 위험도 회귀 모델 학습

```cmd
python scripts\train_risk_model.py
```

생성 파일:

```text
models/ml/risk_regression_model.pkl
```

### 11.8 Flask 서버 실행

```cmd
python app.py
```

브라우저 접속:

```text
http://127.0.0.1:5000/
```

---

## 12. 테스트 예시

### 위험도 예측 API 테스트

```cmd
curl -X POST http://127.0.0.1:5000/api/risk/predict ^
-H "Content-Type: application/json" ^
-d "{\"day\":\"night\",\"camera_type\":\"IR\",\"weather\":\"rain\",\"location\":\"산림\",\"time_zone\":\"night\",\"season\":\"fall\",\"species\":\"멧돼지\",\"object_count\":4,\"max_bbox_area_ratio\":0.08,\"avg_bbox_area_ratio\":0.05}"
```

예상 결과:

```text
success: true
predicted_score 반환
predicted_grade 반환
risk_reasons 반환
action_message 반환
roadkill_features 반환
```

---

## 13. GitHub 업로드 제외 파일

다음 파일 및 폴더는 용량, 라이선스, 로컬 환경 의존성 문제로 GitHub에 업로드하지 않습니다.

```text
data/
models/ml/
.venv/
.idea/
__pycache__/
*.pkl
*.csv
```

단, 학습 및 전처리 스크립트는 GitHub에 포함하여 로컬에서 동일한 파이프라인을 재현할 수 있도록 합니다.

---

## 14. Git 작업 규칙

### 작업 시작 전

```cmd
git pull origin main
git status
```

### 작업 종료 후

```cmd
git status
git add <수정한 파일>
git commit -m "커밋 메시지"
git pull --rebase origin main
git push origin main
git status
```

### 주의사항

- `data/` 폴더는 GitHub에 업로드하지 않습니다.
- `models/ml/` 폴더의 학습 모델 파일은 GitHub에 업로드하지 않습니다.
- `.idea/`, `.venv/` 등 로컬 환경 파일은 커밋하지 않습니다.
- 집 PC와 학원 PC를 오갈 때는 작업 시작 전에 반드시 `git pull origin main`을 먼저 실행합니다.

---

## 15. 현재 구현 상태 요약

### 1차 ML

- AI Hub JSON 메타데이터 CSV 변환
- GPS 좌표 추출
- 한국도로공사 로드킬 다발 구간 데이터 통합
- 관측 지점과 로드킬 지점 간 거리 feature 생성
- 로드킬 hotspot 기반 위험 점수 보정
- RandomForestRegressor 회귀 모델 학습
- 위험 점수 및 등급 예측 API 구현
- 위험 요인 설명 및 현장 대응 메시지 반환
- 위험도 예측 웹 화면 연동

### 2차 Vision

- YOLO 기반 야생동물 이미지/영상 탐지
- 탐지 결과 bounding box 표시
- 위험 여부 판단 기능 구현

### 3차 LLM

- 야생동물 대응 상담 챗봇 기능 구현
- 위험도 예측 결과 기반 상담 흐름 구성

### 4차 SLM

- 향후 경량 모델 기반 상담 및 요약 기능으로 확장 예정

---

## 16. 향후 개선 방향

- 사용자가 입력한 실제 GPS 좌표 기반 실시간 로드킬 feature 계산
- 기상청 API를 활용한 실시간 날씨 feature 추가
- 토지피복도 및 생태자연도 기반 공간 환경 feature 추가
- 위험도 예측 결과와 YOLO 탐지 결과 자동 연동
- 예측 기록 기반 지역별 위험 통계 대시보드 구현
- 지도 기반 위험 hotspot 시각화
- 상담 챗봇 답변 고도화
- 실제 신고/피해 데이터 확보 시 위험도 점수 체계 재설계

---

## 17. 프로젝트 의의

WildGuard AI의 1차 머신러닝 서비스는 단순한 점수 예측 API가 아니라, 야생동물 관측 메타데이터와 외부 공공데이터를 결합하여 현장 위험도를 평가하는 구조로 설계되었습니다.

특히 한국도로공사 로드킬 다발 구간 데이터를 활용하여 관측 지점 주변의 과거 야생동물 사고 위험을 feature로 반영했고, 예측 결과와 함께 위험 요인 및 대응 메시지를 제공하여 실제 서비스 형태에 가까운 위험도 평가 흐름을 구현했습니다.
