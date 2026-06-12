# WildGuard AI ERD

## 1. 문서 개요

본 문서는 WildGuard AI 서비스의 데이터베이스 구조를 정의한다.

WildGuard AI는 야생동물 위험 점수 예측, 이미지 탐지, 대응 상담 기능을 제공하는 웹 기반 AI 서비스이다.

현재 1차 ML 기능은 AI Hub 야생동물 라벨링 JSON 메타데이터를 기반으로 `risk_score`를 예측하는 회귀 모델 API로 구현되어 있으며, 로그인 사용자의 예측 결과를 DB에 저장하는 구조로 확장한다.

---

## 2. 데이터베이스 사용 목적

| 목적             | 설명                                  |
| -------------- | ----------------------------------- |
| 사용자 관리         | 회원가입, 로그인, 사용자 역할 관리                |
| 위험 점수 예측 기록 저장 | 사용자가 실행한 위험 점수 예측 결과 저장             |
| 이미지 탐지 기록 저장   | 2차 Vision 기능에서 이미지 탐지 결과 저장         |
| 상담 기록 저장       | 3차 LLM / 4차 SLM 상담 기록 저장            |
| 관리자 조회         | 지자체 담당자 또는 관리자가 전체 기록을 조회할 수 있도록 확장 |

---

## 3. 주요 엔티티

| 엔티티                     | 설명              |
| ----------------------- | --------------- |
| `USERS`                 | 서비스 사용자 정보      |
| `RISK_PREDICTION_LOGS`  | 위험 점수 예측 기록     |
| `VISION_DETECTION_LOGS` | 이미지 탐지 기록       |
| `CONSULTATION_LOGS`     | LLM / SLM 상담 기록 |

---

## 4. ERD 개요

```text
USERS
  └── RISK_PREDICTION_LOGS
  └── VISION_DETECTION_LOGS
  └── CONSULTATION_LOGS
```

하나의 사용자는 여러 개의 위험 점수 예측 기록, 이미지 탐지 기록, 상담 기록을 가질 수 있다.

---

## 5. USERS 테이블

### 설명

회원가입 및 로그인 사용자의 정보를 저장한다.

### 컬럼 정의

| 컬럼명             | 타입            | 제약조건                 | 설명           |
| --------------- | ------------- | -------------------- | ------------ |
| `USER_ID`       | NUMBER        | PK                   | 사용자 고유 ID    |
| `USERNAME`      | VARCHAR2(50)  | UNIQUE, NOT NULL     | 로그인 아이디      |
| `PASSWORD_HASH` | VARCHAR2(255) | NOT NULL             | 해시 처리된 비밀번호  |
| `NAME`          | VARCHAR2(50)  | NOT NULL             | 사용자 이름       |
| `ROLE`          | VARCHAR2(30)  | NOT NULL             | 사용자 역할       |
| `ORGANIZATION`  | VARCHAR2(100) | NULL                 | 소속 기관 또는 농장명 |
| `CREATED_AT`    | TIMESTAMP     | DEFAULT SYSTIMESTAMP | 가입 일시        |
| `UPDATED_AT`    | TIMESTAMP     | NULL                 | 수정 일시        |

### ROLE 값

| 값          | 설명      |
| ---------- | ------- |
| `citizen`  | 일반 사용자  |
| `farmer`   | 농장주     |
| `ranger`   | 산림관리원   |
| `official` | 지자체 담당자 |
| `admin`    | 관리자     |

---

## 6. RISK_PREDICTION_LOGS 테이블

### 설명

위험 점수 예측 API 실행 결과를 저장한다.

현재 API는 회귀 모델 기반으로 `predicted_score`를 반환하므로, DB도 위험 등급뿐 아니라 위험 점수를 함께 저장해야 한다.

### 컬럼 정의

