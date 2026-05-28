# WildGuard AI 기능명세서

## 1. 문서 개요

본 문서는 WildGuard AI의 기능을 정의한다. 현재 프로젝트는 AI Hub 야생동물 라벨링 데이터를 기반으로 1차 정형 데이터 ML, 2차 YOLO 객체 탐지, 3차 LLM 상담, 4차 SLM 상담으로 확장하는 구조이다.

---

## 2. 전체 기능 목록

| 기능 ID | 기능명 | 설명 | 단계 |
|---|---|---|---|
| F-001 | 프로젝트 기본 화면 | WildGuard AI 소개 및 주요 기능 이동 | 공통 |
| F-002 | AI Hub JSON 메타데이터 변환 | 라벨링 JSON을 1차 ML용 CSV로 변환 | 1차 |
| F-003 | 위험도 라벨 생성 | 객체 수, bbox 크기, 시간대를 기준으로 risk_level 생성 | 1차 |
| F-004 | 위험도 예측 모델 학습 | 변환 CSV로 위험도 분류 모델 학습 | 1차 |
| F-005 | 위험도 예측 API | 사용자 입력값 기반 위험도 예측 결과 반환 | 1차 |
| F-006 | 위험도 예측 화면 | 웹에서 위험도 입력 및 결과 확인 | 1차 |
| F-007 | YOLO 라벨 변환 | JSON bbox를 YOLO txt 형식으로 변환 | 2차 |
| F-008 | 이미지 탐지 API | 이미지 업로드 후 사족보행 야생동물 탐지 | 2차 |
| F-009 | 탐지 결과 이미지 저장 | bbox가 표시된 결과 이미지를 저장 | 2차 |
| F-010 | LLM 상담 | 예측/탐지 결과 기반 대응 상담 제공 | 3차 |
| F-011 | SLM 경량 상담 | 현장용 경량 상담 응답 제공 | 4차 |
| F-012 | Oracle DB 결과 저장 | 예측, 탐지, 상담 결과 저장 | 공통 |
| F-013 | 결과 조회 | 저장된 분석 결과 조회 | 공통 |

---

## 3. F-001 프로젝트 기본 화면

### 기능 설명
서비스 소개와 1차 위험도 예측, 2차 이미지 탐지, 3차 상담 기능으로 이동할 수 있는 메인 화면을 제공한다.

### URL
```http
GET /
```

### 출력
서비스명, 프로젝트 설명, 1차 위험도 예측 페이지 링크, 2차 이미지 탐지 페이지 링크, 3차 상담 페이지 링크

### 필요 이유
사용자가 WildGuard AI의 전체 기능 흐름을 이해하고 각 기능으로 이동할 수 있어야 하기 때문이다.

---

## 4. F-002 AI Hub JSON 메타데이터 변환

### 기능 설명
AI Hub 라벨링 JSON 파일을 읽어 머신러닝 학습 가능한 CSV 데이터셋으로 변환한다.

### 입력 경로
```text
data/aihub_json/TL-quadruped
```

### 출력 경로
```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
```

### 실행 명령어
```powershell
python scripts/convert_aihub_metadata.py
```

### 처리 내용
JSON 파일 재귀 탐색, 이미지 메타데이터 추출, annotation 정보 추출, 객체 수 계산, bbox 면적 비율 계산, 시간대와 계절 생성, risk_level 생성, CSV 저장

### 출력 컬럼
`json_file`, `image_id`, `file_name`, `width`, `height`, `date_created`, `hour`, `time_zone`, `season`, `day`, `camera_type`, `location`, `gps`, `weather`, `object_count`, `species`, `category_name`, `hazardous`, `nocturnality`, `max_bbox_area_ratio`, `avg_bbox_area_ratio`, `risk_level`

### 현재 처리 결과
```text
데이터 크기: 30,700행 x 22컬럼
medium: 18,694
high: 10,196
low: 1,810
```

### 필요 이유
원본 JSON은 ML 모델이 직접 학습하기 어렵다. 따라서 이미지 메타데이터와 annotation 정보를 정형 컬럼으로 변환해야 1차 머신러닝 프로젝트로 사용할 수 있다.

---

## 5. F-003 위험도 라벨 생성

### 기능 설명
원본 데이터에 없는 위험도 라벨을 프로젝트 목적에 맞게 생성한다.

### 기준 컬럼
`object_count`, `max_bbox_area_ratio`, `time_zone`, `day`

### 점수 규칙
| 조건 | 점수 |
|---|---:|
| object_count >= 3 | +2 |
| object_count == 2 | +1 |
| max_bbox_area_ratio >= 0.05 | +2 |
| max_bbox_area_ratio >= 0.02 | +1 |
| time_zone이 night 또는 dawn | +1 |
| day가 night | +1 |

### 분류 규칙
| 점수 | risk_level |
|---|---|
| 0~1 | low |
| 2~3 | medium |
| 4 이상 | high |

### 필요 이유
AI Hub 라벨링 데이터에는 `hazardous`와 `nocturnality`는 있지만 서비스용 위험도 라벨은 없다. 객체 수와 bbox 크기, 야간 여부를 이용해 상황 위험도를 생성해야 ML 분류 모델 학습이 가능하다.

---

## 6. F-004 위험도 예측 모델 학습

### 기능 설명
변환된 CSV 데이터셋을 사용하여 위험도 분류 모델을 학습한다.

### 입력 데이터
```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
```

### 추천 Feature
| 구분 | 컬럼 |
|---|---|
| 범주형 | day, camera_type, weather, location, time_zone, season |
| 수치형 | object_count, max_bbox_area_ratio, avg_bbox_area_ratio |

### Target
`risk_level`

