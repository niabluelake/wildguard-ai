# WildGuard AI 기능명세서

## 1. 문서 개요

본 문서는 WildGuard AI의 기능을 정의한다.

현재 프로젝트는 다음 4단계 구조로 진행한다.

| 단계 | 내용 |
|---|---|
| 1차 ML | 서울시 멧돼지 민원신고 현황 데이터를 기반으로 자치구·월별 출현 위험도 예측 |
| 2차 Vision | AI Hub 야생동물 이미지와 bbox 라벨을 활용한 YOLO 객체 탐지 |
| 3차 LLM | 위험도 예측 결과와 탐지 결과 기반 야생동물 대응 상담 |
| 4차 SLM | 현장용 경량 야생동물 대응 상담 모델 |

---

## 2. 전체 기능 목록

| 기능 ID | 기능명 | 설명 | 단계 |
|---|---|---|---|
| F-001 | 프로젝트 기본 화면 | WildGuard AI 소개 및 주요 기능 이동 | 공통 |
| F-002 | 서울시 멧돼지 신고 데이터 수집 | 서울시 멧돼지 민원신고 CSV를 프로젝트 데이터로 구성 | 1차 |
| F-003 | 위험도 라벨 생성 | 출현개체수 기준으로 low / medium / high 생성 | 1차 |
| F-004 | 위험도 예측 모델 학습 | 자치구·월·계절·과거 통계 기반 분류 모델 학습 | 1차 |
| F-005 | 위험도 예측 API | 사용자 입력값 기반 위험도 예측 결과 반환 | 1차 |
| F-006 | 위험도 예측 화면 | 웹에서 자치구와 월 입력 후 결과 확인 | 1차 |
| F-007 | YOLO 라벨 변환 | AI Hub bbox를 YOLO txt 형식으로 변환 | 2차 |
| F-008 | 이미지 탐지 API | 이미지 업로드 후 야생동물 탐지 | 2차 |
| F-009 | 탐지 결과 이미지 저장 | bbox 표시 결과 이미지 저장 | 2차 |
| F-010 | LLM 상담 | 예측/탐지 결과 기반 대응 상담 제공 | 3차 |
| F-011 | SLM 경량 상담 | 현장용 경량 상담 응답 제공 | 4차 |
| F-012 | 회원가입/로그인 | 사용자 인증 및 세션 관리 | 공통 |
| F-013 | Oracle DB 결과 저장 | 로그인 사용자 예측 결과 저장 | 공통 |
| F-014 | 결과 조회 | 저장된 분석 결과 조회 | 공통 |

---

## 3. F-001 프로젝트 기본 화면

### 기능 설명

서비스 소개와 1차 위험도 예측, 2차 이미지 탐지, 3차 상담 기능으로 이동할 수 있는 메인 화면을 제공한다.

### URL

```http
GET /
```

### 출력

- 서비스명
- 프로젝트 설명
- 1차 위험도 예측 페이지 링크
- 2차 이미지 탐지 예정 안내
- 3차 상담 예정 안내
- 로그인/회원가입 또는 사용자 정보

---

## 4. F-002 서울시 멧돼지 신고 데이터 수집

### 기능 설명

서울시 멧돼지 민원신고 현황 CSV를 1차 ML 학습 데이터로 사용한다.

### 입력 경로

```text
data/seoul_wildlife/seoul_boar_reports.csv
```

### 원본 컬럼

| 컬럼 | 설명 |
|---|---|
| 연도 | 신고 연도 |
| 자치구 | 서울시 자치구 |
| 월 | 신고 월 |
| 출현개체수 | 신고된 멧돼지 출현 개체수 |
| 포획개체수 | 포획된 멧돼지 개체수 |

### 필요 이유

AI Hub 이미지는 객체 탐지에는 적합하지만, 출현하지 않은 상황과 비교하는 지역별 위험도 예측에는 한계가 있다. 따라서 1차 ML은 실제 민원신고 기반의 지역·월별 데이터로 구성한다.

---

## 5. F-003 위험도 라벨 생성

### 기능 설명

`출현개체수`를 기준으로 서비스용 위험도 라벨을 생성한다.

| 조건 | risk_level |
|---|---|
| 출현개체수 0건 | low |
| 출현개체수 1건 | medium |
| 출현개체수 2건 이상 | high |

### 필요 이유

원본 데이터는 출현개체수와 포획개체수를 제공하지만 위험도 라벨은 제공하지 않는다. 따라서 서비스 목적에 맞게 low / medium / high 라벨을 생성한다.

---

## 6. F-004 위험도 예측 모델 학습

