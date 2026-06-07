# WildGuard AI PRD

## 1. 제품 개요

### 제품명

WildGuard AI

### 한 줄 설명

서울시 멧돼지 민원신고 현황 데이터와 AI Hub 야생동물 영상 데이터를 활용하여 야생동물 출현 위험도 예측, 이미지 탐지, 대응 상담을 제공하는 AI 서비스

### 제품 목표

WildGuard AI의 목표는 야생동물 출현 가능성을 데이터 기반으로 판단하고, 사용자가 안전하게 대응할 수 있도록 예측, 탐지, 상담 기능을 제공하는 것이다.

---

## 2. 배경

야생동물 출현은 농장, 산림, 도로, 마을 주변에서 안전 문제와 재산 피해를 유발할 수 있다. 특히 멧돼지는 도심 인근 산림, 하천, 주거지 경계에서 출현할 수 있으며 사용자가 직접 위험도를 판단하기 어렵다.

| 단계 | 제품 기능 |
|---|---|
| 1차 | 서울시 멧돼지 민원신고 현황 기반 자치구·월별 위험도 예측 |
| 2차 | AI Hub 이미지 기반 YOLO 야생동물 탐지 |
| 3차 | LLM 기반 대응 상담 |
| 4차 | SLM 기반 현장용 경량 상담 |

### 방향 선정 이유

AI Hub 데이터는 이미지와 bbox 라벨이 있어 2차 Vision에 적합하다. 반면 1차 ML의 지역·월별 출현 위험도 예측에는 실제 신고 기록 기반 데이터가 더 자연스럽다. 따라서 1차는 서울시 멧돼지 민원신고 현황을 사용하고, 2차는 AI Hub 원천 이미지와 bbox를 사용한다.

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

- 지역과 시기에 따른 야생동물 출현 위험도를 판단하기 어렵다.
- 이미지 속 야생동물 여부를 빠르게 확인하기 어렵다.
- 위험 상황에서 어떤 행동을 해야 할지 알기 어렵다.
- 분석 결과를 기록하고 재확인하기 어렵다.

---

## 4. 제품 가치

| 가치 | 설명 |
|---|---|
| 예측 | 서울시 멧돼지 신고 현황 기반 자치구·월별 위험도 예측 |
| 탐지 | 이미지 속 야생동물 탐지 |
| 상담 | 위험도와 탐지 결과 기반 대응 안내 |
| 기록 | Oracle DB 기반 결과 저장 |
| 확장 | LLM에서 SLM으로 경량 현장 상담 확장 |

---

## 5. MVP 범위

### 포함 기능

| 기능 | 설명 |
|---|---|
| 서울시 멧돼지 신고 데이터 활용 | 자치구·월별 출현개체수와 포획개체수 활용 |
| 위험도 라벨 생성 | 출현개체수 기준 low / medium / high 생성 |
| 위험도 예측 모델 | RandomForest 기반 분류 모델 |
| Flask 위험도 화면 | 사용자가 자치구와 월 입력 후 위험도 확인 |
| 과거 신고 통계 표시 | 자치구 총 출현, 평균 출현, 포획 통계 표시 |
| 회원가입/로그인 | 사용자 인증 |
| 비회원 체험 모드 | 로그인 없이 예측 가능, DB 저장 없음 |
| GitHub 관리 | 코드와 문서를 버전 관리 |

### 제외 기능

| 제외 기능 | 이유 |
|---|---|
| 실시간 CCTV 분석 | 구현 범위가 커짐 |
| 모바일 앱 | 웹 MVP 이후 확장 |
| 공공기관 자동 신고 | 실제 기관 연동이 필요함 |
| 원본 데이터 GitHub 업로드 | 용량과 라이선스 문제 |
| 완전한 다중 클래스 탐지 | 2차 Vision 단계에서 별도 진행 |

---

## 6. 데이터 전략

### 1차 ML 메인 데이터

```text
서울시 멧돼지 민원신고 현황.csv
```

### 1차 ML 데이터 사용 방식

사용자가 직접 입력하는 값은 `자치구`, `월`이다. 모델 학습 시에는 원본 CSV에서 파생 통계를 생성하여 feature로 사용한다.

| 원본 컬럼 | 설명 |
|---|---|
| 연도 | 신고 데이터 연도 |
| 자치구 | 서울시 자치구 |
| 월 | 신고 월 |
| 출현개체수 | 신고된 멧돼지 출현 개체수 |
| 포획개체수 | 포획된 멧돼지 개체수 |

### 주요 파생 Feature

| Feature | 설명 |
|---|---|
| 계절 | 월 기준 봄/여름/가을/겨울 |
| district_total_count | 자치구 총 출현개체수 |
| district_avg_count | 자치구 평균 출현개체수 |
| month_avg_count | 월별 평균 출현개체수 |
| district_month_avg_count | 자치구·월 평균 출현개체수 |
| district_total_capture | 자치구 총 포획개체수 |

### 위험도 라벨

| 조건 | risk_level |
|---|---|
| 출현개체수 0건 | low |
| 출현개체수 1건 | medium |
| 출현개체수 2건 이상 | high |