### 제외 권장 컬럼
`hazardous`, `nocturnality`, `species`, `file_name`, `json_file`

### 저장 모델
```text
models/ml/risk_model.pkl
```

### 필요 이유
규칙 기반 라벨 생성만으로 끝내면 머신러닝 프로젝트로 보이기 어렵다. 변환된 정형 데이터를 기반으로 실제 분류 모델을 학습해야 1차 ML 프로젝트가 완성된다.

---

## 7. F-005 위험도 예측 API

### URL
```http
POST /api/risk/predict
```

### Request 예시
```json
{
  "day": "night",
  "camera_type": "IR",
  "weather": "cloudy",
  "location": "대산농원",
  "time_zone": "night",
  "season": "fall",
  "object_count": 2,
  "max_bbox_area_ratio": 0.0235,
  "avg_bbox_area_ratio": 0.0206
}
```

### Response 예시
```json
{
  "risk_level": "medium",
  "message": "야간에 사족보행 야생동물이 탐지되어 주의가 필요합니다."
}
```

### 필요 이유
Flask 웹 서비스와 ML 모델을 연결하기 위해 API 형태의 예측 기능이 필요하다.

---

## 8. F-006 위험도 예측 화면

### URL
```http
GET /risk/
POST /risk/
```

### 입력 항목
주야간 여부, 카메라 타입, 날씨, 위치, 시간대, 계절, 객체 수, bbox 면적 비율

### 출력 항목
위험도, 위험도 설명, 대응 메시지

### 필요 이유
비전문가가 API를 직접 호출하지 않고 웹 화면에서 결과를 확인할 수 있어야 한다.

---

## 9. F-007 YOLO 라벨 변환

### 기능 설명
AI Hub JSON의 bbox 좌표를 YOLO 학습용 txt 라벨로 변환한다.

### 출력 형식
```text
class_id x_center y_center width height
```

### 클래스 정책
초기 모델은 사족보행 야생동물을 하나의 클래스로 통합한다.

```text
class 0 = quadruped
```

### 필요 이유
멧돼지 데이터가 대부분이고 고라니, 반달가슴곰, 멧토끼 데이터는 적다. 클래스별 불균형을 줄이고, 현장에서 위험 가능 사족보행 객체가 있는지 먼저 탐지하기 위해 단일 클래스가 적합하다.

---

## 10. F-008 이미지 탐지 API

### URL
```http
POST /api/vision/detect
```

### Request
```text
multipart/form-data
image: 업로드 이미지
```

### Response 예시
```json
{
  "detected": true,
  "count": 1,
  "detections": [
    {
      "class_id": 0,
      "class_name": "quadruped",
      "confidence": 0.87,
      "bbox": [120, 80, 420, 360],
      "risk_level": "danger"
    }
  ],
  "result_image_url": "/static/outputs/result_001.jpg"
}
```

### 필요 이유
2차 프로젝트의 핵심은 이미지 기반 객체 탐지이다. REST API로 구현하면 Flask 서비스와 프론트엔드에서 쉽게 사용할 수 있다.

---

## 11. F-009 탐지 결과 이미지 저장

### 저장 경로
```text
static/outputs/
```

### 필요 이유
사용자가 탐지 결과를 시각적으로 확인할 수 있어야 하며, 추후 결과 조회와 상담 기능에서도 활용할 수 있다.

---

## 12. F-010 LLM 상담

### URL
```http
POST /api/chat
```

### Request 예시
```json
{
  "risk_level": "high",
  "detected": true,
  "animal_group": "quadruped",
  "object_count": 2,
  "time_zone": "night",
  "message": "농장 근처에서 멧돼지 같은 동물이 보였습니다."
}
```

### Response 예시
```json
{
  "answer": "야간에 사족보행 야생동물이 여러 마리 탐지된 상황이므로 직접 접근하지 말고 안전한 실내로 이동한 뒤 위치와 시간을 기록하세요."
}
```

### 필요 이유
예측과 탐지 결과만 제공하면 사용자가 다음 행동을 판단하기 어렵다. LLM 상담은 결과를 사람이 이해할 수 있는 대응 지침으로 바꿔준다.

---

## 13. F-011 SLM 경량 상담

### 기능 설명
저사양 또는 현장 환경에서 짧고 빠른 대응 상담을 제공한다.

### 입력
동물 그룹, 위험도, 시간대, 객체 수, 위치 상황

### 출력
핵심 대응 요약, 접근 금지 여부, 신고 필요 여부

### 필요 이유
4차 프로젝트는 3차 LLM과 차별화되어야 한다. SLM은 작은 모델로 빠른 현장 대응을 제공하는 방향이 적합하다.

---

## 14. F-012 Oracle DB 결과 저장

### 주요 테이블
| 테이블 | 설명 |
|---|---|
| USERS | 사용자 정보 |
| RISK_PREDICTION_RESULT | 1차 위험도 예측 결과 |
| VISION_DETECTION_RESULT | 2차 이미지 탐지 결과 |
| CHAT_LOG | 3차/4차 상담 로그 |

### 필요 이유
기존 Oracle XE와 python-oracledb 경험을 활용할 수 있고, Flask + Oracle DB 연동은 웹 서비스 프로젝트의 완성도를 높인다.

---

## 15. F-013 결과 조회

### 기능 설명
로그인 사용자가 이전 예측, 탐지, 상담 결과를 조회할 수 있다.

### 출력 항목
분석 날짜, 분석 유형, 위험도, 객체 수, 탐지 여부, 상담 요약

### 필요 이유
야생동물 출현은 반복 기록 관리가 중요하므로, 결과 저장과 조회는 서비스 완성도를 높인다.
