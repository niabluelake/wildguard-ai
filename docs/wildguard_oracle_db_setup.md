# WildGuard AI Oracle DB 환경 설정 문서

이 문서는 WildGuard AI 프로젝트에서 **집 PC와 학원 PC를 오가며 Oracle DB를 연결하는 방법**을 정리한 문서입니다.

프로젝트는 Python Flask + Oracle DB + SQL Developer를 사용합니다.

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

SQL Developer만 설치하면 DB가 생기는 것이 아닙니다. 실제 DB 서버인 **Oracle Database XE**가 설치되어 있어야 합니다.

---

## 2. PC별 Oracle 연결 차이

집 PC와 학원 PC는 Oracle 환경이 다릅니다.

| 구분 | 집 PC | 학원 PC |
|---|---|---|
| Oracle 버전 | Oracle 21c XE | 구버전 Oracle XE |
| 접속 호스트 | `192.168.219.103` | `localhost` |
| 서비스 이름 | `XEPDB1` | `XE` |
| python-oracledb 모드 | Thin mode | Thick mode |
| Oracle Client 필요 | 필요 없음 | 필요함 |
| Instant Client 경로 | 없음 | `C:\oraclexe\instantclient_19_25` |
| 추천 실행 터미널 | CMD | CMD |

---

## 3. Oracle 서비스 확인

CMD에서 Oracle 서비스가 설치되어 있는지 확인합니다.

```cmd
sc query | findstr /I Oracle
```

정상적으로 설치되어 있으면 다음과 비슷하게 나옵니다.

### 집 PC 예시

```text
OracleOraDB21Home1TNSListener
OracleServiceXE
OracleOraDB21Home1MTSRecoveryService
```

### 학원 PC 예시

```text
OracleServiceXE
OracleXETNSListener
```

서비스 실행 상태 확인:

```cmd
sc query OracleServiceXE
```

리스너 확인:

```cmd
sc query OracleOraDB21Home1TNSListener
```

또는 학원 PC에서는:

```cmd
sc query OracleXETNSListener
```

정상 상태:

```text
STATE              : 4  RUNNING
```

서비스 시작은 관리자 권한 CMD에서 실행해야 합니다.

```cmd
net start OracleServiceXE
net start OracleOraDB21Home1TNSListener
```

권한이 없으면 다음 오류가 납니다.

```text
시스템 오류 5이(가) 생겼습니다.
액세스가 거부되었습니다.
```

이 경우 CMD를 관리자 권한으로 실행해야 합니다.

---

## 4. SQL Developer 접속 순서

처음에는 반드시 `system` 계정으로 먼저 접속합니다.

### 4-1. 집 PC system 접속

집 PC는 보통 다음 설정으로 접속합니다.

```text
접속 이름: system_xe
사용자 이름: system
비밀번호: Oracle 설치 시 설정한 비밀번호
호스트 이름: 192.168.219.103
포트: 1521
서비스 이름: XEPDB1
```

집 PC에서는 `localhost`가 아니라 `192.168.219.103`으로 접속해야 했습니다.

포트 확인:

```cmd
netstat -ano | findstr :1521
```

실제 결과 예시:

```text
TCP    192.168.219.103:1521   0.0.0.0:0   LISTENING
```

이 경우 SQL Developer의 호스트 이름도 `192.168.219.103`으로 맞춥니다.

### 4-2. 학원 PC system 접속

학원 PC는 다음 설정을 사용합니다.

```text
접속 이름: system_xe
사용자 이름: system
비밀번호: Oracle 설치 시 설정한 비밀번호
호스트 이름: localhost
포트: 1521
서비스 이름 또는 SID: XE
```

학원 PC는 `XE`로 접속되었습니다.

---

## 5. wildguard 계정 생성

`system` 계정으로 접속한 뒤 SQL 워크시트에서 실행합니다.

```sql
CREATE USER wildguard IDENTIFIED BY wildguard123;

GRANT CONNECT, RESOURCE TO wildguard;

ALTER USER wildguard QUOTA UNLIMITED ON USERS;
```

이미 계정이 존재하면 다음 SQL로 비밀번호 초기화 및 잠금 해제를 합니다.

```sql
ALTER USER wildguard IDENTIFIED BY wildguard123 ACCOUNT UNLOCK;
```

