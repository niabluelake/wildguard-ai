  # WildGuard AI GitHub 정리 가이드

> 목적: 집 PC와 학원 PC를 오가며 WildGuard AI 프로젝트를 안전하게 동기화하기 위한 GitHub 사용 규칙 정리

---

## 1. GitHub에 올릴 것

코드, 문서, 설정 예시 파일은 GitHub에 올린다.

```text
app.py
routes/
services/
config/
scripts/
templates/
static/
docs/
requirements.txt
README.md
.gitignore
```

특히 이번에 올려야 하는 주요 파일은 다음과 같다.

```text
config/db_config.py
services/db_service.py
services/risk_log_service.py
scripts/convert_aihub_json_to_csv.py
scripts/train_risk_model.py
scripts/test_oracle_connection.py
routes/risk_routes.py
requirements.txt
docs/wildguard_oracle_db_setup.md
```

---

## 2. GitHub에 올리면 안 되는 것

AI Hub 원본 데이터, 변환 CSV, 학습된 모델 파일, 개인 환경 설정은 GitHub에 올리지 않는다.

```text
data/
models/ml/
*.pkl
*.joblib
.env
.venv/
__pycache__/
.idea/
```

이유:

- `data/`에는 AI Hub 원본 JSON과 변환 CSV가 들어간다.
- `models/ml/risk_model.pkl`은 학습 결과 파일이라 PC마다 다시 생성한다.
- `.env`에는 DB 비밀번호나 PC별 Oracle 설정이 들어갈 수 있다.
- `.venv/`는 가상환경이라 GitHub에 올리지 않는다.
- `.idea/`는 PyCharm 개인 설정이다.

---

## 3. 권장 `.gitignore`

프로젝트 루트의 `.gitignore`에 아래 내용이 포함되어 있어야 한다.

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual environment
.venv/
venv/

# Environment variables
.env

# PyCharm
.idea/

# Data
data/
data/aihub_json/
data/aihub/
data/aihub/ml_dataset/
data/aihub/aihub_json/

# Models
models/ml/
*.pkl
*.joblib

# OS
.DS_Store
Thumbs.db
```

---

## 4. 집 PC / 학원 PC 환경 차이

### 집 PC

```text
DB_HOST=192.168.219.103
DB_SERVICE_NAME=XEPDB1
USE_ORACLE_THICK_MODE=false
ORACLE_CLIENT_DIR=
```

집 PC는 Oracle 21c XE라서 python-oracledb thin mode로 연결 가능했다.

### 학원 PC

```text
DB_HOST=localhost
DB_SERVICE_NAME=XE
USE_ORACLE_THICK_MODE=true
ORACLE_CLIENT_DIR=C:\oraclexe\instantclient_19_25
```

학원 PC는 Oracle 버전이 낮아서 python-oracledb thin mode가 지원되지 않았다.  
따라서 Instant Client를 사용하는 thick mode가 필요하다.

---

## 5. CMD 기준 환경변수 설정

### 학원 PC 실행 전

```cmd
cd /d E:\WildGuard_AI
.venv\Scripts\activate

set DB_HOST=localhost
set DB_SERVICE_NAME=XE
set USE_ORACLE_THICK_MODE=true
set ORACLE_CLIENT_DIR=C:\oraclexe\instantclient_19_25

python scripts\test_oracle_connection.py
```

성공 예시:

```text
{'message': 'Oracle 연결 성공'}
```

### 집 PC 실행 전

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

## 6. GitHub에 올리기 전 확인 순서

항상 커밋 전에는 `git status`를 먼저 확인한다.

```cmd
cd /d E:\WildGuard_AI
git status
```

또는 집 PC:

```cmd
cd /d E:\Projects\wildguard-ai
git status
```

아래 항목이 보이면 커밋하면 안 된다.

```text
data/
models/ml/
risk_model.pkl
aihub_wildlife_metadata.csv
TL-quadruped/
.env
.venv/
```

---

## 7. 안전한 Git add 방식

전체 추가보다 필요한 파일만 추가하는 것이 안전하다.

```cmd
git add config
git add services
git add scripts
git add routes
git add docs
git add requirements.txt
git add README.md
git add .gitignore
```

그 다음 다시 확인한다.

```cmd
git status
```

---

## 8. 커밋 메시지 예시

Oracle DB 설정과 변환 스크립트를 정리한 경우:

```cmd
git commit -m "fix: support oracle db config across environments"
```

AI Hub JSON 변환 스크립트를 추가한 경우:

```cmd
git commit -m "feat: add aihub json conversion script"
```

문서 정리를 추가한 경우:

```cmd
git commit -m "docs: add oracle and github setup guides"
```

여러 작업을 한 번에 정리한 경우:

```cmd
git commit -m "chore: organize db setup and project sync docs"
```

---

## 9. GitHub 푸시

```cmd
git push
```

---

## 10. 다른 PC에서 가져오기

학원 PC에서 집 PC 작업을 가져올 때:

```cmd
cd /d E:\WildGuard_AI
git pull
```

집 PC에서 학원 PC 작업을 가져올 때:

```cmd
cd /d E:\Projects\wildguard-ai
git pull
```

---

## 11. 데이터와 모델 복구 흐름

GitHub에는 데이터와 모델을 올리지 않기 때문에, PC마다 아래 작업을 다시 수행한다.

### 1. AI Hub TL JSON 위치 맞추기

권장 구조:

```text
data/
└─ aihub/
   ├─ aihub_json/
   │  └─ TL-quadruped/
   └─ ml_dataset/
```

### 2. JSON → CSV 변환

```cmd
python scripts\convert_aihub_json_to_csv.py
```

정상 분포 예시:

```text
medium    18652
high      10196
low        1852
```

### 3. 모델 학습

```cmd
python scripts\train_risk_model.py
```

생성 파일:

```text
models\ml\risk_model.pkl
```

### 4. Flask 실행

```cmd
python app.py
```

---

## 12. 최종 작업 루틴

작업 시작할 때:

```cmd
cd /d E:\WildGuard_AI
git pull
.venv\Scripts\activate
```

작업 완료 후:

```cmd
git status
git add config services scripts routes docs requirements.txt README.md .gitignore
git status
git commit -m "작업 내용"
git push
```

---

## 13. 핵심 규칙

```text
코드와 문서는 GitHub에 올린다.
데이터와 모델은 GitHub에 올리지 않는다.
PC별 DB 설정은 환경변수로 처리한다.
학원 PC는 CMD + thick mode를 사용한다.
집 PC는 thin mode를 사용한다.
작업 전 git pull, 작업 후 git push를 습관화한다.
```
