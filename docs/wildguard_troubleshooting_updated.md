# WildGuard AI 트러블슈팅 문서

## 1. JSON 경로 오류

### 증상
```text
FileNotFoundError: JSON 폴더가 없습니다
```

### 해결
```cmd
cd /d E:\WildGuard_AI
dir data\aihub\aihub_json\TL-quadruped
dir data\aihub\aihub_json\TL-quadruped\*.json /s /b | find /c /v ""
```

권장 구조:
```text
data\aihub\aihub_json\TL-quadruped
```

---

## 2. JSON 변환값 unknown 문제

### 원인
AI Hub JSON의 `images`가 리스트이고 bbox가 `[[x1,y1],[x2,y2]]` 구조였는데 잘못 파싱했다.

### 해결
- `images[0]` 사용
- bbox 좌표쌍 처리
- date_created에서 시간대와 계절 추출

정상 분포:
```text
medium 약 18600
high 10196
low 약 1800
```

---

## 3. ORA-00955

### 증상
```text
ORA-00955: name is already used by an existing object
```

### 원인
USERS, USERS_SEQ, TRG_USERS가 이미 존재한다.

### 확인
```sql
SELECT object_name, object_type
FROM user_objects
WHERE object_name IN ('USERS', 'USERS_SEQ', 'TRG_USERS');

DESC users;
```

---

## 4. ORA-00904 EMAIL

### 증상
```text
ORA-00904: "EMAIL": 부적합한 식별자
```

### 원인
EMAIL 컬럼이 없는데 삭제하려고 했다.

### 해결
DB는 정상이다. 코드와 HTML에서 email만 제거한다.

---

## 5. DPY-3010 thin mode 오류

### 증상
```text
DPY-3010: connections to this database server version are not supported
```

### 해결
학원 PC는 thick mode 사용.

```cmd
set DB_HOST=localhost
set DB_SERVICE_NAME=XE
set USE_ORACLE_THICK_MODE=true
set ORACLE_CLIENT_DIR=C:\oraclexe\instantclient_19_25
python scripts\test_oracle_connection.py
```

---

## 6. CMD와 PowerShell 환경변수 차이

CMD:
```cmd
set DB_HOST=localhost
```

PowerShell:
```powershell
$env:DB_HOST="localhost"
```

프로젝트에서는 CMD 기준으로 진행한다.

---

## 7. 집/학원 Oracle 설정

### 집 PC
```cmd
set DB_HOST=192.168.219.103
set DB_SERVICE_NAME=XEPDB1
set USE_ORACLE_THICK_MODE=false
set ORACLE_CLIENT_DIR=
```

### 학원 PC
```cmd
set DB_HOST=localhost
set DB_SERVICE_NAME=XE
set USE_ORACLE_THICK_MODE=true
set ORACLE_CLIENT_DIR=C:\oraclexe\instantclient_19_25
```

---

## 8. git push rejected

### 증상
```text
! [rejected] main -> main (fetch first)
```

### 해결
```cmd
git status
git add app.py routes services templates static config scripts docs database requirements.txt README.md .gitignore
git commit -m "작업 내용"
git pull --rebase origin main
git push origin main
```

---

## 9. unstaged changes 때문에 pull 실패

### 증상
```text
error: cannot pull with rebase: You have unstaged changes.
```

### 해결
변경사항을 커밋하거나 stash 후 pull한다.

```cmd
git stash push -m "temporary local changes"
git pull
```

또는:

```cmd
git add app.py routes services templates docs database
git commit -m "작업 내용"
git pull --rebase origin main
```

---

## 10. rebase 충돌

### 확인
```cmd
git diff --name-only --diff-filter=U
```

### 해결 예시
```cmd
git checkout --theirs docs\REQUIREMENTS_ANALYSIS.md
git add docs\REQUIREMENTS_ANALYSIS.md
git rebase --continue
git push origin main
```

---

## 11. _updated 문서명 문제

### 증상
```text
deleted: docs/PRD.md
untracked: docs/PRD_updated.md
```

### 해결
```cmd
copy docs\PRD_updated.md docs\PRD.md
del docs\PRD_updated.md
```

---

## 12. GitHub 제외 파일

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

---

## 13. Codex 토큰 오류

### 증상
```text
Your access token could not be refreshed.
Maximum resubmit count exceeded
```

### 해결 방향
Codex 없이 직접 구현한다. 핵심 기능은 파일 직접 수정으로 진행 가능하다.

---

## 14. 로그인 사용자만 DB 저장

정책:
```text
비회원: 예측 가능, DB 저장 안 함
로그인: 예측 가능, DB 저장
```

핵심:
```python
if "user_id" in session:
    save_risk_prediction_log(user_id=session["user_id"], ...)
    saved_to_db = True
else:
    saved_to_db = False
```

---

## 15. DB 변경사항 관리

Oracle DB 자체는 GitHub에 올라가지 않는다.  
SQL 변경 파일을 관리한다.

```text
database/migrations/001_add_auth_tables.sql
```

다른 PC에서는 git pull 후 SQL Developer에서 migration을 실행한다.