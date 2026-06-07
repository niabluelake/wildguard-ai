# WildGuard AI Oracle DB 환경 설정 문서

이 문서는 WildGuard AI 프로젝트에서 집 PC와 학원 PC를 오가며 Oracle DB를 연결하고, 서울시 멧돼지 위험도 예측 기록을 저장하는 방법을 정리한다.

프로젝트는 Python Flask + Oracle DB + SQL Developer를 사용한다.

---

## 1. 전체 구조

```text
WildGuard AI
├─ Flask 웹/REST API
├─ ML 위험도 예측 모델
├─ Oracle Database XE
├─ SQL Developer
└─ python-oracledb
```

역할 구분:

```text
Oracle Database XE = 실제 DB 서버
SQL Developer      = DB 접속/테이블 확인용 GUI
python-oracledb    = Flask 프로젝트에서 Oracle DB에 연결하는 Python 라이브러리
```

---

## 2. PC별 Oracle 연결 차이

| 구분 | 집 PC | 학원 PC |
|---|---|---|
| Oracle 버전 | Oracle 21c XE | 구버전 Oracle XE |
| 프로젝트 경로 | `E:\Projects\wildguard-ai` | `E:\WildGuard_AI` |
| 접속 호스트 | `192.168.219.103` | `localhost` |
| 서비스 이름 | `XEPDB1` | `XE` |
| python-oracledb 모드 | Thin mode | Thick mode |
| Oracle Client 필요 | 필요 없음 | 필요함 |
| Instant Client 경로 | 없음 | `C:\oraclexe\instantclient_19_25` |
| 추천 실행 터미널 | CMD | CMD |

---

## 3. Oracle 서비스 확인

CMD에서 Oracle 서비스가 설치되어 있는지 확인한다.

```cmd
sc query | findstr /I Oracle
```

서비스 실행 상태 확인:

```cmd
sc query OracleServiceXE
```

리스너 확인:

```cmd
sc query OracleOraDB21Home1TNSListener
```

학원 PC에서는 다음일 수 있다.

```cmd
sc query OracleXETNSListener
```

정상 상태:

```text
STATE              : 4  RUNNING
```

서비스 시작은 관리자 권한 CMD에서 실행해야 한다.

```cmd
net start OracleServiceXE
net start OracleOraDB21Home1TNSListener
```

---

## 4. wildguard 계정 생성

`system` 계정으로 접속한 뒤 SQL 워크시트에서 실행한다.

```sql
CREATE USER wildguard IDENTIFIED BY wildguard123;

GRANT CONNECT, RESOURCE TO wildguard;

ALTER USER wildguard QUOTA UNLIMITED ON USERS;
```

이미 계정이 존재하면 다음 SQL로 비밀번호 초기화 및 잠금 해제를 한다.

```sql
ALTER USER wildguard IDENTIFIED BY wildguard123 ACCOUNT UNLOCK;
```

---

## 5. USERS 테이블 생성

```sql
CREATE TABLE users (
    user_id NUMBER PRIMARY KEY,
    username VARCHAR2(50) UNIQUE NOT NULL,
    password_hash VARCHAR2(255) NOT NULL,
    name VARCHAR2(50) NOT NULL,
    organization VARCHAR2(100),
    role VARCHAR2(30) DEFAULT 'citizen',
    created_at DATE DEFAULT SYSDATE
);

CREATE SEQUENCE users_seq
START WITH 1
INCREMENT BY 1
NOCACHE;

CREATE OR REPLACE TRIGGER trg_users
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF :NEW.user_id IS NULL THEN
        SELECT users_seq.NEXTVAL INTO :NEW.user_id FROM dual;
    END IF;
END;
/
```

---

## 6. 서울시 멧돼지 위험도 예측 로그 테이블 생성

기존 `risk_prediction_log`는 AI Hub 메타데이터 기반 구조였다. 현재 1차 ML은 서울시 멧돼지 신고 데이터 기반이므로 새 테이블 `seoul_boar_risk_log`를 사용한다.

```sql
CREATE TABLE seoul_boar_risk_log (
    log_id NUMBER PRIMARY KEY,
    user_id NUMBER,
    district VARCHAR2(50),
    month NUMBER,
    year NUMBER,
    season VARCHAR2(20),
    risk_level VARCHAR2(20),
    risk_message VARCHAR2(500),
    district_total_count NUMBER,
    district_avg_count NUMBER,
    month_avg_count NUMBER,
    district_month_avg_count NUMBER,
    district_total_capture NUMBER,
    created_at DATE DEFAULT SYSDATE
);
```

