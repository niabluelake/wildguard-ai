# WildGuard AI 기능명세서

## 1. 문서 개요

본 문서는 WildGuard AI 서비스의 주요 기능을 정의한다.

WildGuard AI는 AI Hub 야생동물 라벨링 JSON 데이터를 기반으로 야생동물 관측 상황의 위험 점수를 예측하고, 이후 이미지 탐지와 대응 상담으로 확장하는 AI 서비스이다.

현재 1차 ML 프로젝트는 기존의 단순 위험 등급 분류 방식이 아니라, AI Hub JSON 메타데이터를 정형 데이터로 변환한 뒤 `risk_score`를 예측하는 회귀 모델 방식으로 구현한다.

---

## 2. 전체 기능 목록

| 기능 ID | 기능명            | 설명                          | 단계        | 상태    |
| ----- | -------------- | --------------------------- | --------- | ----- |
| F-001 | 메인 화면          | WildGuard AI 소개 및 기능 이동     | 공통        | 완료    |
| F-002 | AI Hub JSON 변환 | 라벨링 JSON을 ML용 CSV로 변환       | 1차 ML     | 완료    |
| F-003 | 위험 점수 생성       | 도메인 가중치 기반 `risk_score` 생성  | 1차 ML     | 완료    |
| F-004 | 위험 점수 회귀 모델 학습 | `risk_score`를 예측하는 회귀 모델 학습 | 1차 ML     | 완료    |
| F-005 | 위험 점수 예측 API   | 입력 조건 기반 위험 점수 예측           | 1차 ML     | 완료    |
| F-006 | 위험도 예측 화면      | 웹 화면에서 위험 점수 예측 결과 표시       | 1차 ML     | 수정 예정 |
| F-007 | 예측 기록 저장       | 로그인 사용자 예측 결과 DB 저장         | 공통        | 일부 구현 |
| F-008 | 예측 기록 조회       | 사용자별 위험도 예측 기록 조회           | 공통        | 일부 구현 |
| F-009 | YOLO 라벨 변환     | JSON bbox를 YOLO 학습 포맷으로 변환  | 2차 Vision | 예정    |
| F-010 | 이미지 탐지 API     | 이미지 업로드 후 야생동물 탐지           | 2차 Vision | 예정    |
| F-011 | 탐지 결과 이미지 저장   | bbox가 표시된 결과 이미지 저장         | 2차 Vision | 예정    |
| F-012 | LLM 대응 상담      | 예측/탐지 결과 기반 대응 상담           | 3차 LLM    | 예정    |
| F-013 | SLM 경량 상담      | 현장용 경량 상담 모델 제공             | 4차 SLM    | 예정    |

---

## 3. F-001 메인 화면

### 기능 설명

WildGuard AI 서비스의 메인 페이지를 제공한다.

### 주요 내용

* 서비스 소개
* 1차 위험 점수 예측 기능 이동
* 2차 이미지 탐지 기능 이동
* 향후 LLM/SLM 상담 기능 안내

### 관련 파일

| 구분  | 파일                      |
| --- | ----------------------- |
| 라우트 | `routes/main_routes.py` |
| 템플릿 | `templates/index.html`  |

---

## 4. F-002 AI Hub JSON 변환

### 기능 설명

AI Hub 야생동물 라벨링 JSON을 읽어 머신러닝 학습 가능한 CSV 파일로 변환한다.

1차 ML에서는 이미지 자체를 학습하지 않고, JSON 내부의 이미지 메타데이터와 annotation 정보를 정형 컬럼으로 변환한다.

### 입력 경로

```text
data/aihub/aihub_json/TL-quadruped/
```