### 기능 설명

서울시 멧돼지 신고 데이터를 기반으로 위험도 분류 모델을 학습한다.

### 입력 데이터

```text
data/seoul_wildlife/seoul_boar_reports.csv
```

### 사용 Feature

| 구분 | 컬럼 |
|---|---|
| 기본 | 연도, 자치구, 월, 계절 |
| 파생 | district_total_count |
| 파생 | district_avg_count |
| 파생 | month_avg_count |
| 파생 | district_month_avg_count |
| 파생 | district_total_capture |

### Target

```text
risk_level
```

### 저장 모델

```text
models/ml/seoul_boar_risk_model.pkl
models/ml/seoul_boar_stats.pkl
```

### 학습 결과

```text
Accuracy: 0.7222
```

```text
high f1-score: 0.76
low  f1-score: 0.80
medium f1-score: 0.32
```

### 필요 이유

사용자가 직접 입력하는 값은 자치구와 월로 단순하게 유지하되, 백엔드에서 과거 출현 통계 feature를 자동 결합하여 더 안정적인 예측을 제공한다.

---

## 7. F-005 위험도 예측 API

### URL

```http
POST /api/risk/predict
```

### Request 예시

```json
{
  "district": "은평구",
  "month": 10
}
```

### Response 예시

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

### 필요 이유

Flask 웹 화면과 ML 모델을 연결하기 위해 API 형태의 예측 기능이 필요하다.

---

## 8. F-006 위험도 예측 화면

### URL

```http
GET /risk
```

### 입력 항목

| 항목 | 설명 |
|---|---|
| 자치구 | 서울시 멧돼지 신고 데이터에 포함된 자치구 |
| 월 | 1월~12월 |

### 출력 항목

| 항목 | 설명 |
|---|---|
| 위험도 | low / medium / high |
| 위험도 메시지 | 대응 안내 문구 |
| 자치구 | 입력 자치구 |
| 월 | 입력 월 |
| 계절 | 월 기준 자동 변환 |
| 과거 신고 통계 | 자치구 총 출현, 월평균, 포획 통계 등 |

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

```text
class 0 = quadruped
```

### 필요 이유

2차 프로젝트의 핵심은 이미지 기반 객체 탐지이다. AI Hub 데이터는 이미지와 bbox 라벨을 제공하므로 YOLO 학습에 적합하다.

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
  "district": "은평구",
  "month": 10,
  "detected": true,
  "animal_group": "quadruped",
  "message": "산 근처에서 멧돼지 같은 동물을 봤습니다."
}
```

### Response 예시

```json
{
  "answer": "은평구 10월은 과거 신고 기준 멧돼지 출현 위험도가 높게 예측됩니다. 동물에게 접근하지 말고 안전한 장소로 이동한 뒤 관할 기관에 신고하세요."
}
```

---

## 13. F-011 SLM 경량 상담

### 기능 설명

저사양 또는 현장 환경에서 짧고 빠른 대응 상담을 제공한다.

### 입력

- 자치구
- 월
- 위험도
- 탐지 여부
- 사용자 상황 설명

### 출력

- 핵심 대응 요약
- 접근 금지 여부
- 신고 필요 여부

---

## 14. F-012 회원가입/로그인

### 회원가입 URL

```http
GET /auth/register
POST /auth/register
```

### 로그인 URL

```http
GET /auth/login
POST /auth/login
```

### 세션 저장 값

```text
user_id
username
name
role
```

### 정책

- 비밀번호는 해시 저장
- 이메일은 MVP에서 제외
- 비회원도 위험도 예측은 가능
- 로그인 사용자는 예측 기록 저장 가능

---

## 15. F-013 Oracle DB 결과 저장

### 저장 대상

```text
seoul_boar_risk_log
```

### 저장 항목

- user_id
- district
- month
- year
- season
- risk_level
- risk_message
- district_total_count
- district_avg_count
- month_avg_count
- district_month_avg_count
- district_total_capture

### 정책

| 사용자 상태 | 예측 | DB 저장 |
|---|---|---|
| 비회원 | 가능 | 불가 |
| 로그인 사용자 | 가능 | 가능 |

---

## 16. F-014 결과 조회

### URL

```http
GET /risk/history
```

### 정책

- 비로그인: 로그인 페이지 이동
- 일반 로그인 사용자: 본인 기록만 조회
- official/admin: 전체 기록 조회로 확장 예정

### 출력 항목

- 생성일
- 자치구
- 월
- 계절
- 위험도
- 자치구 총 출현개체수
- 자치구·월 평균 출현개체수
- 대응 메시지