### 2차 Vision 데이터

AI Hub 야생동물 활동 영상 데이터의 원천 이미지와 bbox 라벨을 사용한다.

---

## 7. 1차 ML 상세

### 목표

서울시 자치구와 월 조건에 따른 멧돼지 출현 위험도를 예측한다.

### 입력

```text
district
month
```

### 출력

```text
risk_level
risk_message
input
stats
```

### 모델

```text
RandomForestClassifier
```

### 모델 성능

```text
Accuracy: 0.7222
```

```text
high f1-score: 0.76
low  f1-score: 0.80
medium f1-score: 0.32
```

### 성능 해석

`high`와 `low`는 비교적 안정적으로 분류되었지만, `medium`은 표본 수가 적고 경계값에 위치해 성능이 낮게 나타났다. 향후 추가 연도 데이터, 기상 데이터, 산림·하천 인접도 등을 결합하면 개선 가능하다.

---

## 8. 화면 구성

### 메인 화면

- 서비스 소개
- 위험도 예측 이동
- 로그인/회원가입 표시
- 로그인 시 예측 기록 이동

### 위험도 예측 화면

입력:

```text
자치구
월
```

출력:

```text
위험도
위험도 진행바
대응 메시지
자치구 / 월 / 계절
과거 신고 통계
DB 저장 여부
```

### 이미지 탐지 화면

입력:

```text
이미지 업로드
```

출력:

```text
탐지 여부
객체 수
confidence
bbox
결과 이미지
```

### 상담 화면

입력:

```text
사용자 질문
위험도 결과
탐지 결과
```

출력:

```text
상황 요약
대응 방법
추가 확인 질문
```

---

## 9. API 설계

### 위험도 예측 API

```http
POST /api/risk/predict
```

Request:

```json
{
  "district": "은평구",
  "month": 10
}
```

Response:

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
  "saved_to_db": false
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

## 10. DB 설계

### USERS

| 컬럼 | 타입 | 설명 |
|---|---|---|
| user_id | NUMBER | 사용자 ID |
| username | VARCHAR2 | 로그인 아이디 |
| password_hash | VARCHAR2 | 해시 비밀번호 |
| name | VARCHAR2 | 사용자 이름 |
| organization | VARCHAR2 | 소속 |
| role | VARCHAR2 | 사용자 유형 |
| created_at | DATE | 가입일 |

### SEOUL_BOAR_RISK_LOG

| 컬럼 | 타입 | 설명 |
|---|---|---|
| log_id | NUMBER | 로그 ID |
| user_id | NUMBER | 사용자 ID |
| district | VARCHAR2 | 자치구 |
| month | NUMBER | 월 |
| year | NUMBER | 기준 연도 |
| season | VARCHAR2 | 계절 |
| risk_level | VARCHAR2 | 예측 위험도 |
| risk_message | VARCHAR2 | 대응 메시지 |
| district_total_count | NUMBER | 자치구 총 출현개체수 |
| district_avg_count | NUMBER | 자치구 평균 출현개체수 |
| month_avg_count | NUMBER | 월별 평균 출현개체수 |
| district_month_avg_count | NUMBER | 자치구·월 평균 출현개체수 |
| district_total_capture | NUMBER | 자치구 총 포획개체수 |
| created_at | DATE | 생성일 |

---

## 11. 성공 지표

| 영역 | 성공 기준 |
|---|---|
| 데이터 구성 | 서울시 멧돼지 신고 CSV 구성 |
| 라벨 생성 | low / medium / high 위험도 라벨 확보 |
| 1차 ML | 위험도 예측 모델 학습 및 저장 |
| 모델 성능 | Accuracy 약 72% 달성 |
| Flask | 웹 화면에서 위험도 예측 가능 |
| DB | 로그인 사용자 예측 기록 저장 |
| 2차 YOLO | 이미지 업로드 후 객체 탐지 |
| 3차 LLM | 대응 상담 답변 생성 |
| 4차 SLM | 경량 상담 응답 제공 |
| GitHub | 코드와 문서가 커밋 단위로 관리됨 |

---

## 12. 현재 진행 상황

| 작업 | 상태 |
|---|---|
| GitHub 저장소 생성 | 완료 |
| 프로젝트 폴더 생성 | 완료 |
| 서울시 멧돼지 CSV 배치 | 완료 |
| 파생 feature 생성 | 완료 |
| 1차 ML 모델 학습 | 완료 |
| Flask 위험도 예측 서비스 | 진행 중 |
| 위험도 예측 화면 | 진행 중 |
| Oracle DB 저장 구조 변경 | 예정 |
| YOLO 라벨 변환 | 예정 |
| LLM 상담 기능 | 예정 |

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
data/
models/ml/
*.pkl
*.joblib
.env
.venv/
원천 이미지
라벨링 JSON
YOLO pt 파일
```

---

## 14. 향후 개선 방향

- 추가 연도 신고 데이터 확보
- 기상 데이터 결합
- 산림·하천·공원 인접도 feature 추가
- 자치구 면적, 인구밀도 등 지역 feature 추가
- AI Hub Vision 결과와 1차 위험도 결과를 통합한 대응 상담 구현
