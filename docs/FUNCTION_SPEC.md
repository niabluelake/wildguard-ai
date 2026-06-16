# WildGuard AI 기능명세서

## 1. 문서 개요

본 문서는 WildGuard AI 서비스의 주요 기능을 정의한다.

WildGuard AI는 AI Hub 야생동물 라벨링 JSON 데이터를 기반으로 야생동물 관측 상황의 위험 점수를 예측하고, 한국도로공사 로드킬 다발 구간 데이터를 외부 feature로 결합하여 현장 위험도 평가 결과를 제공하는 AI 서비스이다.

현재 1차 ML 프로젝트는 단순 위험 등급 분류 방식이 아니라, AI Hub JSON 메타데이터를 정형 데이터로 변환하고 GPS 기반 로드킬 hotspot feature를 결합한 뒤 `risk_score`를 예측하는 회귀 모델 방식으로 구현한다.

---

## 2. 전체 기능 목록

| 기능 ID | 기능명 | 설명 | 단계 | 상태 |
|---|---|---|---|---|
| F-001 | 메인 화면 | WildGuard AI 소개 및 기능 이동 | 공통 | 완료 |
| F-002 | AI Hub JSON 변환 | 라벨링 JSON을 ML용 CSV로 변환 | 1차 ML | 완료 |
| F-003 | GPS 컬럼 추가 | AI Hub JSON에서 관측 지점 latitude, longitude 추출 | 1차 ML | 완료 |
| F-004 | 로드킬 feature 결합 | 로드킬 다발 구간 데이터 기반 거리 feature 생성 | 1차 ML | 완료 |
| F-005 | 위험 점수 생성 | 도메인 가중치 및 로드킬 hotspot 기반 `risk_score` 생성 | 1차 ML | 완료 |
| F-006 | 위험 점수 회귀 모델 학습 | `risk_score`를 예측하는 회귀 모델 학습 | 1차 ML | 완료 |
| F-007 | 위험 점수 예측 API | 입력 조건 기반 위험 점수, 위험 요인, 대응 메시지 반환 | 1차 ML | 완료 |
| F-008 | 위험도 예측 화면 | 웹 화면에서 위험 점수, 위험 요인, 로드킬 feature 표시 | 1차 ML | 완료 |
| F-009 | 예측 기록 저장 | 로그인 사용자 예측 결과 DB 저장 | 공통 | 일부 구현 |
| F-010 | 예측 기록 조회 | 사용자별 위험도 예측 기록 조회 | 공통 | 일부 구현 |
| F-011 | 이미지 탐지 API | 이미지 업로드 후 야생동물 탐지 | 2차 Vision | 구현 |
| F-012 | 탐지 결과 이미지 저장 | bbox가 표시된 결과 이미지 저장 | 2차 Vision | 구현 |
| F-013 | LLM 대응 상담 | 예측/탐지 결과 기반 대응 상담 | 3차 LLM | 구현 |
| F-014 | SLM 경량 상담 | 현장용 경량 상담 모델 제공 | 4차 SLM | 예정 |

---

## 3. F-001 메인 화면

### 기능 설명

WildGuard AI 서비스의 메인 페이지를 제공한다.

### 주요 내용

- 서비스 소개
- 위험도 예측 기능 이동
- 이미지/영상 탐지 기능 이동
- 대응 상담 챗봇 기능 이동
- 로그인 상태에 따른 예측 기록 또는 회원가입 버튼 표시

### 관련 파일

| 구분 | 파일 |
|---|---|
| 라우트 | `routes/main_routes.py` |
| 템플릿 | `templates/index.html` |

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

| 처리 항목 | 설명 |
|---|---|
| JSON 탐색 | `TL-quadruped` 하위 JSON 파일 재귀 탐색 |
| 이미지 정보 추출 | 파일명, 주야간 여부, 카메라 타입 추출 |
| 환경 정보 추출 | 날씨, 위치, 시간대, 계절 추출 |
| 객체 정보 추출 | 동물 종, 객체 수 추출 |
| bbox 정보 계산 | 최대 bbox 면적 비율, 평균 bbox 면적 비율 계산 |
| 위험 점수 생성 | 기본 `risk_score` 생성 |
| 위험 등급 생성 | `risk_grade`, `risk_level` 생성 |
| CSV 저장 | ML 학습용 CSV 저장 |

### 현재 변환 결과

