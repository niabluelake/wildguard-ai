# WildGuard AI 웹 서비스 명세서

## 1. 문서 개요

본 문서는 WildGuard AI 웹 서비스의 화면, API, 데이터 흐름, 사용자 동작 방식을 정의한다.

WildGuard AI는 AI Hub 야생동물 라벨링 JSON 메타데이터를 기반으로 야생동물 관측 상황의 위험 점수를 예측하고, 향후 이미지 탐지와 대응 상담 기능으로 확장하는 웹 기반 AI 서비스이다.

현재 웹 서비스의 핵심 기능은 1차 ML 프로젝트인 위험 점수 예측 기능이다.

---

## 2. 서비스 개요

### 서비스명

WildGuard AI

### 서비스 목적

야생동물 관측 조건을 입력하면 머신러닝 회귀 모델이 위험 점수 `risk_score`를 예측하고, 위험 등급과 대응 메시지를 제공한다.

### 주요 기능

| 구분           | 기능                  | 상태    |
| ------------ | ------------------- | ----- |
| 메인 화면        | 서비스 소개 및 기능 이동      | 완료    |
| 위험 점수 예측 화면  | 관측 조건 입력 및 위험 점수 확인 | 수정 예정 |
| 위험 점수 예측 API | `/api/risk/predict` | 완료    |
| 예측 기록 저장     | 로그인 사용자 결과 저장       | 일부 구현 |
| 예측 기록 조회     | 사용자별 기록 조회          | 일부 구현 |
| 이미지 탐지 화면    | 이미지 업로드 및 탐지 결과 표시  | 예정    |
| LLM 상담 화면    | 위험 상황 대응 상담         | 예정    |

---

## 3. 서비스 실행 환경

| 항목              | 내용                               |
| --------------- | -------------------------------- |
| OS              | Windows                          |
| IDE             | PyCharm                          |
| 터미널             | CMD 기준                           |
| Backend         | Python, Flask                    |
| ML              | scikit-learn, pandas, joblib     |
| Model           | RandomForestRegressor            |
| DB              | Oracle XE                        |
| Frontend        | HTML, CSS, JavaScript, Bootstrap |
| Version Control | Git, GitHub                      |

---

## 4. 프로젝트 실행 방법

### 4.1 프로젝트 이동

```cmd
cd /d E:\WildGuard_AI
```

또는 집 PC에서는 다음 경로를 사용한다.

```cmd
cd /d E:\Projects\wildguard-ai
```

### 4.2 가상환경 활성화

```cmd
.venv\Scripts\activate
```

### 4.3 패키지 설치

```cmd
pip install -r requirements.txt
```

### 4.4 AI Hub JSON 변환

```cmd
python scripts\convert_aihub_json_to_csv.py
```