---

## 6. wildguard 접속 정보

### 집 PC

```text
접속 이름: wildguard
사용자 이름: wildguard
비밀번호: wildguard123
호스트 이름: 192.168.219.103
포트: 1521
서비스 이름: XEPDB1
```

### 학원 PC

```text
접속 이름: wildguard
사용자 이름: wildguard
비밀번호: wildguard123
호스트 이름: localhost
포트: 1521
서비스 이름 또는 SID: XE
```

---

## 7. risk_prediction_log 테이블 생성

`wildguard` 접속으로 SQL 워크시트를 열고 실행합니다.

```sql
CREATE TABLE risk_prediction_log (
    log_id NUMBER PRIMARY KEY,
    day VARCHAR2(20),
    camera_type VARCHAR2(20),
    weather VARCHAR2(30),
    location VARCHAR2(100),
    time_zone VARCHAR2(20),
    season VARCHAR2(20),
    object_count NUMBER,
    max_bbox_area_ratio NUMBER,
    avg_bbox_area_ratio NUMBER,
    risk_level VARCHAR2(20),
    risk_message VARCHAR2(500),
    created_at DATE DEFAULT SYSDATE
);
```

---

## 8. 시퀀스 생성

구버전 Oracle XE에서는 `IDENTITY` 문법이 맞지 않아 오류가 발생했습니다.

오류 예시:

```text
ORA-02000: missing ALWAYS keyword
```

그래서 `IDENTITY` 대신 **시퀀스 + 트리거** 방식을 사용합니다.

```sql
CREATE SEQUENCE risk_prediction_log_seq
START WITH 1
INCREMENT BY 1
NOCACHE;
```

이미 존재하면 다음 오류가 나올 수 있습니다.

```text
ORA-00955: name is already used by an existing object
```

이 경우 이미 생성된 것이므로 다음 단계로 넘어가면 됩니다.

---

## 9. 트리거 생성

```sql
CREATE OR REPLACE TRIGGER trg_risk_prediction_log
BEFORE INSERT ON risk_prediction_log
FOR EACH ROW
BEGIN
    IF :NEW.log_id IS NULL THEN
        SELECT risk_prediction_log_seq.NEXTVAL
        INTO :NEW.log_id
        FROM dual;
    END IF;
END;
/
```

마지막 `/`까지 실행해야 트리거가 컴파일됩니다.

---

## 10. INSERT 테스트

```sql
INSERT INTO risk_prediction_log (
    day,
    camera_type,
    weather,
    location,
    time_zone,
    season,
    object_count,
    max_bbox_area_ratio,
    avg_bbox_area_ratio,
    risk_level,
    risk_message
) VALUES (
    'night',
    'IR',
    'cloudy',
    'mountain',
    'night',
    'winter',
    3,
    0.08,
    0.04,
    'high',
    'Oracle 연결 테스트입니다.'
);

COMMIT;
```

확인:

```sql
SELECT *
FROM risk_prediction_log
ORDER BY log_id DESC;
```

`LOG_ID`가 자동으로 들어가면 시퀀스/트리거가 정상입니다.

테스트 데이터 삭제:

```sql
DELETE FROM risk_prediction_log;

COMMIT;
```

---

## 11. Python 패키지 설치

프로젝트 가상환경에서 실행합니다.

```cmd
cd /d E:\WildGuard_AI
.venv\Scripts\activate
pip install oracledb
```

집 PC 경로가 다른 경우:

```cmd
cd /d E:\Projects\wildguard-ai
.venv\Scripts\activate
pip install oracledb
```

설치 확인:

```cmd
pip show oracledb
```

---

## 12. 공통 DB 설정 코드

파일 위치:

```text
config\db_config.py
```

집/학원 환경 차이를 환경변수로 제어하는 공통 코드입니다.