| 항목 | 값 |
|---|---:|
| JSON 파일 수 | 30,700 |
| CSV 행 수 | 30,700 |
| 기본 CSV 컬럼 수 | 15 |

---

## 5. F-003 GPS 컬럼 추가

### 기능 설명

기존 ML CSV에는 GPS 좌표가 없기 때문에, CSV의 `json_file` 경로를 기준으로 원본 JSON을 다시 읽어 관측 지점의 `latitude`, `longitude`를 추가한다.

### 입력 파일

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
```

### 출력 파일

```text
data/aihub/ml_dataset/aihub_wildlife_metadata_with_gps.csv
```

### 실행 명령어

```cmd
python scripts\add_gps_to_ml_dataset.py
```

### 추가 컬럼

| 컬럼 | 설명 |
|---|---|
| `latitude` | 관측 지점 위도 |
| `longitude` | 관측 지점 경도 |

### 관련 파일

| 구분 | 파일 |
|---|---|
| 스크립트 | `scripts/add_gps_to_ml_dataset.py` |

---

## 6. F-004 로드킬 feature 결합

### 기능 설명

한국도로공사 로드킬 다발 구간 데이터의 위도·경도와 발생건수를 활용하여 AI Hub 관측 지점 주변의 로드킬 hotspot feature를 생성한다.

### 입력 파일

```text
data/aihub/ml_dataset/aihub_wildlife_metadata_with_gps.csv
data/external/roadkill/roadkill_2019_2025_combined.csv
```

### 출력 파일

```text
data/aihub/ml_dataset/aihub_wildlife_metadata_enriched.csv
```

### 실행 명령어

```cmd
python scripts\enrich_ml_dataset_with_roadkill.py
```

### 생성 feature

| feature | 설명 |
|---|---|
| `nearest_roadkill_distance_km` | 가장 가까운 로드킬 다발 구간까지 거리 |
| `roadkill_count_within_5km` | 반경 5km 내 로드킬 발생건수 |
| `roadkill_count_within_10km` | 반경 10km 내 로드킬 발생건수 |
| `roadkill_count_within_20km` | 반경 20km 내 로드킬 발생건수 |
| `roadkill_max_cases_nearby` | 주변 로드킬 지점 중 최대 발생건수 |
| `roadkill_weighted_score` | 가까운 구간일수록 더 크게 반영한 로드킬 가중 점수 |
| `near_roadkill_hotspot` | 10km 내 로드킬 hotspot 존재 여부 |
| `risk_score_base` | 로드킬 반영 전 기존 위험 점수 |

### 최종 데이터셋

| 항목 | 값 |
|---|---:|
| 행 수 | 30,700 |
| 컬럼 수 | 25 |

---

## 7. F-005 위험 점수 생성

### 기능 설명

AI Hub 원본 JSON에는 실제 사고 피해 점수나 위험 점수가 포함되어 있지 않다.

따라서 본 프로젝트에서는 야생동물 관측 상황과 로드킬 hotspot 정보를 수치화하기 위해 도메인 가중치 기반의 `risk_score`를 생성한다.

### 점수 생성 요소

| 요소 | 반영 이유 |
|---|---|
| 동물 종 | 종에 따라 사람, 농작물, 시설물에 미치는 위험도가 다름 |
| 시간대 | 야간과 새벽은 시야 확보와 현장 대응이 어려움 |
| 날씨 | 비, 눈 등은 현장 대응 난도를 높일 수 있음 |
| 객체 수 | 여러 개체가 동시에 관측되면 위험도가 높아질 수 있음 |
| bbox 면적 비율 | 화면에서 크게 잡힌 객체는 카메라와 가까울 가능성이 있음 |
| IR 야간 촬영 여부 | 야간 출현 상황일 가능성이 높음 |
| 로드킬 다발 구간 거리 | 주변에 과거 야생동물 사고 다발 구간이 있으면 위험도가 높아질 수 있음 |
| 반경 내 로드킬 발생건수 | 관측 지점 주변 사고 이력을 위험도에 반영 |

### 위험 점수 범위

```text
risk_score = 0 ~ 100
```

### 위험 등급 변환 기준

| risk_score | risk_grade |
|---:|---|
| 0 이상 45 미만 | low |
| 45 이상 70 미만 | medium |
| 70 이상 100 이하 | high |

### 로드킬 반영 후 위험 등급 분포

| risk_grade | count |
|---|---:|
| medium | 18,285 |
| high | 12,053 |
| low | 362 |

### 로드킬 반영 후 위험 점수 통계

| 항목 | 값 |
|---|---:|
| mean | 66.32 |
| std | 8.39 |
| min | 30.33 |
| max | 100.00 |

---

## 8. F-006 위험 점수 회귀 모델 학습

### 기능 설명

로드킬 feature가 결합된 최종 CSV를 사용하여 `risk_score`를 예측하는 회귀 모델을 학습한다.

### 모델 유형

```text
RandomForestRegressor
```

### 입력 데이터

```text
data/aihub/ml_dataset/aihub_wildlife_metadata_enriched.csv
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