| 컬럼명                   | 타입             | 제약조건                 | 설명                   |
| --------------------- | -------------- | -------------------- | -------------------- |
| `LOG_ID`              | NUMBER         | PK                   | 예측 기록 ID             |
| `USER_ID`             | NUMBER         | FK, NULL             | 사용자 ID, 비회원은 NULL 가능 |
| `DAY_TYPE`            | VARCHAR2(20)   | NOT NULL             | 주간 / 야간 여부           |
| `CAMERA_TYPE`         | VARCHAR2(20)   | NOT NULL             | RGB / IR             |
| `WEATHER`             | VARCHAR2(30)   | NOT NULL             | 날씨                   |
| `LOCATION_NAME`       | VARCHAR2(100)  | NOT NULL             | 관측 위치                |
| `TIME_ZONE`           | VARCHAR2(30)   | NOT NULL             | 시간대                  |
| `SEASON`              | VARCHAR2(30)   | NOT NULL             | 계절                   |
| `SPECIES`             | VARCHAR2(50)   | NOT NULL             | 동물 종                 |
| `OBJECT_COUNT`        | NUMBER         | NOT NULL             | 객체 수                 |
| `MAX_BBOX_AREA_RATIO` | NUMBER(10, 6)  | NOT NULL             | 최대 bbox 면적 비율        |
| `AVG_BBOX_AREA_RATIO` | NUMBER(10, 6)  | NOT NULL             | 평균 bbox 면적 비율        |
| `PREDICTED_SCORE`     | NUMBER(6, 2)   | NOT NULL             | 회귀 모델 예측 위험 점수       |
| `RISK_GRADE`          | VARCHAR2(20)   | NOT NULL             | low / medium / high  |
| `RISK_LEVEL`          | VARCHAR2(20)   | NULL                 | 기존 코드 호환용 등급         |
| `MODEL_TYPE`          | VARCHAR2(30)   | DEFAULT 'regression' | 모델 유형                |
| `MESSAGE`             | VARCHAR2(1000) | NULL                 | 대응 메시지               |
| `MAE`                 | NUMBER(10, 4)  | NULL                 | 모델 MAE               |
| `RMSE`                | NUMBER(10, 4)  | NULL                 | 모델 RMSE              |
| `R2_SCORE`            | NUMBER(10, 4)  | NULL                 | 모델 R2 Score          |
| `REQUEST_JSON`        | CLOB           | NULL                 | 원본 요청 JSON           |
| `RESPONSE_JSON`       | CLOB           | NULL                 | 원본 응답 JSON           |
| `CREATED_AT`          | TIMESTAMP      | DEFAULT SYSTIMESTAMP | 예측 일시                |

### 위험 등급 기준

| `PREDICTED_SCORE` | `RISK_GRADE` |
| ----------------- | ------------ |
| 0 이상 45 미만        | low          |
| 45 이상 70 미만       | medium       |
| 70 이상 100 이하      | high         |

---

## 7. VISION_DETECTION_LOGS 테이블

### 설명

2차 Vision 프로젝트에서 이미지 탐지 결과를 저장한다.

YOLO 모델이 이미지에서 야생동물을 탐지한 결과, bbox, confidence, 결과 이미지 경로 등을 저장한다.

### 컬럼 정의

| 컬럼명                   | 타입            | 제약조건                 | 설명                |
| --------------------- | ------------- | -------------------- | ----------------- |
| `DETECTION_ID`        | NUMBER        | PK                   | 탐지 기록 ID          |
| `USER_ID`             | NUMBER        | FK, NULL             | 사용자 ID            |
| `ORIGINAL_IMAGE_PATH` | VARCHAR2(500) | NOT NULL             | 업로드 원본 이미지 경로     |
| `RESULT_IMAGE_PATH`   | VARCHAR2(500) | NULL                 | bbox 표시 결과 이미지 경로 |
| `CLASS_NAME`          | VARCHAR2(100) | NULL                 | 탐지 클래스명           |
| `CONFIDENCE`          | NUMBER(8, 4)  | NULL                 | 탐지 신뢰도            |
| `BBOX_X1`             | NUMBER(10, 4) | NULL                 | bbox 좌상단 x        |
| `BBOX_Y1`             | NUMBER(10, 4) | NULL                 | bbox 좌상단 y        |
| `BBOX_X2`             | NUMBER(10, 4) | NULL                 | bbox 우하단 x        |
| `BBOX_Y2`             | NUMBER(10, 4) | NULL                 | bbox 우하단 y        |
| `DETECTION_COUNT`     | NUMBER        | DEFAULT 0            | 탐지 객체 수           |
| `RISK_HINT`           | VARCHAR2(500) | NULL                 | 탐지 결과 기반 위험 안내    |
| `REQUEST_JSON`        | CLOB          | NULL                 | 요청 정보             |
| `RESPONSE_JSON`       | CLOB          | NULL                 | 탐지 결과 JSON        |
| `CREATED_AT`          | TIMESTAMP     | DEFAULT SYSTIMESTAMP | 탐지 일시             |

---

## 8. CONSULTATION_LOGS 테이블

### 설명

3차 LLM, 4차 SLM에서 사용자의 질문과 AI 응답을 저장한다.

위험 점수 예측 결과나 이미지 탐지 결과를 바탕으로 야생동물 대응 상담을 제공할 때 사용한다.

### 컬럼 정의

