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

## 2. AI Hub 메타데이터 기반 1차 ML 방향 변경

### 증상

AI Hub JSON에서 만든 위험도 모델의 정확도가 매우 높게 나왔지만, 실제 서비스 입력과 맞지 않았다.

```text
day, camera_type, weather, location, time_zone, object_count, bbox_ratio
```

### 원인

AI Hub 데이터는 동물이 이미 촬영된 이미지 중심이라 출현하지 않은 경우와 비교하기 어렵다. 또한 object_count와 bbox_ratio는 일반 사용자가 입력하기 어렵고, 2차 Vision 결과에 가까운 값이다.

### 해결

1차 ML은 서울시 멧돼지 민원신고 현황 기반으로 변경한다.

```text
입력: 자치구, 월
출력: low / medium / high 위험도
```

AI Hub 데이터는 2차 YOLO 객체 탐지에 사용한다.

---

## 3. 서울시 멧돼지 모델 feature 부족 문제

### 증상

초기 모델 feature가 적어 성능이 낮았다.

```text
자치구, 월, 계절
Accuracy: 0.458
```

### 해결

원본 CSV에서 파생 feature를 추가했다.

```text
연도
자치구
월
계절
district_total_count
district_avg_count
month_avg_count
district_month_avg_count
district_total_capture
```

개선 결과:

```text
Accuracy: 0.722
```

---

## 4. risk_prediction_service.py는 수정했는데 옛날 필수 입력 오류 발생

### 증상

```text
필수 입력이 없습니다:
['day', 'camera_type', 'weather', 'location', 'time_zone', 'season',
 'object_count', 'max_bbox_area_ratio', 'avg_bbox_area_ratio']
```

### 원인

`risk_prediction_service.py`는 새 모델 기준으로 수정되었지만, `routes/risk_routes.py` 또는 DB 저장 서비스에서 옛날 feature를 계속 요구하고 있었다.

### 해결

`routes/risk_routes.py`의 required fields를 아래처럼 변경한다.

```python
required_fields = ["district", "month"]
```

API 입력도 아래처럼 변경한다.

```python
result = predict_risk({
    "district": input_data.get("district"),
    "month": input_data.get("month"),
})
```

DB 저장은 새 테이블 구조가 준비될 때까지 잠시 끈다.

---

## 5. camera_type is not defined

### 증상

```text
name 'camera_type' is not defined
```

### 원인

`routes/risk_routes.py`에서 기존 DB 저장 코드가 남아 있었다.

```python
camera_type=camera_type
```

하지만 새 모델 입력에는 `camera_type`이 없다.

### 해결

DB 저장 코드를 잠시 비활성화하거나, `seoul_boar_risk_log` 기준 저장 함수로 교체한다.

---

## 6. Cannot set properties of null

### 증상

```text
Cannot set properties of null (setting 'className')
```

또는

```text
Cannot set properties of null (setting 'clsName')
```

### 원인

JavaScript에서 찾는 HTML id가 실제 HTML에 없었다.

예:

```js
const actionBox = document.getElementById("actionBox");
actionBox.className = "action-box";
```

그런데 HTML에 `id="actionBox"`가 없었다.

### 해결

HTML에 id를 추가한다.

```html
<div id="actionBox" class="action-box">
    <strong>대응 안내</strong>
    <p id="actionMessage" style="margin-bottom: 0;"></p>
</div>
```

`clsName`은 오타이므로 `className`으로 수정한다.

---

## 7. 화면에 한글이 깨져 보임

### 증상

```text
???꾪뿕????쓬
```

### 원인

파일 인코딩 또는 편집기 저장 인코딩 문제일 수 있다.

### 해결

- HTML 파일을 UTF-8로 저장한다.
- PyCharm 하단 인코딩을 UTF-8로 맞춘다.
- `<meta charset="UTF-8">`가 있는지 확인한다.

---

## 8. ORA-00955

### 증상

```text
ORA-00955: name is already used by an existing object
```

### 원인

테이블, 시퀀스, 트리거가 이미 존재한다.

### 확인

```sql
SELECT object_name, object_type
FROM user_objects
WHERE object_name IN (
    'USERS',
    'USERS_SEQ',
    'TRG_USERS',
    'SEOUL_BOAR_RISK_LOG',
    'SEOUL_BOAR_RISK_LOG_SEQ',
    'TRG_SEOUL_BOAR_RISK_LOG'
);
```

---

## 9. ORA-00904 EMAIL

### 증상

```text
ORA-00904: "EMAIL": 부적합한 식별자
```

### 원인

EMAIL 컬럼이 없는데 삭제하거나 조회하려고 했다.

### 해결

DB는 정상이다. 코드와 HTML에서 email만 제거한다.

---

## 10. DPY-3010 thin mode 오류

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

## 11. CMD와 PowerShell 환경변수 차이

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

## 12. 집/학원 Oracle 설정

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

## 13. git push rejected

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

## 14. unstaged changes 때문에 pull 실패

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

## 15. rebase 충돌

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

## 16. GitHub 제외 파일

```text
data/
models/ml/
*.pkl
*.joblib
*.pt
.env
.venv/
__pycache__/
.idea/
```

---

## 17. Codex 토큰 오류

### 증상

```text
Your access token could not be refreshed.
Maximum resubmit count exceeded
```

### 해결 방향

Codex 없이 직접 구현한다. 핵심 기능은 파일 직접 수정으로 진행 가능하다.

---

## 18. 로그인 사용자만 DB 저장

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

단, 현재는 `seoul_boar_risk_log` 구조에 맞게 저장 함수를 수정한 뒤 다시 연결해야 한다.