### 출력 경로

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
```

### 실행 명령어

```cmd
python scripts\convert_aihub_json_to_csv.py
```

### 처리 내용

| 처리 항목      | 설명                              |
| ---------- | ------------------------------- |
| JSON 탐색    | `TL-quadruped` 하위 JSON 파일 재귀 탐색 |
| 이미지 정보 추출  | 파일명, 주야간 여부, 카메라 타입 추출          |
| 환경 정보 추출   | 날씨, 위치, 시간대, 계절 추출              |
| 객체 정보 추출   | 동물 종, 객체 수 추출                   |
| bbox 정보 계산 | 최대 bbox 면적 비율, 평균 bbox 면적 비율 계산 |
| 위험 점수 생성   | `risk_score` 생성                 |
| 위험 등급 생성   | `risk_grade`, `risk_level` 생성   |
| CSV 저장     | ML 학습용 CSV 저장                   |

### 출력 컬럼

| 컬럼                    | 설명                   |
| --------------------- | -------------------- |
| `json_file`           | 원본 JSON 파일 경로 또는 파일명 |
| `file_name`           | 이미지 파일명              |
| `day`                 | 주간 / 야간 촬영 여부        |
| `camera_type`         | RGB / IR 카메라 유형      |
| `weather`             | 촬영 당시 날씨             |
| `location`            | 촬영 위치                |
| `time_zone`           | 시간대                  |
| `season`              | 계절                   |
| `species`             | 관측된 야생동물 종           |
| `object_count`        | annotation 객체 수      |
| `max_bbox_area_ratio` | 가장 큰 bbox 면적 비율      |
| `avg_bbox_area_ratio` | 평균 bbox 면적 비율        |
| `risk_score`          | 위험 점수                |
| `risk_grade`          | 점수 기반 위험 등급          |
| `risk_level`          | 기존 코드 호환용 위험 등급      |

### 현재 변환 결과

| 항목        |      값 |
| --------- | -----: |
| JSON 파일 수 | 30,700 |
| CSV 행 수   | 30,700 |
| CSV 컬럼 수  |     15 |

---

## 5. F-003 위험 점수 생성

### 기능 설명

AI Hub 원본 JSON에는 실제 사고 피해 점수나 위험 점수가 포함되어 있지 않다.

따라서 본 프로젝트에서는 야생동물 관측 상황을 수치화하기 위해 도메인 가중치 기반의 `risk_score`를 생성한다.

### 점수 생성 요소

| 요소          | 반영 이유                           |
| ----------- | ------------------------------- |
| 동물 종        | 종에 따라 사람, 농작물, 시설물에 미치는 위험도가 다름 |
| 시간대         | 야간과 새벽은 시야 확보와 현장 대응이 어려움       |
| 날씨          | 비, 눈 등은 현장 대응 난도를 높일 수 있음       |
| 객체 수        | 여러 개체가 동시에 관측되면 위험도가 높아질 수 있음   |
| bbox 면적 비율  | 화면에서 크게 잡힌 객체는 카메라와 가까울 가능성이 있음 |
| IR 야간 촬영 여부 | 야간 출현 상황일 가능성이 높음               |

### 위험 점수 범위

```text
risk_score = 0 ~ 100
```

### 위험 등급 변환 기준

| risk_score   | risk_grade |
| ------------ | ---------- |
| 0 이상 45 미만   | low        |
| 45 이상 70 미만  | medium     |
| 70 이상 100 이하 | high       |

### 현재 위험 등급 분포

| risk_grade |  count |
| ---------- | -----: |
| medium     | 19,685 |
| high       | 10,343 |
| low        |    672 |

### 현재 위험 점수 통계

| 항목   |     값 |
| ---- | ----: |
| mean | 62.59 |
| std  |  8.29 |
| min  | 26.33 |
| max  | 88.00 |

---

## 6. F-004 위험 점수 회귀 모델 학습

### 기능 설명

변환된 CSV를 사용하여 `risk_score`를 예측하는 회귀 모델을 학습한다.

### 모델 유형

```text
지도학습 기반 회귀 모델
```

### 사용 모델

```text
RandomForestRegressor
```

### 입력 데이터

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
```

### 학습 스크립트

```text
scripts/train_risk_model.py
```

### 실행 명령어

```cmd
python scripts\train_risk_model.py
```

### 입력 Feature

| 구분  | 컬럼                                                                            |
| --- | ----------------------------------------------------------------------------- |
| 범주형 | `day`, `camera_type`, `weather`, `location`, `time_zone`, `season`, `species` |
| 수치형 | `object_count`, `max_bbox_area_ratio`, `avg_bbox_area_ratio`                  |