생성 파일:

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
```

### 4.5 위험 점수 회귀 모델 학습

```cmd
python scripts\train_risk_model.py
```

생성 파일:

```text
models/ml/risk_regression_model.pkl
```

### 4.6 Flask 서버 실행

```cmd
python app.py
```

기본 접속 주소:

```text
http://127.0.0.1:5000/
```

---

## 5. 화면 구성

## 5.1 메인 화면

### URL

```text
GET /
```

### 목적

WildGuard AI 서비스 소개와 주요 기능 이동 버튼을 제공한다.

### 주요 표시 항목

| 항목        | 설명                        |
| --------- | ------------------------- |
| 서비스명      | WildGuard AI              |
| 서비스 설명    | 야생동물 위험 점수 예측 및 대응 지원 서비스 |
| 위험도 예측 이동 | `/risk` 페이지로 이동           |
| 이미지 탐지 이동 | Vision 기능 페이지로 이동         |
| 로그인 상태    | 로그인 여부에 따라 메뉴 표시          |

### 관련 파일

| 구분       | 파일                      |
| -------- | ----------------------- |
| Route    | `routes/main_routes.py` |
| Template | `templates/index.html`  |

---

## 5.2 위험 점수 예측 화면

### URL

```text
GET /risk
```

### 목적

사용자가 야생동물 관측 조건을 입력하고 위험 점수 예측 결과를 확인한다.

### 입력 항목

| 화면 항목         | API 필드                | 설명                              |
| ------------- | --------------------- | ------------------------------- |
| 주야간 여부        | `day`                 | day / night                     |
| 카메라 타입        | `camera_type`         | RGB / IR                        |
| 날씨            | `weather`             | sunny / cloudy / rain / snow    |
| 위치            | `location`            | 산림, 농장, 도로 등                    |
| 시간대           | `time_zone`           | dawn / day / evening / night    |
| 계절            | `season`              | spring / summer / fall / winter |
| 동물 종          | `species`             | 멧돼지, 고라니, 반달가슴곰, 멧토끼 등          |
| 객체 수          | `object_count`        | 감지된 객체 개수                       |
| 최대 bbox 면적 비율 | `max_bbox_area_ratio` | 가장 큰 객체의 화면 점유 비율               |
| 평균 bbox 면적 비율 | `avg_bbox_area_ratio` | 객체들의 평균 화면 점유 비율                |

### 출력 항목

| 출력 항목    | 설명                  |
| -------- | ------------------- |
| 예측 위험 점수 | `predicted_score`   |
| 위험 등급    | `risk_grade`        |
| 대응 메시지   | 위험 등급별 안내 문구        |
| 모델 유형    | `regression`        |
| 성능 지표    | MAE, RMSE, R2 Score |
| 저장 여부    | 로그인 사용자 DB 저장 여부    |

### 현재 상태

위험 점수 예측 API는 정상 동작한다.
웹 화면은 기존 위험 등급 중심 UI에서 위험 점수 중심 UI로 수정이 필요하다.

### 관련 파일

| 구분         | 파일                                    |
| ---------- | ------------------------------------- |
| Page Route | `routes/risk_page_routes.py`          |
| API Route  | `routes/risk_routes.py`               |
| Service    | `services/risk_prediction_service.py` |
| Template   | `templates/risk.html`                 |

---

## 5.3 예측 기록 화면

### URL

```text
GET /risk/history
```

### 목적

로그인 사용자가 본인의 위험 점수 예측 기록을 조회한다.

### 표시 항목

| 항목     | 설명                |
| ------ | ----------------- |
| 예측 일시  | 예측 실행 시간          |
| 입력 조건  | 사용자가 입력한 관측 조건    |
| 예측 점수  | `predicted_score` |
| 위험 등급  | `risk_grade`      |
| 대응 메시지 | 위험 등급별 안내         |
| 저장 상태  | DB 저장 여부          |

### 현재 상태

기존 예측 기록 구조가 일부 구현되어 있다.
회귀 모델 응답 구조에 맞춰 저장 컬럼과 화면 표시 항목을 수정해야 한다.

### 관련 파일

| 구분       | 파일                              |
| -------- | ------------------------------- |
| Route    | `routes/risk_history_routes.py` |
| Service  | `services/risk_log_service.py`  |
| Template | `templates/risk_history.html`   |

---

## 5.4 이미지 탐지 화면

### URL

```text
GET /vision
```

### 목적

사용자가 이미지를 업로드하면 YOLO 모델이 야생동물을 탐지하고 결과를 표시한다.

### 현재 상태

2차 Vision 프로젝트에서 확장 예정이다.

### 예정 입력 항목

| 항목     | 설명            |
| ------ | ------------- |
| 이미지 파일 | 야생동물이 포함된 이미지 |

### 예정 출력 항목

| 항목         | 설명                  |
| ---------- | ------------------- |
| 탐지 클래스     | 탐지된 동물 또는 quadruped |
| confidence | 탐지 신뢰도              |
| bbox       | 탐지 좌표               |
| 결과 이미지     | bbox가 표시된 이미지       |
| 위험 안내      | 탐지 결과 기반 안내         |

### 관련 파일

| 구분       | 파일                           |
| -------- | ---------------------------- |
| Route    | `routes/vision_routes.py`    |
| Service  | `services/vision_service.py` |
| Template | Vision 화면 템플릿                |

---

## 6. API 명세

## 6.1 위험 점수 예측 API

### Endpoint

```text
POST /api/risk/predict
```

### 설명

사용자가 입력한 야생동물 관측 조건을 기반으로 회귀 모델이 위험 점수를 예측한다.

### Request Header

```text
Content-Type: application/json
```

### Request Body

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

### Request 필드

| 필드                    | 타입     | 필수 여부 | 설명            |
| --------------------- | ------ | ----- | ------------- |
| `day`                 | string | 필수    | 주간 / 야간 여부    |
| `camera_type`         | string | 필수    | RGB / IR      |
| `weather`             | string | 필수    | 날씨            |
| `location`            | string | 필수    | 관측 위치         |
| `time_zone`           | string | 필수    | 시간대           |
| `season`              | string | 필수    | 계절            |
| `species`             | string | 필수    | 동물 종          |
| `object_count`        | number | 필수    | 객체 수          |
| `max_bbox_area_ratio` | number | 필수    | 최대 bbox 면적 비율 |
| `avg_bbox_area_ratio` | number | 필수    | 평균 bbox 면적 비율 |

### Response Body

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

### Response 필드

| 필드                       | 설명                          |
| ------------------------ | --------------------------- |
| `success`                | 요청 성공 여부                    |
| `result.predicted_score` | 모델이 예측한 위험 점수               |
| `result.risk_score`      | predicted_score와 동일한 호환용 필드 |
| `result.risk_grade`      | 점수 기반 위험 등급                 |
| `result.risk_level`      | 기존 코드 호환용 위험 등급             |
| `result.model_type`      | 모델 유형                       |
| `result.message`         | 위험 등급별 대응 메시지               |
| `result.metrics`         | 모델 성능 지표                    |
| `result.input`           | 요청 입력값                      |
| `saved`                  | 저장 여부                       |
| `saved_to_db`            | DB 저장 여부                    |

---

## 6.2 High 위험도 테스트 API 예시

### Request

```cmd
curl -X POST http://127.0.0.1:5000/api/risk/predict -H "Content-Type: application/json" -d "{\"day\":\"night\",\"camera_type\":\"IR\",\"weather\":\"rain\",\"location\":\"산림\",\"time_zone\":\"night\",\"season\":\"fall\",\"species\":\"멧돼지\",\"object_count\":4,\"max_bbox_area_ratio\":0.08,\"avg_bbox_area_ratio\":0.05}"
```

### Response 핵심 결과

```json
{
  "predicted_score": 84.37,
  "risk_grade": "high",
  "risk_level": "high",
  "model_type": "regression"
}
```

---

## 6.3 에러 응답

### JSON 요청 데이터 없음

```json
{
  "success": false,
  "message": "JSON 요청 데이터가 없습니다."
}
```

### 필수 입력 누락

```json
{
  "success": false,
  "message": "필수 입력이 없습니다: ['species']"
}
```

### 모델 파일 없음

```json
{
  "success": false,
  "message": "모델 파일이 없습니다: models/ml/risk_regression_model.pkl"
}
```

---

## 7. 위험 점수 기준

## 7.1 점수 범위

```text
risk_score = 0 ~ 100
```

## 7.2 등급 기준

| risk_score   | risk_grade | 설명    |
| ------------ | ---------- | ----- |
| 0 이상 45 미만   | low        | 낮은 위험 |
| 45 이상 70 미만  | medium     | 중간 위험 |
| 70 이상 100 이하 | high       | 높은 위험 |

## 7.3 대응 메시지

| 등급     | 메시지                                                          |
| ------ | ------------------------------------------------------------ |
| low    | 낮은 수준의 위험입니다. 즉각적인 대응보다는 관측 기록을 유지하는 것이 좋습니다.                |
| medium | 중간 수준의 위험입니다. 출현 조건을 확인하고 반복 관측 여부를 모니터링하세요.                 |
| high   | 위험 점수가 높습니다. 야생동물 근접 출현 가능성이 있으므로 현장 접근을 주의하고 주변 시설물을 점검하세요. |

---

## 8. 데이터 흐름

## 8.1 위험 점수 예측 흐름

```text
사용자 입력
↓
/risk 화면
↓
JavaScript fetch 요청
↓
POST /api/risk/predict
↓
routes/risk_routes.py
↓
services/risk_prediction_service.py
↓
risk_regression_model.pkl 로드
↓
RandomForestRegressor 예측
↓
predicted_score 반환
↓
risk_grade 변환
↓
대응 메시지 생성
↓
JSON 응답
↓
웹 화면 표시
```

---

## 9. 모델 파일 정책

학습 모델 파일은 GitHub에 업로드하지 않는다.

### 제외 파일

```text
models/ml/risk_regression_model.pkl
```

### 제외 이유

| 이유         | 설명                       |
| ---------- | ------------------------ |
| 용량         | 모델 파일 크기가 약 98MB         |
| 재생성 가능     | 학습 스크립트로 다시 생성 가능        |
| Git 저장소 관리 | 대용량 바이너리 파일은 저장소를 무겁게 만듦 |

### 모델 재생성 명령어

```cmd
python scripts\convert_aihub_json_to_csv.py
python scripts\train_risk_model.py
```

---

## 10. GitHub 업로드 제외 대상

다음 파일과 폴더는 GitHub에 업로드하지 않는다.

```text
data/
models/ml/
*.pkl
*.joblib
.env
```

### 제외 이유

| 대상             | 이유                    |
| -------------- | --------------------- |
| AI Hub 원본 JSON | 용량 및 라이선스 문제          |
| AI Hub 원천 이미지  | 용량 및 라이선스 문제          |
| 변환 CSV         | 스크립트로 재생성 가능          |
| 학습 모델          | 용량이 크고 재생성 가능         |
| `.env`         | DB 비밀번호 등 보안 정보 포함 가능 |

---

## 11. 사용자 권한

| 사용자 상태  | 가능 기능                     |
| ------- | ------------------------- |
| 비회원     | 위험 점수 예측 체험               |
| 로그인 사용자 | 위험 점수 예측, 결과 저장, 내 기록 조회  |
| 농장주     | 예측 결과 저장, 농장 주변 위험 확인     |
| 산림관리원   | 산림 지역 관측 기록 관리            |
| 지자체 담당자 | 전체 기록 조회 기능으로 확장 가능       |
| 관리자     | 사용자 및 전체 기록 관리 기능으로 확장 가능 |

---

## 12. 보안 요구사항

| 항목     | 요구사항                 |
| ------ | -------------------- |
| 비밀번호   | 해시 처리 후 저장           |
| 세션     | 로그인 사용자 정보는 세션에 저장   |
| 원본 데이터 | GitHub 업로드 금지        |
| 모델 파일  | GitHub 업로드 제외        |
| DB 정보  | `.env` 또는 로컬 설정으로 관리 |
| 입력 검증  | API 필수 입력값 검증        |

---

## 13. 현재 구현 상태

| 작업             | 상태    |
| -------------- | ----- |
| Flask 기본 서버    | 완료    |
| 메인 화면          | 완료    |
| AI Hub JSON 변환 | 완료    |
| 위험 점수 생성       | 완료    |
| 회귀 모델 학습       | 완료    |
| 위험 점수 예측 API   | 완료    |
| Medium API 테스트 | 완료    |
| High API 테스트   | 완료    |
| 위험 점수 중심 웹 화면  | 수정 예정 |
| 로그인 사용자 DB 저장  | 수정 예정 |
| 이미지 탐지 API     | 예정    |
| LLM 상담 화면      | 예정    |
| SLM 상담 화면      | 예정    |

---

## 14. 향후 수정 대상

| 파일                             | 수정 내용                                         |
| ------------------------------ | --------------------------------------------- |
| `templates/risk.html`          | `predicted_score`, `risk_grade`, `metrics` 표시 |
| `routes/risk_routes.py`        | 로그인 사용자 DB 저장 연동                              |
| `services/risk_log_service.py` | 회귀 모델 결과 저장 구조 반영                             |
| `templates/risk_history.html`  | 위험 점수 기록 표시                                   |
| `routes/vision_routes.py`      | 2차 Vision API 확장                              |
| `services/vision_service.py`   | YOLO 모델 연결                                    |