| 구분 | 컬럼 |
|---|---|
| 범주형 | `day`, `camera_type`, `weather`, `location`, `time_zone`, `season`, `species` |
| 수치형 | `object_count`, `max_bbox_area_ratio`, `avg_bbox_area_ratio`, `nearest_roadkill_distance_km`, `roadkill_count_within_5km`, `roadkill_count_within_10km`, `roadkill_count_within_20km`, `roadkill_max_cases_nearby`, `roadkill_weighted_score`, `near_roadkill_hotspot` |

### Target

```text
risk_score
```

### 저장 모델

```text
models/ml/risk_regression_model.pkl
```

### 모델 성능

| 지표 | 값 |
|---|---:|
| MAE | 0.0276 |
| RMSE | 0.2472 |
| R2 Score | 0.9991 |

### 성능 해석

현재 `risk_score`는 실제 사고 피해 데이터가 아니라, AI Hub 메타데이터와 로드킬 다발 구간 정보를 기반으로 설계한 점수이다.

따라서 위 성능은 실제 사고 위험을 거의 완벽하게 예측했다는 의미가 아니라, 설계된 위험 점수 체계를 회귀 모델이 얼마나 잘 학습했는지를 의미한다.

---

## 9. F-007 위험 점수 예측 API

### 기능 설명

사용자가 야생동물 관측 조건을 JSON으로 입력하면, 회귀 모델이 위험 점수 `predicted_score`를 예측하고 위험 등급, 위험 요인, 대응 메시지, 로드킬 feature 정보를 반환한다.

### Endpoint

```text
POST /api/risk/predict
```

### 관련 파일

| 구분 | 파일 |
|---|---|
| 라우트 | `routes/risk_routes.py` |
| 서비스 | `services/risk_prediction_service.py` |
| 모델 | `models/ml/risk_regression_model.pkl` |

### Request 필수 입력값

| 필드 | 설명 |
|---|---|
| `day` | 주간/야간 촬영 여부 |
| `camera_type` | RGB/IR 카메라 유형 |
| `weather` | 날씨 |
| `location` | 위치 |
| `time_zone` | 시간대 |
| `season` | 계절 |
| `species` | 동물 종 |
| `object_count` | 객체 수 |
| `max_bbox_area_ratio` | 최대 bbox 면적 비율 |
| `avg_bbox_area_ratio` | 평균 bbox 면적 비율 |

### Request 예시

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

### Response 예시

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

## 10. F-008 위험도 예측 화면

### 기능 설명

사용자가 웹 화면에서 야생동물 관측 조건을 입력하고 위험 점수 예측 결과를 확인할 수 있도록 한다.

### URL

```text
GET /risk
```

### 입력 항목

| 항목 | 설명 |
|---|---|
| 지역 이름 | 사용자가 알아보기 쉬운 별칭 |
| 위험도를 확인할 지역 | AI Hub 관측 지역 |
| 날씨 | sunny, cloudy, rain, snow |
| 시간대 | dawn, day, evening, night |
| 계절 | spring, summer, fall, winter |

현재 웹 화면은 사용성 유지를 위해 종, 객체 수, bbox 면적 비율을 직접 입력받지 않고 기본 관측 시나리오 값을 API 요청에 포함한다.

### 출력 항목

| 항목 | 설명 |
|---|---|
| 예측 위험 점수 | `predicted_score` |
| 위험 등급 | `predicted_grade_ko` |
| 위험도 설명 | `message` 또는 `action_message` |
| 주요 위험 요인 | `risk_reasons` |
| 현장 대응 가이드 | `action_message` |
| 로드킬 다발 구간 기반 외부 feature | `roadkill_features` |
| 모델 성능 지표 | MAE, RMSE, R2 Score |