### Target

```text
risk_score
```

### 저장 모델

```text
models/ml/risk_regression_model.pkl
```

### 모델 성능

| 지표       |      값 |
| -------- | -----: |
| MAE      | 0.0183 |
| RMSE     | 0.2324 |
| R2 Score | 0.9992 |

### 성능 해석

현재 `risk_score`는 실제 사고 피해 데이터가 아니라, AI Hub 메타데이터 기반 도메인 가중치로 설계한 점수이다.

따라서 위 성능은 실제 사고 위험을 거의 완벽하게 예측했다는 의미가 아니라, 설계된 위험 점수 체계를 회귀 모델이 거의 정확하게 학습했다는 의미이다.

향후 실제 신고 데이터, 피해 기록, 기상 데이터, 지역 환경 데이터가 확보되면 현재의 `risk_score` 라벨을 실제 데이터 기반 라벨로 교체할 수 있다.

---

## 7. F-005 위험 점수 예측 API

### 기능 설명

사용자가 야생동물 관측 조건을 JSON으로 입력하면, 회귀 모델이 위험 점수 `predicted_score`를 예측하고 위험 등급과 대응 메시지를 반환한다.

### Endpoint

```text
POST /api/risk/predict
```

### 관련 파일

| 구분  | 파일                                    |
| --- | ------------------------------------- |
| 라우트 | `routes/risk_routes.py`               |
| 서비스 | `services/risk_prediction_service.py` |
| 모델  | `models/ml/risk_regression_model.pkl` |

### Request 필수 입력값

| 필드                    | 설명              |
| --------------------- | --------------- |
| `day`                 | 주간 / 야간 촬영 여부   |
| `camera_type`         | RGB / IR 카메라 유형 |
| `weather`             | 날씨              |
| `location`            | 위치              |
| `time_zone`           | 시간대             |
| `season`              | 계절              |
| `species`             | 동물 종            |
| `object_count`        | 객체 수            |
| `max_bbox_area_ratio` | 최대 bbox 면적 비율   |
| `avg_bbox_area_ratio` | 평균 bbox 면적 비율   |

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

## 8. F-006 위험도 예측 화면

### 기능 설명

사용자가 웹 화면에서 야생동물 관측 조건을 입력하고 위험 점수 예측 결과를 확인할 수 있도록 한다.

### URL

```text
GET /risk
```

### 입력 항목

| 항목            | 설명                    |
| ------------- | --------------------- |
| 주야간 여부        | `day`                 |
| 카메라 타입        | `camera_type`         |
| 날씨            | `weather`             |
| 위치            | `location`            |
| 시간대           | `time_zone`           |
| 계절            | `season`              |
| 동물 종          | `species`             |
| 객체 수          | `object_count`        |
| 최대 bbox 면적 비율 | `max_bbox_area_ratio` |
| 평균 bbox 면적 비율 | `avg_bbox_area_ratio` |

### 출력 항목

| 항목       | 설명                  |
| -------- | ------------------- |
| 예측 위험 점수 | `predicted_score`   |
| 위험 등급    | `risk_grade`        |
| 대응 메시지   | 위험 등급별 안내           |
| 모델 유형    | `regression`        |
| 모델 성능    | MAE, RMSE, R2 Score |

### 현재 상태

API는 회귀 모델과 연결되어 정상 동작한다.
웹 화면은 기존 위험 등급 중심 UI에서 위험 점수 중심 UI로 수정이 필요하다.

---

## 9. F-007 예측 기록 저장

### 기능 설명

로그인 사용자의 위험 점수 예측 결과를 DB에 저장한다.

### 현재 상태

현재 API 응답에는 저장 여부를 나타내는 필드가 포함되어 있다.

```json
{
  "saved": false,
  "saved_to_db": false
}
```

비회원 예측은 저장하지 않고, 로그인 사용자의 예측 결과만 저장하는 구조로 확장한다.

### 저장 대상

| 항목     | 설명                |
| ------ | ----------------- |
| 사용자 ID | 로그인 사용자 식별자       |
| 입력 데이터 | 예측 요청 JSON        |
| 예측 점수  | `predicted_score` |
| 위험 등급  | `risk_grade`      |
| 메시지    | 대응 안내             |
| 생성 시각  | 예측 실행 시간          |