---

## 7. 시퀀스 생성

구버전 Oracle XE 호환성을 위해 `IDENTITY` 대신 시퀀스 + 트리거 방식을 사용한다.

```sql
CREATE SEQUENCE seoul_boar_risk_log_seq
START WITH 1
INCREMENT BY 1
NOCACHE;
```

이미 존재하면 다음 오류가 나올 수 있다.

```text
ORA-00955: name is already used by an existing object
```

이 경우 이미 생성된 것이므로 다음 단계로 넘어가면 된다.

---

## 8. 트리거 생성

```sql
CREATE OR REPLACE TRIGGER trg_seoul_boar_risk_log
BEFORE INSERT ON seoul_boar_risk_log
FOR EACH ROW
BEGIN
    IF :NEW.log_id IS NULL THEN
        SELECT seoul_boar_risk_log_seq.NEXTVAL
        INTO :NEW.log_id
        FROM dual;
    END IF;
END;
/
```

마지막 `/`까지 실행해야 트리거가 컴파일된다.

---

## 9. INSERT 테스트

```sql
INSERT INTO seoul_boar_risk_log (
    user_id,
    district,
    month,
    year,
    season,
    risk_level,
    risk_message,
    district_total_count,
    district_avg_count,
    month_avg_count,
    district_month_avg_count,
    district_total_capture
) VALUES (
    1,
    '은평구',
    10,
    2024,
    '가을',
    'high',
    'Oracle 연결 테스트입니다.',
    275,
    7.64,
    3.2,
    9.0,
    272
);

COMMIT;
```

확인:

```sql
SELECT *
FROM seoul_boar_risk_log
ORDER BY log_id DESC;
```

테스트 데이터 삭제:

```sql
DELETE FROM seoul_boar_risk_log;

COMMIT;
```

---

## 10. Python 패키지 설치

집 PC:

```cmd
cd /d E:\Projects\wildguard-ai
.venv\Scripts\activate
pip install oracledb
```

학원 PC:

```cmd
cd /d E:\WildGuard_AI
.venv\Scripts\activate
pip install oracledb
```

설치 확인:

```cmd
pip show oracledb
```

---

## 11. DB 공통 설정 코드

파일 위치:

```text
config/db_config.py
```

환경변수로 집/학원 설정을 전환한다.

---

## 12. DB 공통 서비스 코드

파일 위치:

```text
services/db_service.py
```

권장 함수:

```text
fetch_one
fetch_all
execute_sql
```

또는 기존 코드에 맞춰 `execute`를 사용한다.

---

## 13. Oracle 연결 테스트

파일 위치:

```text
scripts/test_oracle_connection.py
```

```python
from services.db_service import fetch_one

result = fetch_one("SELECT 'Oracle 연결 성공' AS message FROM dual")
print(result)
```

---

## 14. 학원 PC 실행 방법

```cmd
cd /d E:\WildGuard_AI
.venv\Scripts\activate

set DB_HOST=localhost
set DB_SERVICE_NAME=XE
set USE_ORACLE_THICK_MODE=true
set ORACLE_CLIENT_DIR=C:\oraclexe\instantclient_19_25

python scripts\test_oracle_connection.py
```

---

## 15. 집 PC 실행 방법

```cmd
cd /d E:\Projects\wildguard-ai
.venv\Scripts\activate

set DB_HOST=192.168.219.103
set DB_SERVICE_NAME=XEPDB1
set USE_ORACLE_THICK_MODE=false
set ORACLE_CLIENT_DIR=

python scripts\test_oracle_connection.py
```

---

## 16. 주요 오류와 해결

### 16-1. ModuleNotFoundError: No module named 'oracledb'

```cmd
pip install oracledb
```

### 16-2. DPY-3010 thin mode 오류

학원 PC에서는 thick mode 사용.

```cmd
set USE_ORACLE_THICK_MODE=true
set ORACLE_CLIENT_DIR=C:\oraclexe\instantclient_19_25
```

### 16-3. DPI-1047 Oracle Client 오류

Instant Client 경로 확인.

```cmd
dir C:\oraclexe\instantclient_19_25
```

### 16-4. ORA-12541 리스너 없음

```cmd
sc query OracleServiceXE
netstat -ano | findstr :1521
```

---

## 17. 다음 연결 작업

1. `services/risk_log_service.py`를 `seoul_boar_risk_log` 기준으로 수정한다.
2. `routes/risk_routes.py`에서 로그인 사용자일 때 저장 기능을 다시 연결한다.
3. `/risk/history`를 새 컬럼 기준으로 수정한다.