### 현재 상태

API와 웹 화면이 연결되어 위험 점수, 위험 요인, 대응 메시지, 로드킬 feature를 화면에 표시한다.

---

## 11. F-009 예측 기록 저장

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

| 항목 | 설명 |
|---|---|
| 사용자 ID | 로그인 사용자 식별자 |
| 입력 데이터 | 예측 요청 JSON |
| 예측 점수 | `predicted_score` |
| 위험 등급 | `predicted_grade` |
| 위험 요인 | `risk_reasons` |
| 메시지 | 대응 안내 |
| 생성 시각 | 예측 실행 시간 |

---

## 12. F-010 예측 기록 조회

### 기능 설명

사용자가 본인의 위험 점수 예측 기록을 조회한다.

### 사용자별 권한

| 사용자 | 조회 범위 |
|---|---|
| 비회원 | 조회 불가 |
| 일반 사용자 | 본인 기록 |
| 농장주 | 본인 기록 |
| 산림관리원 | 본인 기록 |
| 지자체 담당자 | 전체 기록 조회로 확장 가능 |
| 관리자 | 전체 기록 조회 가능 |

---

## 13. F-011 이미지 탐지 API

### 기능 설명

사용자가 이미지를 업로드하면 YOLO 모델이 야생동물을 탐지하고 결과를 반환한다.

### Endpoint

```text
POST /api/vision/predict
```

### 출력 항목

| 항목 | 설명 |
|---|---|
| class_name | 탐지 클래스 |
| confidence | 탐지 신뢰도 |
| bbox | 탐지 좌표 |
| result_image_url | bbox 표시 결과 이미지 |
| risk_hint | 탐지 기반 위험 안내 |

---

## 14. F-012 LLM 대응 상담

### 기능 설명

위험 점수 예측 결과와 이미지 탐지 결과를 바탕으로 사용자 상황에 맞는 야생동물 대응 상담을 제공한다.

### 상담 예시

```text
야간 산림 인근에서 멧돼지가 크게 관측되어 위험 점수가 높게 예측되었습니다.
주변 20km 이내 로드킬 다발 구간도 확인되었으므로 현장 접근을 피하고,
주변 시설물과 이동 경로를 확인하세요.
```

---

## 15. F-013 SLM 경량 상담

### 기능 설명

현장 환경에서 빠르게 사용할 수 있는 경량 상담 모델을 제공한다.

### 목표

- 낮은 사양 환경에서 실행 가능
- 짧은 대응 안내 생성
- 인터넷 연결이 불안정한 환경에서도 기본 상담 가능

---

## 16. GitHub 업로드 제외 대상

다음 파일은 GitHub에 업로드하지 않는다.

```text
data/
models/ml/
*.pkl
*.joblib
*.csv
```

### 제외 이유

- AI Hub 원본 데이터는 용량과 라이선스 문제가 있음
- 로드킬 통합 CSV는 외부 공공데이터 기반으로 로컬에서 관리함
- 변환 CSV는 스크립트로 재생성 가능함
- 학습 모델은 GitHub 저장소를 무겁게 만들 수 있음
- 모델은 아래 명령어로 로컬에서 재생성 가능함

```cmd
python scripts\convert_aihub_json_to_csv.py
python scripts\add_gps_to_ml_dataset.py
python scripts\enrich_ml_dataset_with_roadkill.py
python scripts\train_risk_model.py
```

---

## 17. 현재 완료 상태

| 작업 | 상태 |
|---|---|
| AI Hub JSON 30,700개 변환 | 완료 |
| GPS 좌표 추출 | 완료 |
| 로드킬 통합 CSV 준비 | 완료 |
| 로드킬 거리 기반 feature 생성 | 완료 |
| `risk_score` 생성 | 완료 |
| `risk_grade` 생성 | 완료 |
| 회귀 모델 학습 | 완료 |
| `risk_regression_model.pkl` 생성 | 완료 |
| `/api/risk/predict` 회귀 모델 연결 | 완료 |
| 위험 요인 설명 반환 | 완료 |
| 현장 대응 메시지 반환 | 완료 |
| 로드킬 feature 반환 | 완료 |
| 웹 화면 상세 위험 분석 표시 | 완료 |
| DB 저장 연동 | 일부 구현 |
| YOLO 탐지 기능 | 구현 |
| LLM 상담 기능 | 구현 |
| SLM 경량화 | 예정 |
