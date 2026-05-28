# WildGuard AI PRD

## 1. 제품 개요

### 제품명
WildGuard AI

### 한 줄 설명
AI Hub 야생동물 라벨링 데이터를 활용하여 야생동물 출현 위험도를 예측하고, 이미지 탐지와 대응 상담을 제공하는 AI 서비스

### 제품 목표
WildGuard AI의 목표는 야생동물 출현 상황을 데이터 기반으로 판단하고, 사용자가 안전하게 대응할 수 있도록 예측, 탐지, 상담 기능을 제공하는 것이다.

---

## 2. 배경

야생동물 출현은 농장, 산림, 도로, 마을 주변에서 발생할 수 있으며, 사용자는 출현 상황이 얼마나 위험한지 판단하기 어렵다. 특히 멧돼지와 같은 사족보행 야생동물은 야간에 출현하는 경우가 많고, 직접 접근 시 위험할 수 있다.

| 단계 | 제품 기능 |
|---|---|
| 1차 | JSON 메타데이터 기반 위험도 예측 |
| 2차 | YOLO 기반 사족보행 야생동물 탐지 |
| 3차 | LLM 기반 대응 상담 |
| 4차 | SLM 기반 현장용 경량 상담 |

### 방향 선정 이유
라벨링 JSON에는 단순 bbox뿐 아니라 촬영 시간, 주야간 여부, 날씨, 위치, GPS, 동물 종, 위험 여부, 야행성 여부가 포함되어 있다. 따라서 이 데이터를 정형 데이터로 변환하면 1차 ML에 활용할 수 있고, 원천 이미지와 bbox는 2차 YOLO 학습에 활용할 수 있다.

---

## 3. 사용자와 문제

### 주요 사용자
| 사용자 | 문제 |
|---|---|
| 농장주 | 야간 출현 야생동물에 의한 농작물 피해와 안전 문제 |
| 산림관리원 | 등산로, 산림 지역의 야생동물 출현 관리 |
| 지자체 담당자 | 신고·민원 대응과 위험 상황 안내 |
| 일반 사용자 | 야생동물 발견 시 안전 행동 요령 부족 |

### 사용자 문제
- 야생동물 출현 상황의 위험도를 판단하기 어렵다.
- 이미지 속 야생동물 여부를 빠르게 확인하기 어렵다.
- 위험 상황에서 어떤 행동을 해야 할지 알기 어렵다.
- 분석 결과를 기록하고 재확인하기 어렵다.

---

## 4. 제품 가치

| 가치 | 설명 |
|---|---|
| 예측 | 정형 메타데이터 기반 위험도 예측 |
| 탐지 | 이미지 속 사족보행 야생동물 탐지 |
| 상담 | 위험도와 탐지 결과 기반 대응 안내 |
| 기록 | Oracle DB 기반 결과 저장 |
| 확장 | LLM에서 SLM으로 경량 현장 상담 확장 |

---

## 5. MVP 범위

### 포함 기능
| 기능 | 설명 |
|---|---|
| AI Hub JSON 전처리 | 라벨링 JSON을 CSV로 변환 |
| 위험도 라벨 생성 | 객체 수, bbox 크기, 야간 여부 기반 risk_level 생성 |
| 위험도 예측 모델 | low / medium / high 분류 |
| Flask 위험도 화면 | 사용자가 조건 입력 후 위험도 확인 |
| YOLO 변환 준비 | bbox를 YOLO 형식으로 변환하는 구조 설계 |
| GitHub 관리 | 코드와 문서를 버전 관리 |

### 제외 기능
| 제외 기능 | 이유 |
|---|---|
| 실시간 CCTV 분석 | 구현 범위가 커짐 |
| 모바일 앱 | 웹 MVP 이후 확장 |
| 공공기관 자동 신고 | 실제 기관 연동이 필요함 |
| 원본 데이터 GitHub 업로드 | 용량과 라이선스 문제 |
| 완전한 다중 클래스 탐지 | 데이터 불균형이 큼 |

---

## 6. 데이터 전략

### 메인 데이터
AI Hub 야생동물 라벨링 JSON + 원천 이미지

### 1차 ML 데이터 사용 방식
1차에서는 이미지를 직접 사용하지 않고 JSON 메타데이터만 사용한다.

