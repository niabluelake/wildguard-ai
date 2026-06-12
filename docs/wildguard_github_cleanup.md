# WildGuard AI GitHub 정리 및 작업 규칙

## 1. 문서 개요

본 문서는 WildGuard AI 프로젝트의 GitHub 저장소 관리 규칙을 정리한다.

WildGuard AI는 집 PC와 학원 PC를 오가며 작업하는 프로젝트이므로, GitHub 동기화 규칙을 지키지 않으면 코드 충돌, 파일 누락, 모델 파일 미존재 문제가 발생할 수 있다.

특히 AI Hub 원본 데이터, 변환 CSV, 학습 모델 파일은 용량과 라이선스 문제로 GitHub에 업로드하지 않는다.

---

## 2. 저장소 정보

| 항목         | 내용                         |
| ---------- | -------------------------- |
| GitHub 저장소 | `niabluelake/wildguard-ai` |
| 기본 브랜치     | `main`                     |
| 학원 PC 경로   | `E:\WildGuard_AI`          |
| 집 PC 경로    | `E:\Projects\wildguard-ai` |
| 주 사용 터미널   | CMD 기준                     |
| 가상환경       | `.venv`                    |

---

## 3. GitHub에 업로드하는 파일

GitHub에는 프로젝트를 재현할 수 있는 코드와 문서만 업로드한다.

| 대상          | 설명                                  |
| ----------- | ----------------------------------- |
| Python 코드   | Flask, ML 학습, 데이터 변환, API 코드        |
| HTML/CSS/JS | 웹 화면 템플릿과 정적 파일                     |
| 문서          | README, 요구사항 분석서, 기능명세서, PRD, ERD 등 |
| 설정 파일       | `.gitignore`, `requirements.txt`    |
| DB 문서       | Oracle DB 생성 SQL 문서                 |

---

## 4. GitHub에 업로드하지 않는 파일

다음 파일과 폴더는 GitHub에 업로드하지 않는다.

```text
data/
models/ml/
*.pkl
*.joblib
.env
```

### 제외 이유

| 대상             | 제외 이유                  |
| -------------- | ---------------------- |
| AI Hub 원본 JSON | 데이터 용량이 크고 라이선스 문제가 있음 |
| AI Hub 원천 이미지  | 용량이 크고 GitHub 저장소에 부적합 |
| 변환 CSV         | 스크립트로 재생성 가능           |
| 학습 모델 pkl      | 약 98MB로 크고 재생성 가능      |
| `.env`         | DB 비밀번호 등 민감 정보 포함 가능  |

---

## 5. 모델 파일 업로드 정책

현재 1차 ML 모델 파일은 다음 경로에 생성된다.

```text
models/ml/risk_regression_model.pkl
```

이 파일은 GitHub에 업로드하지 않는다.

### 이유

| 이유      | 설명                           |
| ------- | ---------------------------- |
| 용량 문제   | 모델 파일 크기가 약 98MB             |
| 저장소 비대화 | 모델을 다시 학습할 때마다 큰 바이너리 변경이 쌓임 |
| 재생성 가능  | 학습 스크립트로 다시 만들 수 있음          |
| 협업 안정성  | PC마다 로컬에서 생성하는 방식이 더 안전함     |

### 모델 재생성 명령어

다른 PC에서 모델 파일이 없으면 아래 명령을 실행한다.

```cmd
python scripts\convert_aihub_json_to_csv.py
python scripts\train_risk_model.py
```

생성 결과:

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
models/ml/risk_regression_model.pkl
```

---

## 6. 데이터 파일 업로드 정책

AI Hub 데이터는 GitHub에 업로드하지 않는다.

### 제외 대상

```text
data/aihub/aihub_json/
data/aihub/ml_dataset/
```

### 이유

* 원본 JSON 수가 많음
* 원천 이미지 용량이 큼
* AI Hub 데이터는 배포/공개에 제한이 있을 수 있음
* 변환 CSV는 스크립트로 재생성 가능함

---

## 7. `.gitignore` 관리 기준

`.gitignore`에는 다음 항목이 포함되어야 한다.

```gitignore
# Python
__pycache__/
*.pyc
.venv/
venv/

# IDE
.idea/
.vscode/

# Environment
.env

# Data
data/

# Models
models/ml/
*.pkl
*.joblib

