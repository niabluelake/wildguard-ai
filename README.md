# WildGuard AI

WildGuard AI는 AI Hub 야생동물 관측 데이터와 YOLO 기반 이미지/영상 탐지를 활용하여 야생동물 출몰 위험도 예측, 탐지, 대응 상담을 제공하는 Flask 기반 AI 서비스입니다.

사용자는 관측 지역, 날씨, 시간대, 계절 조건을 입력하여 야생동물 출몰 위험 점수를 확인할 수 있고, 이미지/영상 탐지 및 대응 상담 챗봇을 통해 상황별 행동 요령을 확인할 수 있습니다.

---

## 주요 기능

| 기능 | 설명 | 상태 |
| --- | --- | --- |
| 위험도 예측 | AI Hub 관측 지역, 날씨, 시간대, 계절 조건 기반 야생동물 출몰 위험 점수 예측 | 구현 |
| 이미지/영상 탐지 | YOLO 기반 이미지 및 짧은 영상 내 야생동물 탐지 | 구현 |
| 대응 상담 챗봇 | 위험도 예측 결과를 바탕으로 상세 상담 및 현장 대응 안내 제공 | 구현 |
| 예측 기록 관리 | 로그인 사용자의 위험도 예측 결과를 Oracle DB에 저장 및 조회 | 구현/연동 중 |

---

## 서비스 흐름

```text
사용자 입력
  ├─ 지역명
  ├─ 날씨
  ├─ 시간대
  └─ 계절

AI Hub 관측 데이터 기반 지역 위험 프로필 생성
  └─ location / weather / time_zone / season 단위 집계

RandomForestRegressor 위험 점수 예측
  └─ predicted_score, risk_grade, main_risk_species 반환

웹 서비스 제공
  ├─ /risk 위험도 예측 화면
  ├─ /vision 이미지/영상 탐지 화면
  └─ /chat 대응 상담 챗봇
```

---

## 사용 데이터

원본 AI Hub 데이터는 용량과 라이선스 이슈로 GitHub에 업로드하지 않습니다.

```text
data/aihub/aihub_json/TL-quadruped/
```

로컬에서 생성되는 주요 데이터 파일은 다음과 같습니다.

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
data/aihub/ml_dataset/aihub_area_risk_dataset.csv
```

현재 프로젝트 기준 변환된 AI Hub JSON 수는 약 30,700개입니다.

---

## 위험도 예측 모델

### 모델 목적

AI Hub 야생동물 관측 메타데이터를 지역, 날씨, 시간대, 계절 단위로 집계하고, 해당 조건에서의 야생동물 출몰 위험 점수를 예측합니다.

### 입력값

| 필드 | 설명 |
| --- | --- |
| `location` | AI Hub 관측 데이터에 포함된 지역명 |
| `weather` | 날씨 |
| `time_zone` | 시간대 |
| `season` | 계절 |
| `region_name` | 사용자 화면에 표시할 별칭 |

### 모델 파일

```text
models/ml/area_risk_model.pkl
```

모델 파일은 GitHub에 업로드하지 않으며, 로컬에서 학습 스크립트를 실행해 생성합니다.

### 모델 성능

| 지표 | 값 |
| --- | ---: |
| MAE | 1.766 |
| RMSE | 2.4457 |
| R2 Score | 0.9032 |

현재 위험 점수는 실제 사고 피해 데이터가 아니라 AI Hub 관측 메타데이터와 도메인 가중치를 바탕으로 설계한 점수입니다. 따라서 모델 성능은 실제 사고 발생을 직접 예측했다는 의미가 아니라, 설계된 지역 기반 위험 점수 체계를 모델이 얼마나 잘 학습했는지를 의미합니다.

---

## 주요 파일

| 구분 | 파일 |
| --- | --- |
| Flask 앱 진입점 | `app.py` |
| 메인 라우트 | `routes/main_routes.py` |
| 위험도 예측 API | `routes/risk_routes.py` |
| 위험도 예측 페이지 | `routes/risk_page_routes.py` |
| 예측 기록 라우트 | `routes/risk_history_routes.py` |
| 이미지/영상 탐지 라우트 | `routes/vision_routes.py` |
| 대응 상담 챗봇 라우트 | `routes/chat_routes.py` |
| 위험도 예측 서비스 | `services/risk_prediction_service.py` |
| 대응 상담 서비스 | `services/chat_service.py` |
| 이미지/영상 탐지 서비스 | `services/vision_service.py` |
| AI Hub JSON 변환 | `scripts/convert_aihub_json_to_csv.py` |
| 지역 위험 데이터셋 생성 | `scripts/create_area_risk_dataset.py` |
| 지역 위험 모델 학습 | `scripts/train_area_risk_model.py` |
| 메인 화면 | `templates/index.html` |
| 위험도 예측 화면 | `templates/risk.html` |
| 대응 상담 화면 | `templates/chat.html` |

---

## 실행 방법

### 1. 프로젝트 이동

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

이미 `aihub_wildlife_metadata.csv`가 있다면 생략할 수 있습니다.

```cmd
python scripts\convert_aihub_json_to_csv.py
```

### 5. 지역 위험 데이터셋 생성

```cmd
python scripts\create_area_risk_dataset.py
```

### 6. 지역 위험 모델 학습

```cmd
python scripts\train_area_risk_model.py
```

실행 후 아래 파일이 생성됩니다.

```text
models/ml/area_risk_model.pkl
```

### 7. Flask 서버 실행

```cmd
python app.py
```

브라우저 접속:

```text
http://127.0.0.1:5000/
```

---

## 주요 화면

| URL | 설명 |
| --- | --- |
| `/` | 메인 화면 |
| `/risk` | 지역 기반 야생동물 위험도 예측 |
| `/vision` | 이미지/영상 기반 야생동물 탐지 |
| `/chat` | 위험도 기반 대응 상담 챗봇 |
| `/risk/history` | 로그인 사용자 예측 기록 조회 |

---

## API

### 위험도 예측 API

```text
POST /api/risk/predict
```

Request 예시:

```json
{
  "region_name": "집 근처",
  "location": "진전면",
  "weather": "rain",
  "time_zone": "night",
  "season": "fall"
}
```

### 대응 상담 API

```text
POST /api/chat/message
```

Request 예시:

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

상담 모드:

| 값 | 설명 |
| --- | --- |
| `detail` | 상세 상담 모드 |
| `field` | 현장 대응 모드 |

---

## Git 작업 규칙

작업 시작 전:

```cmd
git pull origin main
git status
```

작업 종료 후:

```cmd
git status
git add <수정한 파일>
git commit -m "커밋 메시지"
git pull --rebase origin main
git push origin main
git status
```

`.idea`, `.venv`, `data`, `models/ml` 등 로컬 환경 파일과 대용량 데이터/모델 파일은 GitHub에 업로드하지 않습니다.

---

## 향후 개선 방향

- 실제 GPS 기반 위치 데이터 연동
- 행정구역별 신고 데이터 추가
- 기상 API 및 실시간 날씨 데이터 연동
- 위험도 예측 결과와 이미지 탐지 결과 통합
- 상담 챗봇 답변 고도화
- 지역별 위험 지도 시각화