변환 후 CSV 예시:
| day | camera_type | weather | location | time_zone | season | object_count | max_bbox_area_ratio | risk_level |
|---|---|---|---|---|---|---:|---:|---|
| night | IR | cloudy | 대산농원 | night | fall | 2 | 0.0235 | medium |

### 현재 데이터 처리 결과
| 항목 | 결과 |
|---|---|
| JSON 파일 수 | 30,700개 |
| 변환 CSV 행 수 | 30,700행 |
| 변환 CSV 컬럼 수 | 22개 |
| 주요 종 | 멧돼지 중심 |
| 출력 파일 | `data/aihub/ml_dataset/aihub_wildlife_metadata.csv` |

위험도 분포:
| risk_level | count |
|---|---:|
| medium | 18,694 |
| high | 10,196 |
| low | 1,810 |

### GitHub 제외 대상
```gitignore
data/aihub_json/
data/aihub/ml_dataset/
*.pkl
*.joblib
```

### 제외 이유
데이터 용량이 크고 라이선스가 있으므로 GitHub에는 코드, 문서, 변환 스크립트만 올리는 것이 안전하다.

---

## 7. 제품 기능 상세

### 7.1 1차 ML: 위험도 예측

#### 목표
AI Hub 라벨링 JSON을 정형 데이터로 변환하여 야생동물 출현 상황의 위험도를 예측한다.

#### 입력
`day`, `camera_type`, `weather`, `location`, `time_zone`, `season`, `object_count`, `max_bbox_area_ratio`, `avg_bbox_area_ratio`

#### 출력
`risk_level`: low / medium / high, 대응 메시지

#### 성공 기준
30,700행 CSV 변환 완료, 모델 학습 가능, 테스트 데이터에 대해 위험도 예측 결과 출력, Flask 화면에서 결과 확인 가능

### 7.2 2차 Vision: YOLO 탐지

#### 목표
원천 이미지와 bbox 라벨을 사용하여 사족보행 야생동물을 탐지한다.

#### 클래스 정책
```text
class 0 = quadruped
```

#### 이유
데이터가 멧돼지에 집중되어 있고 일부 종은 수가 적다. 단일 클래스로 묶으면 클래스 불균형을 줄이고 탐지 모델 완성도를 높일 수 있다.

#### API
```http
POST /api/vision/detect
```

#### 성공 기준
이미지 업로드 가능, 탐지 여부 반환, bbox 좌표 반환, 결과 이미지 저장

### 7.3 3차 LLM: 대응 상담

#### 목표
위험도 예측 결과와 이미지 탐지 결과를 자연어 대응 지침으로 변환한다.

#### 예시 출력
```text
야간에 사족보행 야생동물이 여러 마리 탐지된 상황이므로 직접 접근하지 말고 안전한 장소로 이동하세요. 위치와 시간을 기록하고 관할 기관에 신고하는 것이 좋습니다.
```

#### 성공 기준
사용자의 질문에 대해 대응 방법 출력, 예측/탐지 결과를 답변에 반영, 상담 로그 저장 가능

### 7.4 4차 SLM: 경량 상담

#### 목표
저사양 또는 현장 환경에서 빠르게 사용할 수 있는 경량 상담 모델을 구성한다.

| 구분 | LLM | SLM |
|---|---|---|
| 목적 | 상세 상담 | 빠른 현장 대응 |
| 응답 길이 | 길고 설명적 | 짧고 핵심적 |
| 실행 환경 | 서버 중심 | 로컬/저사양 가능 |
| 사용 상황 | 일반 상담 | 현장 즉시 대응 |

---

## 8. 화면 구성

### 메인 화면
서비스 소개, 1차 위험도 예측 이동, 2차 이미지 탐지 이동, 3차 상담 이동

### 위험도 예측 화면
입력: 주야간 여부, 카메라 타입, 날씨, 위치, 시간대, 계절, 객체 수, bbox 면적 비율

출력: 위험도, 위험도 설명, 대응 메시지

### 이미지 탐지 화면
입력: 이미지 업로드

출력: 탐지 여부, 객체 수, confidence, bbox, 결과 이미지

### 상담 화면
입력: 사용자 질문, 위험도 결과, 탐지 결과

출력: 상황 요약, 대응 방법, 추가 확인 질문

---

## 9. API 설계