# Logs
*.log
```

### 주의

`.idea/`, `.venv/`, `data/`, `models/ml/`은 커밋하지 않는다.

---

## 8. 작업 시작 전 루틴

집 PC 또는 학원 PC에서 작업을 시작하기 전에 반드시 아래 명령을 실행한다.

```cmd
git pull origin main
git status
```

### 정상 상태

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

### 이유

다른 PC에서 작업한 변경사항을 먼저 받아와야 충돌을 줄일 수 있다.

---

## 9. 작업 종료 루틴

작업을 마친 뒤에는 필요한 파일만 추가하고 커밋한다.

```cmd
git status
git add 수정한파일
git commit -m "커밋 메시지"
git pull --rebase origin main
git push origin main
git status
```

### 예시

```cmd
git status
git add docs\wildguard_github_cleanup.md
git commit -m "docs: update GitHub cleanup rules"
git pull --rebase origin main
git push origin main
git status
```

---

## 10. 파일 추가 시 주의사항

`git add .`는 가급적 사용하지 않는다.

### 이유

실수로 원본 데이터, 모델 파일, 임시 파일이 포함될 수 있기 때문이다.

### 권장 방식

수정한 파일만 직접 추가한다.

```cmd
git add README.md
git add docs\REQUIREMENTS_ANALYSIS.md
git add docs\FUNCTION_SPEC.md
git add docs\PRD.md
```

---

## 11. 현재 1차 ML 관련 커밋 기준

1차 ML 회귀 모델 관련 주요 커밋은 다음과 같은 형태로 관리한다.

| 커밋 메시지                                                | 내용                |
| ----------------------------------------------------- | ----------------- |
| `feat: add risk score generation`                     | 위험 점수 생성 로직 추가    |
| `feat: add risk score regression training`            | 회귀 모델 학습 코드 추가    |
| `feat: update risk prediction to regression API`      | API를 회귀 모델 구조로 수정 |
| `docs: update README for risk regression model`       | README 수정         |
| `docs: update requirements for risk regression model` | 요구사항 분석서 수정       |

---

## 12. 최신 코드 확인 방법

현재 PC에 최신 코드가 들어왔는지 확인하려면 아래 명령을 실행한다.

```cmd
git log --oneline -10
```

확인해야 하는 커밋 예시:

```text
feat: update risk prediction to regression API
feat: add risk score generation
feat: add risk score regression training
```

위 커밋이 보이면 회귀 모델 관련 코드가 해당 PC에 반영된 것이다.

---

## 13. 회귀 모델 코드 반영 확인

아래 명령으로 실제 파일 내용도 확인한다.

```cmd
findstr /N /I /C:"risk_regression_model.pkl" services\risk_prediction_service.py
findstr /N /I /C:"district" routes\risk_routes.py
findstr /N /I /C:"predicted_score" services\risk_prediction_service.py routes\risk_routes.py
```

### 정상 기준

| 확인 항목                       | 정상 상태                                     |
| --------------------------- | ----------------------------------------- |
| `risk_regression_model.pkl` | `services/risk_prediction_service.py`에 존재 |
| `district`                  | `routes/risk_routes.py`에 없어야 함            |
| `predicted_score`           | 서비스 또는 라우트에 존재                            |

`district`가 아직 나오면 이전 서울시 멧돼지 API 코드가 남아 있는 것이다.

---

## 14. 모델 파일 없음 문제 해결

### 증상

다른 PC에서 API 실행 시 다음 오류가 발생할 수 있다.

```text
모델 파일이 없습니다: models/ml/risk_regression_model.pkl
```

### 원인

모델 파일은 GitHub에 업로드하지 않기 때문이다.

### 해결

```cmd
python scripts\convert_aihub_json_to_csv.py
python scripts\train_risk_model.py
```

그 후 모델 파일을 확인한다.

```cmd
dir models\ml
```

확인해야 하는 파일:

```text
risk_regression_model.pkl
```

---

## 15. 실수로 제외 파일을 추가한 경우

### 데이터나 모델 파일이 staged 된 경우

```cmd
git status
```

만약 아래 파일이 staged 상태로 보이면 제거한다.

```text
data/
models/ml/risk_regression_model.pkl
```

### Git staging에서만 제거

```cmd
git restore --staged data
git restore --staged models\ml\risk_regression_model.pkl
```

파일 자체는 로컬에 남고, Git 커밋 대상에서만 빠진다.

---

## 16. 이미 커밋에 잘못 들어간 경우

아직 push 전이라면 마지막 커밋을 되돌릴 수 있다.

```cmd
git reset --soft HEAD~1
```

그 후 잘못 추가된 파일을 staging에서 제거한다.

```cmd
git restore --staged data
git restore --staged models\ml\risk_regression_model.pkl
```

다시 필요한 파일만 추가한다.

```cmd
git add 필요한파일
git commit -m "올바른 커밋 메시지"
```

---

## 17. Git LFS 사용 여부

현재 프로젝트에서는 Git LFS를 사용하지 않는다.

### 이유

| 항목        | 설명                      |
| --------- | ----------------------- |
| 모델 재생성 가능 | 학습 스크립트로 모델을 다시 만들 수 있음 |
| 프로젝트 단순화  | Git LFS 설정 없이 관리 가능     |
| 제출 안정성    | 코드와 문서 중심으로 저장소를 가볍게 유지 |
| 데이터 라이선스  | 원본 데이터는 어차피 업로드하지 않음    |

### 결론

모델 파일은 Git LFS로도 올리지 않고, 로컬에서 생성하는 방식으로 관리한다.

---

## 18. 집 PC와 학원 PC 작업 규칙

### 학원 PC에서 시작할 때

```cmd
cd /d E:\WildGuard_AI
git pull origin main
git status
```

### 집 PC에서 시작할 때

```cmd
cd /d E:\Projects\wildguard-ai
git pull origin main
git status
```

### 작업 후 공통

```cmd
git status
git add 수정한파일
git commit -m "커밋 메시지"
git pull --rebase origin main
git push origin main
git status
```

---

## 19. 충돌 방지 규칙

| 규칙             | 설명                             |
| -------------- | ------------------------------ |
| 작업 시작 전 pull   | 다른 PC 변경사항 먼저 받기               |
| 작업 종료 후 push   | 다음 PC에서 이어받을 수 있게 하기           |
| 같은 파일 동시 수정 금지 | 집/학원 PC에서 같은 파일을 따로 수정하지 않기    |
| 필요한 파일만 add    | `git add .` 남용 금지              |
| 문서 파일명 확인      | 실제 존재하는 파일명 기준으로 수정            |
| 모델/데이터 제외      | `data/`, `models/ml/`은 커밋하지 않기 |

---

## 20. 문서 파일명 기준

현재 문서 파일명은 다음 기준으로 관리한다.

| 문서           | 파일명                                         |
| ------------ | ------------------------------------------- |
| README       | `README.md`                                 |
| 요구사항 분석서     | `docs\REQUIREMENTS_ANALYSIS.md`             |
| 기능명세서        | `docs\FUNCTION_SPEC.md`                     |
| PRD          | `docs\PRD.md`                               |
| ERD          | `docs\ERD.md`                               |
| GitHub 정리    | `docs\wildguard_github_cleanup.md`          |
| Oracle DB 설정 | `docs\wildguard_oracle_db_setup.md`         |
| 오류 해결 기록     | `docs\wildguard_troubleshooting_updated.md` |
| 웹 서비스 명세서    | `docs\wildguard_web_service_spec.md`        |

파일명을 잘못 입력하면 새 파일이 생기거나 커밋 대상이 달라질 수 있으므로, 수정 전 `dir docs`로 확인한다.

```cmd
dir docs
```

---

## 21. 문서 커밋 순서

현재 1차 ML 회귀 모델 구조에 맞춰 다음 문서들을 정리한다.

| 순서 | 파일                                          | 상태 |
| -- | ------------------------------------------- | -- |
| 1  | `README.md`                                 | 완료 |
| 2  | `docs\REQUIREMENTS_ANALYSIS.md`             | 완료 |
| 3  | `docs\FUNCTION_SPEC.md`                     | 수정 |
| 4  | `docs\PRD.md`                               | 수정 |
| 5  | `docs\wildguard_web_service_spec.md`        | 수정 |
| 6  | `docs\ERD.md`                               | 수정 |
| 7  | `docs\wildguard_oracle_db_setup.md`         | 수정 |
| 8  | `docs\wildguard_troubleshooting_updated.md` | 수정 |
| 9  | `docs\wildguard_github_cleanup.md`          | 수정 |

---

## 22. 현재 기준 안정화된 작업 흐름

```text
GitHub에서 최신 코드 pull
↓
AI Hub JSON은 로컬에만 보관
↓
convert_aihub_json_to_csv.py 실행
↓
aihub_wildlife_metadata.csv 생성
↓
train_risk_model.py 실행
↓
risk_regression_model.pkl 생성
↓
Flask 서버 실행
↓
/api/risk/predict 테스트
↓
코드와 문서만 GitHub에 push
```

---

## 23. 결론

WildGuard AI 저장소는 코드와 문서 중심으로 관리한다.

AI Hub 원본 데이터, 변환 CSV, 학습 모델 파일은 GitHub에 올리지 않는다.

다른 PC에서 작업할 때는 항상 다음 순서를 지킨다.

```cmd
git pull origin main
git status
```

작업 후에는 다음 순서로 마무리한다.

```cmd
git add 수정한파일
git commit -m "커밋 메시지"
git pull --rebase origin main
git push origin main
```

이 규칙을 지키면 집 PC와 학원 PC를 오가며 작업해도 코드 누락과 충돌을 줄일 수 있다.
