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
database/
requirements.txt
README.md
.gitignore
```

현재 서울시 멧돼지 위험도 모델 기준으로 특히 관리해야 하는 주요 파일은 다음과 같다.

```text
scripts/train_seoul_boar_risk_model.py
services/risk_prediction_service.py
routes/risk_routes.py
templates/risk.html
services/risk_log_service.py
database/migrations/
docs/
README.md
```

---

## 2. GitHub에 올리면 안 되는 것

원본 데이터, 변환 데이터, 학습된 모델 파일, 개인 환경 설정은 GitHub에 올리지 않는다.

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

- `data/`에는 서울시 CSV, AI Hub 원본 JSON, 변환 CSV가 들어갈 수 있다.
- `models/ml/seoul_boar_risk_model.pkl`은 학습 결과 파일이라 PC마다 다시 생성한다.
- `models/ml/seoul_boar_stats.pkl`은 학습 데이터 기반 통계 파일이라 GitHub에 올리지 않는다.
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

# IDE
.idea/
.vscode/

# Data
data/

# Models
models/ml/
*.pkl
*.joblib
*.pt

# OS
.DS_Store
Thumbs.db
```

---

## 4. 집 PC / 학원 PC 환경 차이

### 집 PC

```text
프로젝트 경로: E:\Projects\wildguard-ai
DB_HOST=192.168.219.103
DB_SERVICE_NAME=XEPDB1
USE_ORACLE_THICK_MODE=false
ORACLE_CLIENT_DIR=
```

집 PC는 Oracle 21c XE라서 python-oracledb thin mode로 연결 가능했다.

### 학원 PC

```text
프로젝트 경로: E:\WildGuard_AI
DB_HOST=localhost
DB_SERVICE_NAME=XE
USE_ORACLE_THICK_MODE=true
ORACLE_CLIENT_DIR=C:\oraclexe\instantclient_19_25
```

학원 PC는 Oracle 버전이 낮아서 python-oracledb thin mode가 지원되지 않았다. 따라서 Instant Client를 사용하는 thick mode가 필요하다.

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

## 6. 모델과 데이터 복구 흐름

GitHub에는 데이터와 모델을 올리지 않기 때문에, PC마다 아래 작업을 다시 수행한다.

### 1. 서울시 CSV 위치 맞추기

```text
data/
└─ seoul_wildlife/
   └─ seoul_boar_reports.csv
```

### 2. 모델 학습

```cmd
python scripts\train_seoul_boar_risk_model.py
```

생성 파일:

```text
models\ml\seoul_boar_risk_model.pkl
models\ml\seoul_boar_stats.pkl
```

### 3. Flask 실행

```cmd
python app.py
```

---

## 7. GitHub에 올리기 전 확인 순서

항상 커밋 전에는 `git status`를 먼저 확인한다.

집 PC:

```cmd
cd /d E:\Projects\wildguard-ai
git status
```

학원 PC:

```cmd
cd /d E:\WildGuard_AI
git status
```

아래 항목이 staged에 들어가 있으면 커밋하면 안 된다.

```text
data/
models/ml/
seoul_boar_risk_model.pkl
seoul_boar_stats.pkl
.env
.venv/
```

---

## 8. 안전한 Git add 방식

전체 추가보다 필요한 파일만 추가하는 것이 안전하다.

```cmd
git add app.py
git add routes
git add services
git add scripts
git add templates
git add static
git add config
git add docs
git add database
git add requirements.txt
git add README.md
git add .gitignore
```

그 다음 다시 확인한다.

```cmd
git status
```

모델이나 데이터가 staged에 들어갔다면 제거한다.

```cmd
git restore --staged data
git restore --staged models\ml
```

---

## 9. 커밋 메시지 예시

서울시 멧돼지 위험도 모델을 추가한 경우:

```cmd
git commit -m "feat: update risk prediction with Seoul boar report data"
```

문서를 정리한 경우:

```cmd
git commit -m "docs: update WildGuard service documents"
```

DB 저장 구조를 변경한 경우:

```cmd
git commit -m "feat: add Seoul boar risk log table"
```

오류를 수정한 경우:

```cmd
git commit -m "fix: align risk API with Seoul boar model inputs"
```

---

## 10. GitHub 푸시

```cmd
git pull --rebase origin main
git push origin main
```

---

## 11. 다른 PC에서 가져오기

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

## 12. 최종 작업 루틴

작업 시작할 때:

```cmd
cd /d E:\Projects\wildguard-ai
git pull
```

작업 후:

```cmd
git status
git add app.py routes services scripts templates static config docs database requirements.txt README.md .gitignore
git status
git commit -m "작업 내용"
git pull --rebase origin main
git push origin main
```

---

## 13. 충돌이 났을 때

충돌 파일 확인:

```cmd
git diff --name-only --diff-filter=U
```

수정 후:

```cmd
git add 충돌파일
git rebase --continue
git push origin main
```

---

## 14. 현재 프로젝트 기준 핵심 규칙

```text
1차 ML 데이터와 모델은 GitHub에 올리지 않는다.
서울시 CSV는 data/ 아래에 둔다.
학습 모델과 통계 pkl은 models/ml/ 아래에 둔다.
다른 PC에서는 CSV를 다시 배치하고 학습 스크립트를 실행한다.
문서와 코드는 GitHub로 관리한다.
```