| 컬럼명                 | 타입           | 제약조건                 | 설명                  |
| ------------------- | ------------ | -------------------- | ------------------- |
| `CONSULTATION_ID`   | NUMBER       | PK                   | 상담 기록 ID            |
| `USER_ID`           | NUMBER       | FK, NULL             | 사용자 ID              |
| `RISK_LOG_ID`       | NUMBER       | FK, NULL             | 연결된 위험 점수 예측 기록     |
| `DETECTION_ID`      | NUMBER       | FK, NULL             | 연결된 이미지 탐지 기록       |
| `MODEL_TYPE`        | VARCHAR2(30) | NOT NULL             | LLM / SLM           |
| `USER_MESSAGE`      | CLOB         | NOT NULL             | 사용자 질문              |
| `ASSISTANT_MESSAGE` | CLOB         | NOT NULL             | AI 응답               |
| `CONTEXT_JSON`      | CLOB         | NULL                 | 상담에 사용된 위험도/탐지 컨텍스트 |
| `CREATED_AT`        | TIMESTAMP    | DEFAULT SYSTIMESTAMP | 상담 일시               |

---

## 9. 테이블 관계

## 9.1 USERS - RISK_PREDICTION_LOGS

| 관계  | 설명                                               |
| --- | ------------------------------------------------ |
| 1:N | 한 명의 사용자는 여러 위험 점수 예측 기록을 가질 수 있다.               |
| FK  | `RISK_PREDICTION_LOGS.USER_ID` → `USERS.USER_ID` |
| 비고  | 비회원 예측은 저장하지 않거나 `USER_ID`를 NULL로 둘 수 있다.        |

## 9.2 USERS - VISION_DETECTION_LOGS

| 관계  | 설명                                                |
| --- | ------------------------------------------------- |
| 1:N | 한 명의 사용자는 여러 이미지 탐지 기록을 가질 수 있다.                  |
| FK  | `VISION_DETECTION_LOGS.USER_ID` → `USERS.USER_ID` |

## 9.3 USERS - CONSULTATION_LOGS

| 관계  | 설명                                            |
| --- | --------------------------------------------- |
| 1:N | 한 명의 사용자는 여러 상담 기록을 가질 수 있다.                  |
| FK  | `CONSULTATION_LOGS.USER_ID` → `USERS.USER_ID` |

## 9.4 RISK_PREDICTION_LOGS - CONSULTATION_LOGS

| 관계  | 설명                                                              |
| --- | --------------------------------------------------------------- |
| 1:N | 하나의 위험 점수 예측 결과를 기반으로 여러 상담이 생성될 수 있다.                          |
| FK  | `CONSULTATION_LOGS.RISK_LOG_ID` → `RISK_PREDICTION_LOGS.LOG_ID` |

## 9.5 VISION_DETECTION_LOGS - CONSULTATION_LOGS

| 관계  | 설명                                                                      |
| --- | ----------------------------------------------------------------------- |
| 1:N | 하나의 이미지 탐지 결과를 기반으로 여러 상담이 생성될 수 있다.                                    |
| FK  | `CONSULTATION_LOGS.DETECTION_ID` → `VISION_DETECTION_LOGS.DETECTION_ID` |

---

## 10. Oracle DDL 예시

## 10.1 USERS

```sql
CREATE TABLE USERS (
    USER_ID NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    USERNAME VARCHAR2(50) NOT NULL UNIQUE,
    PASSWORD_HASH VARCHAR2(255) NOT NULL,
    NAME VARCHAR2(50) NOT NULL,
    ROLE VARCHAR2(30) DEFAULT 'citizen' NOT NULL,
    ORGANIZATION VARCHAR2(100),
    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
    UPDATED_AT TIMESTAMP
);
```

## 10.2 RISK_PREDICTION_LOGS

```sql
CREATE TABLE RISK_PREDICTION_LOGS (
    LOG_ID NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    USER_ID NUMBER,

    DAY_TYPE VARCHAR2(20) NOT NULL,
    CAMERA_TYPE VARCHAR2(20) NOT NULL,
    WEATHER VARCHAR2(30) NOT NULL,
    LOCATION_NAME VARCHAR2(100) NOT NULL,
    TIME_ZONE VARCHAR2(30) NOT NULL,
    SEASON VARCHAR2(30) NOT NULL,
    SPECIES VARCHAR2(50) NOT NULL,

    OBJECT_COUNT NUMBER NOT NULL,
    MAX_BBOX_AREA_RATIO NUMBER(10, 6) NOT NULL,
    AVG_BBOX_AREA_RATIO NUMBER(10, 6) NOT NULL,

    PREDICTED_SCORE NUMBER(6, 2) NOT NULL,
    RISK_GRADE VARCHAR2(20) NOT NULL,
    RISK_LEVEL VARCHAR2(20),
    MODEL_TYPE VARCHAR2(30) DEFAULT 'regression',

    MESSAGE VARCHAR2(1000),
    MAE NUMBER(10, 4),
    RMSE NUMBER(10, 4),
    R2_SCORE NUMBER(10, 4),

    REQUEST_JSON CLOB,
    RESPONSE_JSON CLOB,
    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,

    CONSTRAINT FK_RISK_USER
        FOREIGN KEY (USER_ID)
        REFERENCES USERS(USER_ID)
);
```

