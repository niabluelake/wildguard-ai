# WildGuard AI ERD

## 1. 개요

WildGuard AI는 회원 정보, 위험도 예측 기록, 이미지/영상 탐지 기록, 상담 기록을 관리할 수 있는 구조로 설계한다. 현재 핵심 DB 기능은 로그인 사용자의 위험도 예측 결과 저장 및 조회이다.

---

## 2. 주요 엔티티

### USERS

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| user_id | NUMBER | 사용자 ID |
| email | VARCHAR2 | 이메일 |
| password_hash | VARCHAR2 | 비밀번호 해시 |
| name | VARCHAR2 | 사용자 이름 |
| created_at | DATE | 가입일 |

### RISK_PREDICTION_LOGS

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| log_id | NUMBER | 예측 기록 ID |
| user_id | NUMBER | 사용자 ID |
| region_name | VARCHAR2 | 사용자 표시 지역명 |
| location | VARCHAR2 | AI Hub 관측 지역 |
| weather | VARCHAR2 | 날씨 |
| time_zone | VARCHAR2 | 시간대 |
| season | VARCHAR2 | 계절 |
| predicted_score | NUMBER | 예측 위험 점수 |
| risk_grade | VARCHAR2 | 위험 등급 |
| main_risk_species | VARCHAR2 | 주요 위험 동물 |
| message | CLOB | 예측 결과 메시지 |
| created_at | DATE | 생성일 |

### VISION_DETECTION_LOGS

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| detection_id | NUMBER | 탐지 기록 ID |
| user_id | NUMBER | 사용자 ID |
| file_name | VARCHAR2 | 업로드 파일명 |
| detection_count | NUMBER | 탐지 수 |
| max_confidence | NUMBER | 최대 confidence |
| result_image_url | VARCHAR2 | 결과 이미지 URL |
| created_at | DATE | 생성일 |

### CHAT_LOGS

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| chat_id | NUMBER | 상담 기록 ID |
| user_id | NUMBER | 사용자 ID |
| consultation_mode | VARCHAR2 | 상담 모드 |
| user_message | CLOB | 사용자 질문 |
| answer | CLOB | 상담 답변 |
| risk_score | NUMBER | 상담에 사용된 위험 점수 |
| risk_grade | VARCHAR2 | 상담에 사용된 위험 등급 |
| created_at | DATE | 생성일 |

---

## 3. 관계

```text
USERS 1 ─ N RISK_PREDICTION_LOGS
USERS 1 ─ N VISION_DETECTION_LOGS
USERS 1 ─ N CHAT_LOGS
```

현재 구현에서는 위험도 예측 기록 저장을 우선으로 하며, 탐지 기록과 상담 기록은 확장 가능한 구조로 정의한다.