```python
import os
from contextlib import contextmanager

import oracledb


DB_USER = os.getenv("DB_USER", "wildguard")
DB_PASSWORD = os.getenv("DB_PASSWORD", "wildguard123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "1521"))
DB_SERVICE_NAME = os.getenv("DB_SERVICE_NAME", "XE")

ORACLE_CLIENT_DIR = os.getenv("ORACLE_CLIENT_DIR", "")
USE_ORACLE_THICK_MODE = os.getenv("USE_ORACLE_THICK_MODE", "false").lower() == "true"


def init_oracle_client():
    if not USE_ORACLE_THICK_MODE:
        return

    if not ORACLE_CLIENT_DIR:
        return

    try:
        oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_DIR)
    except oracledb.ProgrammingError:
        pass


def get_dsn() -> str:
    return oracledb.makedsn(
        host=DB_HOST,
        port=DB_PORT,
        service_name=DB_SERVICE_NAME,
    )


def get_connection() -> oracledb.Connection:
    init_oracle_client()

    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=get_dsn(),
    )


@contextmanager
def db_connection():
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()
```

---

## 13. DB 공통 서비스 코드

파일 위치:

```text
services\db_service.py
```

```python
from config.db_config import db_connection


def fetch_all(query, params=None):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or {})
            columns = [column[0].lower() for column in cursor.description]

            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]


def fetch_one(query, params=None):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or {})
            row = cursor.fetchone()

            if row is None:
                return None

            columns = [column[0].lower() for column in cursor.description]
            return dict(zip(columns, row))


def execute(query, params=None):
    with db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or {})
                affected_rows = cursor.rowcount

            connection.commit()
            return affected_rows
        except Exception:
            connection.rollback()
            raise


def execute_many(query, params_list):
    with db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.executemany(query, params_list)
                affected_rows = cursor.rowcount

            connection.commit()
            return affected_rows
        except Exception:
            connection.rollback()
            raise
```

---

## 14. Oracle 연결 테스트 코드

파일 위치:

```text
scripts\test_oracle_connection.py
```

```python
from services.db_service import fetch_one


result = fetch_one("SELECT 'Oracle 연결 성공' AS message FROM dual")
print(result)
```

정상 결과:

```text
{'message': 'Oracle 연결 성공'}
```

---

## 15. 학원 PC 실행 방법

학원 PC는 구버전 Oracle XE라서 `thick mode`가 필요합니다.

반드시 CMD에서 실행합니다.

```cmd
cd /d E:\WildGuard_AI
.venv\Scripts\activate

set DB_HOST=localhost
set DB_SERVICE_NAME=XE
set USE_ORACLE_THICK_MODE=true
set ORACLE_CLIENT_DIR=C:\oraclexe\instantclient_19_25

python scripts\test_oracle_connection.py
```

정상 결과:

```text
{'message': 'Oracle 연결 성공'}
```

PowerShell에서는 CMD의 `set` 명령이 적용되지 않습니다.

PyCharm 터미널이 PowerShell이면 먼저 다음을 입력해서 CMD로 전환합니다.

```cmd
cmd
```

그다음 위 CMD 명령어를 실행합니다.

---

## 16. 집 PC 실행 방법

집 PC는 Oracle 21c XE라서 `thin mode`로 연결할 수 있습니다.

```cmd
cd /d E:\Projects\wildguard-ai
.venv\Scripts\activate

set DB_HOST=192.168.219.103
set DB_SERVICE_NAME=XEPDB1
set USE_ORACLE_THICK_MODE=false
set ORACLE_CLIENT_DIR=

python scripts\test_oracle_connection.py
```

정상 결과:

```text
{'message': 'Oracle 연결 성공'}
```

---

## 17. 주요 오류와 해결

### 17-1. ModuleNotFoundError: No module named 'oracledb'

원인:

```text
현재 가상환경에 oracledb가 설치되지 않음
```

해결:

```cmd
pip install oracledb
```

---

### 17-2. ModuleNotFoundError: No module named 'services'

원인:

```text
프로젝트 루트 기준 import 경로 문제
```

해결:

```cmd
type nul > services\__init__.py
type nul > config\__init__.py
type nul > scripts\__init__.py
```

또는 테스트 파일에서 루트 경로를 추가합니다.

```python
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
```

---

### 17-3. DPY-3010: thin mode not supported

원인:

```text
구버전 Oracle XE에 python-oracledb thin mode로 접속하려고 함
```

해결:

학원 PC에서는 thick mode를 켭니다.

```cmd
set USE_ORACLE_THICK_MODE=true
set ORACLE_CLIENT_DIR=C:\oraclexe\instantclient_19_25
```

---

