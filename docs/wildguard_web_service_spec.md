# WildGuard AI 웹서비스 기능명세서

## 1. 개요
WildGuard AI는 야생동물 출현 위험도를 예측하고, 로그인 사용자에게 예측 기록 저장과 조회 기능을 제공하는 공공기관형 웹 서비스이다.

## 2. 핵심 정책

| 사용자 상태 | 예측 | DB 저장 | 기록 조회 |
|---|---|---|---|
| 비회원 | 가능 | 불가 | 불가 |
| 로그인 사용자 | 가능 | 가능 | 본인 기록 |
| official/admin | 가능 | 가능 | 전체 기록 예정 |

## 3. URL 구조

| URL | Method | 기능 | 접근 |
|---|---|---|---|
| `/` | GET | 메인 화면 | 전체 |
| `/auth/register` | GET/POST | 회원가입 | 전체 |
| `/auth/login` | GET/POST | 로그인 | 전체 |
| `/auth/logout` | GET | 로그아웃 | 로그인 |
| `/risk` | GET/POST | 위험도 예측 화면 | 전체 |
| `/api/risk/predict` | POST | 위험도 예측 API | 전체 |
| `/risk/history` | GET | 예측 기록 조회 | 로그인 |
| `/admin/risk/logs` | GET | 전체 기록 조회 | official/admin 예정 |
| `/dashboard` | GET | 통계 대시보드 | official/admin 예정 |
| `/api/vision/detect` | POST | 이미지 탐지 API | 예정 |
| `/api/chat` | POST | 상담 API | 예정 |

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

## 7. 로그아웃

```http
GET /auth/logout
```

session을 초기화하고 메인 또는 위험도 예측 화면으로 이동한다.

## 8. 위험도 예측

### URL
```http
GET /risk
POST /risk
```

### 입력
day, camera_type, weather, location, time_zone, season, object_count, max_bbox_area_ratio, avg_bbox_area_ratio

### 출력
risk_level, risk_message, saved_to_db

### 비회원
- 예측 가능
- DB 저장 안 함
- 로그인 안내 표시

### 로그인 사용자
- 예측 가능
- RISK_PREDICTION_LOG에 user_id와 함께 저장
- 저장 완료 안내 표시

## 9. 위험도 예측 API

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
  "message": "야간에 야생동물이 탐지되어 주의가 필요합니다.",
  "saved_to_db": true
}
```

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
생성일, 위치, 날씨, 시간대, 계절, 객체 수, bbox 비율, 위험도, 대응 메시지

## 11. 테스트 시나리오

### 비회원 예측
1. 로그아웃 상태
2. `/risk` 접속
3. 예측 실행
4. 결과 출력 확인
5. DB 저장 안 됨 확인

### 회원 예측
1. 회원가입
2. 로그인
3. `/risk` 예측 실행
4. DB 저장 메시지 확인
5. `risk_prediction_log`에 user_id 포함 저장 확인

### 기록 조회
1. 로그인
2. `/risk/history` 접속
3. 본인 기록 조회 확인
