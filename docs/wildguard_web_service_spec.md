# WildGuard AI 웹 서비스 명세서

## 1. 서비스 URL

| URL | Method | 설명 |
|---|---|---|
| `/` | GET | 메인 화면 |
| `/risk` | GET | 위험도 예측 화면 |
| `/api/risk/predict` | POST | 위험도 예측 API |
| `/vision` | GET | 이미지/영상 탐지 화면 |
| `/api/vision/predict` | POST | 이미지/영상 탐지 API |
| `/chat` | GET | 대응 상담 챗봇 화면 |
| `/api/chat/message` | POST | 대응 상담 API |
| `/auth/register` | GET/POST | 회원가입 |
| `/auth/login` | GET/POST | 로그인 |
| `/auth/logout` | GET | 로그아웃 |
| `/risk/history` | GET | 예측 기록 조회 |

---

## 2. 화면 명세

### 2.1 메인 화면

#### URL

```text
GET /
```

#### 주요 기능

- 서비스 소개
- 위험도 예측, 이미지/영상 탐지, 대응 상담 챗봇으로 이동
- 로그인 상태에 따라 예측 기록 또는 회원가입 버튼 표시

---

### 2.2 위험도 예측 화면

#### URL

```text
GET /risk
```

#### 입력값

| 필드 | 설명 |
|---|---|
| 지역 이름 | 사용자가 알아보기 쉬운 별칭 |
| 위험도를 확인할 지역 | AI Hub 관측 지역 |
| 날씨 | sunny, cloudy, rain, snow |
| 시간대 | dawn, day, evening, night |
| 계절 | spring, summer, fall, winter |

현재 웹 화면은 사용성을 위해 종, 객체 수, bbox 면적 비율을 직접 입력받지 않고 기본 관측 시나리오를 API 요청에 포함한다.

#### 내부 API 요청 보정값

| 필드 | 기본값 |
|---|---|
| `day` | 시간대가 day이면 `day`, 그 외에는 `night` |
| `camera_type` | 시간대가 day이면 `RGB`, 그 외에는 `IR` |
| `species` | `멧돼지` |
| `object_count` | `4` |
| `max_bbox_area_ratio` | `0.08` |
| `avg_bbox_area_ratio` | `0.05` |

#### 출력값

| 항목 | 설명 |
|---|---|
| 위험 점수 | `predicted_score` |
| 위험 등급 | `predicted_grade_ko` |
| 위험도 설명 | `message` 또는 `action_message` |
| 주요 위험 요인 | `risk_reasons` |
| 현장 대응 가이드 | `action_message` |
| 로드킬 다발 구간 기반 외부 feature | `roadkill_features` |
| 모델 성능 지표 | MAE, RMSE, R2 Score |
| DB 저장 여부 | 로그인 상태에 따른 저장 결과 |

---

### 2.3 이미지/영상 탐지 화면

#### URL

```text
GET /vision
```

#### 입력값

- 이미지 파일
- 짧은 영상 파일

#### 출력값

- 탐지 클래스
- 탐지 신뢰도
- bbox 좌표
- 결과 이미지 URL
- 탐지 기반 위험 안내

---

### 2.4 대응 상담 화면

#### URL

```text
GET /chat
```

#### 입력값

- 상담 모드
- 지역 조건
- 사용자 질문

#### 상담 모드

| 모드 | 설명 |
|---|---|
| 상세 상담 모드 | 위험도 해석과 행동 요령을 자세히 설명 |
| 현장 대응 모드 | 빠르게 확인할 수 있는 체크리스트 중심 안내 |

---

## 3. API 명세

### 3.1 위험도 예측 API

```text
POST /api/risk/predict
```

#### Request

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

#### Response

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
  },
  "saved": false,
  "saved_to_db": false
}
```

---

### 3.2 대응 상담 API

```text
POST /api/chat/message
```

#### Request

```json
{
  "region_name": "집 근처",
  "location": "진전면",
  "weather": "rain",
  "time_zone": "night",
  "season": "fall",
  "consultation_mode": "field",
  "message": "지금 바로 어떻게 해야 돼?"
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "answer": "[현장 대응 모드] ...",
    "consultation_mode": "field",
    "mode_name": "현장 대응 모드",
    "risk_result": {}
  }
}
```

---

### 3.3 이미지 탐지 API

```text
POST /api/vision/predict
```

#### Response 주요 항목

| 항목 | 설명 |
|---|---|
| `class_name` | 탐지 클래스 |
| `confidence` | 탐지 신뢰도 |
| `bbox` | 탐지 좌표 |
| `result_image_url` | 결과 이미지 경로 |
| `risk_hint` | 탐지 기반 위험 안내 |

---

## 4. 화면 표시 기준

### 위험 등급 기준

| 점수 범위 | 등급 | 한글 표시 |
|---:|---|---|
| 0 이상 45 미만 | low | 낮음 |
| 45 이상 70 미만 | medium | 보통 |
| 70 이상 100 이하 | high | 높음 |

### 위험도 예측 화면 상세 표시

위험도 예측 화면은 다음 정보를 카드 형태로 표시한다.

- 예측 위험 점수
- 위험 등급
- 주요 위험 요인
- 현장 대응 가이드
- 로드킬 다발 구간 기반 외부 feature
- DB 저장 여부
- 모델 성능 지표

---

## 5. 데이터 및 모델 관리

다음 파일은 GitHub에 업로드하지 않는다.

```text
data/
models/ml/
*.csv
*.pkl
```

모델과 데이터는 로컬에서 다음 순서로 재생성한다.

```cmd
python scripts\convert_aihub_json_to_csv.py
python scripts\add_gps_to_ml_dataset.py
python scripts\enrich_ml_dataset_with_roadkill.py
python scripts\train_risk_model.py
```