---

## 10. F-008 예측 기록 조회

### 기능 설명

사용자가 본인의 위험 점수 예측 기록을 조회한다.

### 사용자별 권한

| 사용자     | 조회 범위           |
| ------- | --------------- |
| 비회원     | 조회 불가           |
| 일반 사용자  | 본인 기록           |
| 농장주     | 본인 기록           |
| 산림관리원   | 본인 기록           |
| 지자체 담당자 | 전체 기록 조회로 확장 가능 |
| 관리자     | 전체 기록 조회 가능     |

---

## 11. F-009 YOLO 라벨 변환

### 기능 설명

AI Hub JSON의 bbox annotation을 YOLO 학습용 txt 라벨로 변환한다.

### 입력

```text
AI Hub 원본 이미지
AI Hub 라벨링 JSON
```

### 출력

```text
YOLO images/train
YOLO images/val
YOLO labels/train
YOLO labels/val
data.yaml
```

### 예정 기능

* bbox 좌표 정규화
* train/val 분리
* YOLO 클래스 정의
* data.yaml 생성

---

## 12. F-010 이미지 탐지 API

### 기능 설명

사용자가 이미지를 업로드하면 YOLO 모델이 야생동물을 탐지하고 결과를 반환한다.

### 예정 Endpoint

```text
POST /api/vision/predict
```

### 출력 항목

| 항목               | 설명             |
| ---------------- | -------------- |
| class_name       | 탐지 클래스         |
| confidence       | 탐지 신뢰도         |
| bbox             | 탐지 좌표          |
| result_image_url | bbox 표시 결과 이미지 |
| risk_hint        | 탐지 기반 위험 안내    |

---

## 13. F-011 LLM 대응 상담

### 기능 설명

위험 점수 예측 결과와 이미지 탐지 결과를 바탕으로 사용자 상황에 맞는 야생동물 대응 상담을 제공한다.

### 상담 예시

```text
야간 산림 인근에서 멧돼지가 크게 관측되어 위험 점수가 높게 예측되었습니다.
현장 접근을 피하고, 주변 시설물과 이동 경로를 확인하세요.
반복 출현이 확인되면 관계 기관에 신고하거나 차단 장치를 점검하세요.
```

---

## 14. F-012 SLM 경량 상담

### 기능 설명

현장 환경에서 빠르게 사용할 수 있는 경량 상담 모델을 제공한다.

### 목표

* 낮은 사양 환경에서 실행 가능
* 짧은 대응 안내 생성
* 인터넷 연결이 불안정한 환경에서도 기본 상담 가능

---

## 15. GitHub 업로드 제외 대상

다음 파일은 GitHub에 업로드하지 않는다.

```text
data/
models/ml/
*.pkl
*.joblib
```

### 제외 이유

* AI Hub 원본 데이터는 용량과 라이선스 문제가 있음
* 변환 CSV는 스크립트로 재생성 가능함
* 학습 모델은 약 98MB로 GitHub 저장소를 무겁게 만듦
* 모델은 아래 명령어로 로컬에서 재생성 가능함

```cmd
python scripts\convert_aihub_json_to_csv.py
python scripts\train_risk_model.py
```

---

## 16. 현재 완료 상태

| 작업                             | 상태    |
| ------------------------------ | ----- |
| AI Hub JSON 30,700개 변환         | 완료    |
| `risk_score` 생성                | 완료    |
| `risk_grade` 생성                | 완료    |
| 회귀 모델 학습                       | 완료    |
| `risk_regression_model.pkl` 생성 | 완료    |
| `/api/risk/predict` 회귀 모델 연결   | 완료    |
| medium 테스트                     | 완료    |
| high 테스트                       | 완료    |
| 웹 화면 점수 표시                     | 수정 예정 |
| DB 저장 연동                       | 수정 예정 |
| YOLO 탐지 기능                     | 예정    |
| LLM 상담 기능                      | 예정    |
| SLM 경량화                        | 예정    |