## 10.3 VISION_DETECTION_LOGS

```sql
CREATE TABLE VISION_DETECTION_LOGS (
    DETECTION_ID NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    USER_ID NUMBER,

    ORIGINAL_IMAGE_PATH VARCHAR2(500) NOT NULL,
    RESULT_IMAGE_PATH VARCHAR2(500),

    CLASS_NAME VARCHAR2(100),
    CONFIDENCE NUMBER(8, 4),

    BBOX_X1 NUMBER(10, 4),
    BBOX_Y1 NUMBER(10, 4),
    BBOX_X2 NUMBER(10, 4),
    BBOX_Y2 NUMBER(10, 4),

    DETECTION_COUNT NUMBER DEFAULT 0,
    RISK_HINT VARCHAR2(500),

    REQUEST_JSON CLOB,
    RESPONSE_JSON CLOB,
    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,

    CONSTRAINT FK_VISION_USER
        FOREIGN KEY (USER_ID)
        REFERENCES USERS(USER_ID)
);
```

## 10.4 CONSULTATION_LOGS

```sql
CREATE TABLE CONSULTATION_LOGS (
    CONSULTATION_ID NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    USER_ID NUMBER,
    RISK_LOG_ID NUMBER,
    DETECTION_ID NUMBER,

    MODEL_TYPE VARCHAR2(30) NOT NULL,
    USER_MESSAGE CLOB NOT NULL,
    ASSISTANT_MESSAGE CLOB NOT NULL,
    CONTEXT_JSON CLOB,

    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,

    CONSTRAINT FK_CONSULT_USER
        FOREIGN KEY (USER_ID)
        REFERENCES USERS(USER_ID),

    CONSTRAINT FK_CONSULT_RISK
        FOREIGN KEY (RISK_LOG_ID)
        REFERENCES RISK_PREDICTION_LOGS(LOG_ID),

    CONSTRAINT FK_CONSULT_DETECTION
        FOREIGN KEY (DETECTION_ID)
        REFERENCES VISION_DETECTION_LOGS(DETECTION_ID)
);
```

---

## 11. 인덱스 설계

```sql
CREATE INDEX IDX_RISK_USER_ID
ON RISK_PREDICTION_LOGS(USER_ID);

CREATE INDEX IDX_RISK_CREATED_AT
ON RISK_PREDICTION_LOGS(CREATED_AT);

CREATE INDEX IDX_RISK_GRADE
ON RISK_PREDICTION_LOGS(RISK_GRADE);

CREATE INDEX IDX_VISION_USER_ID
ON VISION_DETECTION_LOGS(USER_ID);

CREATE INDEX IDX_CONSULT_USER_ID
ON CONSULTATION_LOGS(USER_ID);
```

---

## 12. 현재 구현 상태와 ERD 반영 상태

| 항목                   | 상태                                   |
| -------------------- | ------------------------------------ |
| 사용자 테이블              | 기존 구현 기반 유지                          |
| 위험도 예측 기록            | 회귀 모델 구조에 맞춰 수정 필요                   |
| 이미지 탐지 기록            | 2차 Vision 확장용 설계                     |
| 상담 기록                | 3차 LLM / 4차 SLM 확장용 설계               |
| `predicted_score` 저장 | 반영                                   |
| `risk_grade` 저장      | 반영                                   |
| `metrics` 저장         | MAE, RMSE, R2 Score 반영               |
| JSON 원본 저장           | `REQUEST_JSON`, `RESPONSE_JSON`으로 반영 |

---

## 13. 향후 수정 대상

| 파일                                   | 수정 내용                                               |
| ------------------------------------ | --------------------------------------------------- |
| `services/risk_log_service.py`       | `predicted_score`, `risk_grade`, `metrics` 저장 구조 반영 |
| `routes/risk_routes.py`              | 로그인 사용자일 때 예측 결과 저장                                 |
| `templates/risk_history.html`        | 위험 점수 기반 기록 표시                                      |
| `docs/wildguard_oracle_db_setup.md`  | 실제 Oracle 생성 SQL을 ERD와 맞게 수정                        |
| `docs/wildguard_web_service_spec.md` | 저장 여부와 기록 조회 구조 반영                                  |

---

## 14. 비고

현재 1차 ML의 위험 점수 `risk_score`는 실제 사고 피해 데이터가 아니라 AI Hub 메타데이터 기반 도메인 가중치로 설계한 점수이다.

따라서 DB에는 예측 점수와 등급뿐 아니라 입력값, 모델 유형, 성능 지표, 원본 JSON 응답을 함께 저장하여 향후 실제 신고 데이터 또는 피해 기록과 비교 및 고도화할 수 있도록 한다.