### 위험도 예측 API
```http
POST /api/risk/predict
```

Request:
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

Response:
```json
{
  "risk_level": "medium",
  "message": "야간에 야생동물이 탐지되어 주의가 필요합니다."
}
```

### 이미지 탐지 API
```http
POST /api/vision/detect
```

### 상담 API
```http
POST /api/chat
```

---

## 10. DB 설계 초안

### USERS
| 컬럼 | 타입 | 설명 |
|---|---|---|
| user_id | NUMBER | 사용자 ID |
| username | VARCHAR2 | 사용자명 |
| password | VARCHAR2 | 비밀번호 |
| user_type | VARCHAR2 | 사용자 유형 |
| created_at | DATE | 가입일 |

### RISK_PREDICTION_RESULT
| 컬럼 | 타입 | 설명 |
|---|---|---|
| result_id | NUMBER | 결과 ID |
| user_id | NUMBER | 사용자 ID |
| day_type | VARCHAR2 | 주야간 |
| camera_type | VARCHAR2 | 카메라 유형 |
| weather | VARCHAR2 | 날씨 |
| location_name | VARCHAR2 | 위치 |
| object_count | NUMBER | 객체 수 |
| max_bbox_area_ratio | NUMBER | 최대 bbox 면적 비율 |
| predicted_risk_level | VARCHAR2 | 예측 위험도 |
| message | VARCHAR2 | 결과 메시지 |
| created_at | DATE | 생성일 |

### VISION_DETECTION_RESULT
| 컬럼 | 타입 | 설명 |
|---|---|---|
| detection_id | NUMBER | 탐지 ID |
| user_id | NUMBER | 사용자 ID |
| image_path | VARCHAR2 | 원본 이미지 경로 |
| result_image_path | VARCHAR2 | 결과 이미지 경로 |
| detected | VARCHAR2 | 탐지 여부 |
| class_name | VARCHAR2 | 클래스명 |
| confidence | NUMBER | 신뢰도 |
| bbox | VARCHAR2 | bbox 좌표 |
| created_at | DATE | 생성일 |

### CHAT_LOG
| 컬럼 | 타입 | 설명 |
|---|---|---|
| chat_id | NUMBER | 상담 ID |
| user_id | NUMBER | 사용자 ID |
| question | VARCHAR2 | 사용자 질문 |
| answer | CLOB | 답변 |
| model_type | VARCHAR2 | LLM 또는 SLM |
| created_at | DATE | 생성일 |

---

## 11. 성공 지표

| 영역 | 성공 기준 |
|---|---|
| 데이터 전처리 | 30,700개 JSON을 CSV로 변환 |
| 라벨 생성 | low / medium / high 위험도 분포 확보 |
| 1차 ML | 위험도 예측 모델 학습 및 저장 |
| Flask | 웹 화면에서 위험도 예측 가능 |
| 2차 YOLO | 이미지 업로드 후 사족보행 객체 탐지 |
| 3차 LLM | 대응 상담 답변 생성 |
| 4차 SLM | 경량 상담 응답 제공 |
| GitHub | 코드와 문서가 커밋 단위로 관리됨 |

---

## 12. 현재 진행 상황

| 작업 | 상태 |
|---|---|
| GitHub 저장소 생성 | 완료 |
| 프로젝트 폴더 생성 | 완료 |
| AI Hub JSON 배치 | 완료 |
| JSON 메타데이터 변환 스크립트 | 완료 |
| 30,700개 JSON 변환 | 완료 |
| 위험도 라벨 분포 조정 | 완료 |
| 요구사항 분석서 작성 | 완료 |
| 기능명세서 작성 | 완료 |
| PRD 작성 | 완료 |
| 1차 ML 학습 코드 | 다음 작업 |
| Flask 위험도 예측 연결 | 예정 |
| YOLO 라벨 변환 | 예정 |
| Oracle DB 연동 | 예정 |

---

## 13. GitHub 업로드 정책

GitHub에 올릴 것:
```text
README.md
.gitignore
app.py
routes/
services/
scripts/
docs/
requirements.txt
```

GitHub에 올리지 않을 것:
```text
data/aihub_json/
data/aihub/ml_dataset/
원천 이미지
라벨링 JSON
모델 pkl/joblib 파일
YOLO pt 파일
```