### 17-4. DPI-1047: Cannot locate a 64-bit Oracle Client library

원인:

```text
thick mode를 켰지만 Oracle Instant Client 경로가 없거나 틀림
```

해결:

```cmd
dir C:\oraclexe\instantclient_19_25
```

다음 파일이 있는지 확인합니다.

```text
oci.dll
oraociei19.dll
```

집 PC에서는 thick mode를 끕니다.

```cmd
set USE_ORACLE_THICK_MODE=false
set ORACLE_CLIENT_DIR=
```

---

### 17-5. ORA-12541: 리스너가 없습니다

원인:

```text
Oracle Listener가 꺼져 있거나, 다른 호스트/포트에서 대기 중
```

해결:

```cmd
sc query OracleOraDB21Home1TNSListener
netstat -ano | findstr :1521
```

집 PC에서는 `localhost`가 아니라 `192.168.219.103`에서 리스너가 열려 있었습니다.

---

### 17-6. ORA-01017: 사용자명/비밀번호가 부적합

원인:

```text
계정이 없거나 비밀번호가 다름
또는 XE/XEPDB1 접속 위치가 다름
```

해결:

먼저 `system`으로 접속한 뒤 계정을 생성 또는 초기화합니다.

```sql
ALTER USER wildguard IDENTIFIED BY wildguard123 ACCOUNT UNLOCK;
```

---

### 17-7. ORA-00955: name is already used by an existing object

원인:

```text
같은 이름의 테이블, 시퀀스, 트리거가 이미 존재함
```

해결:

이미 생성된 것이므로 다음 단계로 진행하면 됩니다.

---

## 18. Flask 실행 후 DB 저장 확인

Flask 실행:

```cmd
python app.py
```

위험도 예측 페이지에서 예측을 한 번 실행합니다.

SQL Developer에서 확인:

```sql
SELECT *
FROM risk_prediction_log
ORDER BY log_id DESC;
```

새 행이 들어오면 다음 흐름이 완성된 것입니다.

```text
위험도 예측 입력
→ ML 모델 예측
→ Flask API 결과 반환
→ Oracle DB risk_prediction_log 저장
```

---

## 19. GitHub에 올릴 파일 / 올리면 안 되는 파일

### 올려도 되는 파일

```text
config/db_config.py
services/db_service.py
services/risk_log_service.py
scripts/test_oracle_connection.py
scripts/convert_aihub_json_to_csv.py
scripts/train_risk_model.py
routes/risk_routes.py
requirements.txt
```

### 올리면 안 되는 파일

```text
data/
models/ml/
*.pkl
.env
aihub_wildlife_metadata.csv
TL-quadruped/
```

`.gitignore`에 포함 권장:

```text
.venv/
__pycache__/
*.pyc
.env
.idea/
data/
models/ml/
*.pkl
*.joblib
```

Git 저장:

```cmd
git status
git add config services scripts routes requirements.txt
git status
git commit -m "docs: add oracle db setup and environment guide"
git push
```

---

## 20. 최종 PC별 실행 요약

### 학원 PC

```cmd
cd /d E:\WildGuard_AI
.venv\Scripts\activate

set DB_HOST=localhost
set DB_SERVICE_NAME=XE
set USE_ORACLE_THICK_MODE=true
set ORACLE_CLIENT_DIR=C:\oraclexe\instantclient_19_25

python scripts\test_oracle_connection.py
python app.py
```

### 집 PC

```cmd
cd /d E:\Projects\wildguard-ai
.venv\Scripts\activate

set DB_HOST=192.168.219.103
set DB_SERVICE_NAME=XEPDB1
set USE_ORACLE_THICK_MODE=false
set ORACLE_CLIENT_DIR=

python scripts\test_oracle_connection.py
python app.py
```

---

## 21. 현재 결론

집 PC와 학원 PC는 Oracle 연결 방식이 다르므로, DB 설정을 코드에 고정하지 않고 환경변수로 분리해야 합니다.

```text
집 PC  → Oracle 21c XE / XEPDB1 / thin mode
학원 PC → Oracle XE / XE / thick mode / Instant Client 필요
```

CMD에서 환경변수를 설정한 뒤 실행하면 두 환경 모두 같은 코드로 Oracle DB에 연결할 수 있습니다.