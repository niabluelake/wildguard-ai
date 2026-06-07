# WildGuard AI 웹서비스 기능명세서

## 1. 개요

WildGuard AI는 야생동물 출현 위험도를 예측하고, 로그인 사용자에게 예측 기록 저장과 조회 기능을 제공하는 공공기관형 웹 서비스이다.

현재 1차 위험도 예측은 서울시 멧돼지 민원신고 현황 데이터를 기반으로 한다.

---

## 2. 핵심 정책

| 사용자 상태 | 예측 | DB 저장 | 기록 조회 |
|---|---|---|---|
| 비회원 | 가능 | 불가 | 불가 |
| 로그인 사용자 | 가능 | 가능 | 본인 기록 |
| official/admin | 가능 | 가능 | 전체 기록 예정 |

---

## 3. URL 구조

| URL | Method | 기능 | 접근 |
|---|---|---|---|
| `/` | GET | 메인 화면 | 전체 |
| `/auth/register` | GET/POST | 회원가입 | 전체 |
| `/auth/login` | GET/POST | 로그인 | 전체 |
| `/auth/logout` | GET | 로그아웃 | 로그인 |
| `/risk` | GET | 위험도 예측 화면 | 전체 |
| `/api/risk/predict` | POST | 위험도 예측 API | 전체 |
| `/risk/history` | GET | 예측 기록 조회 | 로그인 |
| `/admin/risk/logs` | GET | 전체 기록 조회 | official/admin 예정 |
| `/dashboard` | GET | 통계 대시보드 | official/admin 예정 |
| `/api/vision/detect` | POST | 이미지 탐지 API | 예정 |
| `/api/chat` | POST | 상담 API | 예정 |

---

## 4. 메인 화면

### 기능

- 서비스 소개
- 위험도 예측 이동
- 로그인/회원가입 표시
- 로그인 시 사용자명, 예측 기록, 로그아웃 표시

### 비로그인 navbar

```text
홈 | 위험도 예측 | 이미지 탐지 예정 | 상담 챗봇 예정 | 로그인 | 회원가입
```

### 로그인 navbar

```text
홈 | 위험도 예측 | 예측 기록 | 이미지 탐지 예정 | 상담 챗봇 예정 | 사용자명 | 로그아웃
```

---

## 5. 회원가입

### URL

```http
GET /auth/register
POST /auth/register
```

### 입력

| 항목 | name | 필수 |
|---|---|---|
| 아이디 | username | O |
| 비밀번호 | password | O |
| 비밀번호 확인 | password_confirm | O |
| 이름 | name | O |
| 소속 | organization | X |
| 사용자 유형 | role | O |

이메일 기능은 MVP에서 제외한다.

### 처리

1. 입력값 검증
2. 비밀번호 확인
3. 비밀번호 hash 생성
4. USERS 저장
5. 로그인 페이지 이동

---

## 6. 로그인

### URL

```http
GET /auth/login
POST /auth/login
```

### 처리

1. username으로 사용자 조회
2. password hash 검증
3. 성공 시 session 저장
4. `/risk`로 이동

### session

```text
user_id
username
name
role
```

---

## 7. 로그아웃

```http
GET /auth/logout
```

session을 초기화하고 메인 또는 위험도 예측 화면으로 이동한다.

---

## 8. 위험도 예측 화면

### URL

```http
GET /risk
```

### 입력

| 항목 | name | 설명 |
|---|---|---|
| 자치구 | district | 서울시 멧돼지 신고 데이터에 포함된 자치구 |
| 월 | month | 1월~12월 |

### 출력

| 항목 | 설명 |
|---|---|
| risk_level | low / medium / high |
| risk_message | 대응 안내 |
| district | 입력 자치구 |
| month | 입력 월 |
| season | 월 기준 자동 변환 |
| stats | 과거 신고 통계 |
| saved_to_db | DB 저장 여부 |

### 비회원

- 예측 가능
- DB 저장 안 함
- 로그인 안내 표시

### 로그인 사용자

- 예측 가능
- `seoul_boar_risk_log`에 user_id와 함께 저장
- 저장 완료 안내 표시

---

## 9. 위험도 예측 API

```http
POST /api/risk/predict
```

### Request

```json
{
  "district": "은평구",
  "month": 10
}
```

### Response

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
  "saved": false,
  "saved_to_db": false
}
```

---

## 10. 예측 기록 조회

### URL

```http
GET /risk/history
```

### 정책

- 비로그인: 로그인 페이지 이동
- 일반 로그인 사용자: 본인 기록만 조회
- official/admin: 전체 기록 조회로 확장 예정

### 출력

| 항목 | 설명 |
|---|---|
| created_at | 예측 일시 |
| district | 자치구 |
| month | 월 |
| season | 계절 |
| risk_level | 위험도 |
| risk_message | 대응 메시지 |
| district_total_count | 자치구 총 출현개체수 |
| district_month_avg_count | 자치구·월 평균 출현개체수 |

---

## 11. 테스트 시나리오

### 비회원 예측

1. 로그아웃 상태
2. `/risk` 접속
3. 자치구와 월 선택
4. 예측 실행
5. 결과 출력 확인
6. DB 저장 안 됨 확인

### 회원 예측

1. 회원가입
2. 로그인
3. `/risk` 접속
4. 자치구와 월 선택
5. 예측 실행
6. DB 저장 메시지 확인
7. `/risk/history`에서 기록 확인

### API 테스트

```cmd
curl -X POST http://127.0.0.1:5000/api/risk/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"district\":\"은평구\",\"month\":10}"
```

---

## 12. 2차 이미지 탐지 API 예정

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
      "class_name": "quadruped",
      "confidence": 0.87,
      "bbox": [120, 80, 420, 360]
    }
  ],
  "result_image_url": "/static/outputs/result_001.jpg"
}
```

---

## 13. 3차 상담 API 예정

```http
POST /api/chat
```

### Request 예시

```json
{
  "district": "은평구",
  "month": 10,
  "risk_level": "high",
  "message": "산 근처에서 멧돼지를 봤습니다."
}
```

### Response 예시

```json
{
  "answer": "은평구 10월은 과거 신고 기준 멧돼지 출현 위험도가 높게 예측됩니다. 접근하지 말고 안전한 장소로 이동하세요."
}
```

---

## 14. 화면별 상태

| 화면 | 상태 |
|---|---|
| 메인 화면 | 구현 |
| 회원가입 | 구현 |
| 로그인 | 구현 |
| 위험도 예측 화면 | 수정 중 |
| 예측 기록 화면 | 새 DB 구조 반영 예정 |
| 이미지 탐지 화면 | 예정 |
| 상담 화면 | 예정 |
