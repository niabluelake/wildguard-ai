# WildGuard AI 기능 명세서

## 1. 문서 목적

본 문서는 WildGuard AI 서비스의 주요 기능, 입력값, 처리 흐름, 출력값을 정의한다.

---

## 2. 기능 목록

| ID | 기능 | 설명 |
| --- | --- | --- |
| F-001 | 메인 화면 | 서비스 소개 및 주요 기능 이동 제공 |
| F-002 | 위험도 예측 화면 | 사용자가 지역 조건을 입력해 위험도 예측 |
| F-003 | 위험도 예측 API | 지역 기반 위험 점수, 등급, 대응 요령 반환 |
| F-004 | 이미지/영상 탐지 화면 | 이미지 또는 영상 업로드 기능 제공 |
| F-005 | 이미지/영상 탐지 API | YOLO 기반 탐지 결과 반환 |
| F-006 | 대응 상담 화면 | 위험도 기반 상담 질문 입력 및 답변 표시 |
| F-007 | 대응 상담 API | 위험도 예측 결과 기반 상담 답변 반환 |
| F-008 | 회원 기능 | 회원가입, 로그인, 로그아웃 |
| F-009 | 예측 기록 | 로그인 사용자 예측 결과 저장 및 조회 |

---

## 3. F-001 메인 화면

```text
GET /
```

WildGuard AI의 주요 기능인 위험도 예측, 이미지/영상 탐지, 대응 상담 챗봇으로 이동할 수 있는 메인 화면을 제공한다.

관련 파일: `routes/main_routes.py`, `templates/index.html`

---

## 4. F-002 위험도 예측 화면

```text
GET /risk
```

사용자가 관측 지역, 날씨, 시간대, 계절을 선택하여 야생동물 출몰 위험도를 확인할 수 있는 화면을 제공한다.

| 필드 | 설명 |
| --- | --- |
| `region_name` | 사용자 표시용 지역 별칭 |
| `location` | AI Hub 관측 데이터에 포함된 지역명 |
| `weather` | 날씨 |
| `time_zone` | 시간대 |
| `season` | 계절 |

관련 파일: `routes/risk_page_routes.py`, `templates/risk.html`

---

## 5. F-003 위험도 예측 API

```text
POST /api/risk/predict
```

입력된 지역 조건을 기반으로 지역 위험 프로필을 구성하고, RandomForestRegressor 모델로 야생동물 출몰 위험 점수를 예측한다.

| 구분 | 파일 |
| --- | --- |
| 라우트 | `routes/risk_routes.py` |
| 서비스 | `services/risk_prediction_service.py` |
| 데이터셋 생성 | `scripts/create_area_risk_dataset.py` |
| 모델 학습 | `scripts/train_area_risk_model.py` |
| 모델 파일 | `models/ml/area_risk_model.pkl` |

Request:

```json
{
  "region_name": "집 근처",
  "location": "진전면",
  "weather": "rain",
  "time_zone": "night",
  "season": "fall"
}
```

Response 주요 필드:

| 필드 | 설명 |
| --- | --- |
| `predicted_score` | 예측된 지역 기반 위험 점수 |
| `risk_grade_korean` | 위험 등급 한글값 |
| `main_risk_species` | 주의 가능성이 높은 동물 |
| `historical_count` | 예측에 참고된 과거 관측 수 |
| `message` | 사용자 안내 메시지 |
| `actions` | 권장 행동 요령 목록 |

모델 Feature:

| 구분 | Feature |
| --- | --- |
| 범주형 | `location`, `weather`, `time_zone`, `season`, `main_risk_species` |
| 수치형 | `historical_count`, `species_diversity`, `avg_object_count`, `avg_max_bbox_area_ratio`, `avg_avg_bbox_area_ratio` |
| Target | `area_risk_score` |

모델 성능:

| 지표 | 값 |
| --- | ---: |
| MAE | 1.766 |
| RMSE | 2.4457 |
| R2 Score | 0.9032 |

---

## 6. F-004 이미지/영상 탐지 화면

```text
GET /vision
```

사용자가 이미지 또는 짧은 영상을 업로드하여 야생동물 탐지 결과를 확인할 수 있는 화면을 제공한다.

관련 파일: `routes/vision_routes.py`, `services/vision_service.py`, `templates/vision.html`

---

## 7. F-005 이미지/영상 탐지 API

```text
POST /api/vision/predict
```

업로드된 이미지 또는 영상에서 YOLO 모델로 야생동물을 탐지하고, 탐지 결과를 반환한다.

---

## 8. F-006 대응 상담 화면

```text
GET /chat
```

사용자가 지역 조건과 질문을 입력하면, 위험도 예측 결과를 바탕으로 상담 답변을 제공하는 화면이다.

상담 모드:

| 모드 | 설명 |
| --- | --- |
| 상세 상담 모드 | 위험도 수치, 주요 동물, 위험 요인, 행동 요령을 자세히 설명 |
| 현장 대응 모드 | 빠르게 확인할 수 있는 행동 체크리스트 중심 안내 |

관련 파일: `routes/chat_routes.py`, `services/chat_service.py`, `templates/chat.html`

---

## 9. F-007 대응 상담 API

```text
POST /api/chat/message
```

Request:

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

Response 주요 필드:

| 필드 | 설명 |
| --- | --- |
| `answer` | 상담 답변 |
| `consultation_mode` | 상담 모드 |
| `mode_name` | 상담 모드 한글명 |
| `risk_result` | 위험도 예측 결과 |

---

## 10. F-008 회원 기능

회원가입, 로그인, 로그아웃 기능을 제공한다.

관련 파일: `routes/auth_routes.py`, `services/auth_service.py`, `templates/login.html`, `templates/register.html`

---

## 11. F-009 예측 기록

로그인 사용자의 위험도 예측 결과를 Oracle DB에 저장하고 조회한다.

관련 파일: `routes/risk_history_routes.py`, `services/risk_log_service.py`, `services/db_service.py`, `templates/risk_history.html`
