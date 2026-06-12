# WildGuard AI 오류 해결 기록

## 1. 문서 개요

본 문서는 WildGuard AI 프로젝트를 진행하면서 발생한 주요 오류와 해결 방법을 정리한 문서이다.

현재 프로젝트는 AI Hub 야생동물 라벨링 JSON 메타데이터를 기반으로 위험 점수 `risk_score`를 예측하는 1차 ML 기능을 중심으로 개발 중이며, 이후 2차 Vision, 3차 LLM, 4차 SLM으로 확장할 예정이다.

---

## 2. 작업 환경

| 항목      | 내용                           |
| ------- | ---------------------------- |
| OS      | Windows                      |
| IDE     | PyCharm                      |
| 터미널     | CMD 기준                       |
| Python  | 가상환경 `.venv` 사용              |
| Backend | Flask                        |
| ML      | pandas, scikit-learn, joblib |
| Git     | GitHub 원격 저장소 사용             |
| 저장소     | `niabluelake/wildguard-ai`   |

---

## 3. 주요 로컬 경로

| 환경    | 경로                         |
| ----- | -------------------------- |
| 학원 PC | `E:\WildGuard_AI`          |
| 집 PC  | `E:\Projects\wildguard-ai` |

같은 GitHub 저장소를 사용하더라도 PC마다 로컬 프로젝트 경로가 다를 수 있으므로, 작업 시작 전 반드시 현재 경로와 Git 상태를 확인해야 한다.

```cmd
cd /d E:\WildGuard_AI
git status
git log --oneline -5
```

---

## 4. Git 작업 루틴

### 작업 시작 전

```cmd
git pull origin main
git status
```

### 작업 종료 시

```cmd
git status
git add 수정한파일
git commit -m "커밋 메시지"
git pull --rebase origin main
git push origin main
git status
```

### 이유

집 PC와 학원 PC를 오가며 작업하기 때문에, 작업 시작 전에 최신 코드를 가져오지 않으면 서로 다른 PC에서 파일 충돌이 발생할 수 있다.

---

## 5. 오류 1: AI Hub JSON 변환 결과가 0행으로 생성됨

### 증상

AI Hub JSON 변환 스크립트를 실행했을 때 CSV가 정상 생성되지 않고, 변환 결과가 비어 있었다.

예시 증상:

```text
CSV shape: (0, 0)
KeyError: 'risk_level'
```

또는 JSON 파일마다 다음과 같은 오류가 발생했다.

```text
name 'make_risk_score' is not defined
```

### 원인

`parse_json_file()` 함수 내부에서 `make_risk_score(row)`를 호출하고 있었지만, 실제 스크립트에 `make_risk_score()` 함수가 정의되어 있지 않았다.

즉, 위험 점수 생성 함수가 없는 상태에서 JSON 변환을 시도했기 때문에 모든 파일 변환이 실패했다.

### 해결 방법

`convert_aihub_json_to_csv.py`에 다음 기능을 추가했다.

* `get_species_score()`
* `make_risk_score()`
* `make_risk_grade()`

### 해결 후 결과

```text
JSON 파일 수: 30,700
CSV 데이터 크기: 30,700행 x 15컬럼
```

### 관련 파일

```text
scripts/convert_aihub_json_to_csv.py
```

---

## 6. 오류 2: 기존 risk_level 분류 구조와 risk_score 회귀 구조가 섞임

### 증상

초기에는 `risk_level`을 직접 생성하는 분류 모델 구조였으나, 이후 `risk_score`를 예측하는 회귀 모델 구조로 변경했다.

이 과정에서 일부 문서와 코드에 이전 구조가 남아 있었다.

예시:

```text
risk_model.pkl
RandomForestClassifier
risk_level
```

현재 구조에서는 다음 값들이 사용되어야 한다.

```text
risk_regression_model.pkl
RandomForestRegressor
risk_score
predicted_score
risk_grade
```

### 원인

프로젝트 방향을 중간에 분류 모델에서 회귀 모델로 변경했기 때문에 기존 파일명, 문서 내용, API 응답 구조가 일부 남아 있었다.

### 해결 방법

다음 기준으로 코드와 문서를 수정했다.

| 기존 구조                    | 변경 구조                       |
| ------------------------ | --------------------------- |
| `risk_level` 직접 예측       | `risk_score` 예측 후 등급 변환     |
| `RandomForestClassifier` | `RandomForestRegressor`     |
| `risk_model.pkl`         | `risk_regression_model.pkl` |
| `predicted_risk`         | `predicted_score`           |
| 분류 모델                    | 회귀 모델                       |

### 관련 파일

```text
scripts/train_risk_model.py
services/risk_prediction_service.py
routes/risk_routes.py
README.md
docs/REQUIREMENTS_ANALYSIS.md
docs/FUNCTION_SPEC.md
docs/PRD.md
```

---

## 7. 오류 3: API가 여전히 district/month를 요구함

### 증상

회귀 모델 API 테스트를 실행했을 때 다음과 같은 응답이 나왔다.

```json
{
  "success": false,
  "message": "필수 입력이 없습니다: ['district', 'month']"
}
```

### 원인

`routes/risk_routes.py`가 아직 이전 서울시 멧돼지 예측 API 구조를 사용하고 있었다.

기존 API는 다음 필드를 요구했다.

```text
district
month
```

하지만 현재 API는 AI Hub JSON 메타데이터 기반 회귀 모델이므로 다음 필드를 요구해야 한다.

```text
day
camera_type
weather
location
time_zone
season
species
object_count
max_bbox_area_ratio
avg_bbox_area_ratio
```

### 해결 방법

`routes/risk_routes.py`의 필수 입력값 검증 로직을 회귀 모델 입력 구조에 맞게 수정했다.

### 수정 후 API 테스트

```cmd
curl -X POST http://127.0.0.1:5000/api/risk/predict -H "Content-Type: application/json" -d "{\"day\":\"night\",\"camera_type\":\"IR\",\"weather\":\"cloudy\",\"location\":\"산림\",\"time_zone\":\"night\",\"season\":\"fall\",\"species\":\"멧돼지\",\"object_count\":2,\"max_bbox_area_ratio\":0.03,\"avg_bbox_area_ratio\":0.02}"
```

### 정상 응답

```json
{
  "success": true,
  "result": {
    "predicted_score": 68.77,
    "risk_grade": "medium",
    "model_type": "regression"
  }
}
```

### 관련 파일

```text
routes/risk_routes.py
services/risk_prediction_service.py
```

---

## 8. 오류 4: 모델 파일이 GitHub에 없어서 API 실행 불가

### 증상

학원 PC 또는 다른 PC에서 API를 실행할 때 모델 파일을 찾지 못할 수 있다.

예상 오류:

```text
모델 파일이 없습니다: models/ml/risk_regression_model.pkl
```

### 원인

`risk_regression_model.pkl`은 약 98MB 크기의 학습 모델 파일이며, GitHub에는 업로드하지 않도록 설정했다.

따라서 새로운 PC에서 GitHub 코드를 가져온 뒤에는 모델 파일이 없을 수 있다.

### 해결 방법

해당 PC에서 CSV 변환과 모델 학습을 다시 실행한다.

```cmd
python scripts\convert_aihub_json_to_csv.py
python scripts\train_risk_model.py
```

### 생성되는 파일

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
models/ml/risk_regression_model.pkl
```

### 관련 파일

```text
scripts/convert_aihub_json_to_csv.py
scripts/train_risk_model.py
models/ml/risk_regression_model.pkl
```

---

## 9. 오류 5: GitHub에 모델 파일이 추가되지 않음

### 증상

다음 명령을 실행했는데 모델 파일이 Git에 추가되지 않았다.

```cmd
git add models\ml\risk_regression_model.pkl
```

### 원인

`.gitignore`에서 모델 폴더와 pkl 파일이 제외되어 있었기 때문이다.

예상 제외 항목:

```text
models/ml/
*.pkl
*.joblib
```

### 해결 판단

모델 파일은 약 98MB로 크고, 학습 스크립트로 재생성 가능하므로 GitHub에 올리지 않는 것이 좋다.

### 최종 결정

모델 파일은 GitHub에 업로드하지 않는다.

```text
models/ml/risk_regression_model.pkl
```

대신 각 PC에서 아래 명령으로 재생성한다.

```cmd
python scripts\convert_aihub_json_to_csv.py
python scripts\train_risk_model.py
```

---

## 10. 오류 6: 집 PC와 학원 PC 경로 혼동

### 증상

학원 PC에서 `git pull`을 했는데도 집에서 수정한 코드가 안 온 것처럼 보였다.

### 원인

집 PC와 학원 PC의 로컬 경로가 달랐다.

| PC    | 경로                         |
| ----- | -------------------------- |
| 집 PC  | `E:\Projects\wildguard-ai` |
| 학원 PC | `E:\WildGuard_AI`          |

또한 집 PC에서 수정한 내용을 커밋/푸시하지 않았다면 학원 PC에서 `git pull`을 해도 변경 사항을 받을 수 없다.

### 확인 명령어

```cmd
git log --oneline -10
```

### 확인해야 하는 커밋 예시

```text
feat: update risk prediction to regression API
feat: add risk score generation
feat: add risk score regression training
```

### 해결 방법

1. 작업 시작 전 `git pull origin main`
2. 작업 후 반드시 `git commit`
3. `git pull --rebase origin main`
4. `git push origin main`
5. 다른 PC에서 다시 `git pull origin main`

---

## 11. 오류 7: 문서 파일명 혼동

### 증상

문서 수정 시 잘못된 파일명을 기준으로 안내했다.

잘못된 파일명:

```text
docs/WEB_SERVICE_SPEC.md
```

실제 파일명:

```text
docs/wildguard_web_service_spec.md
```

### 원인

문서 파일명이 대문자 형식이 아니라 `wildguard_` 접두어가 붙은 파일명으로 관리되고 있었다.

### 해결 방법

실제 존재하는 파일명을 기준으로 수정하고 커밋한다.

```cmd
git add docs\wildguard_web_service_spec.md
git commit -m "docs: update web service spec for risk regression model"
```

잘못 생성된 파일이 있다면 삭제한다.

```cmd
del docs\WEB_SERVICE_SPEC.md
```

### 파일명 확인 명령어

```cmd
dir docs
```

또는 특정 문자열 검색:

```cmd
findstr /S /N /I /C:"WEB_SERVICE_SPEC.md" docs\*.md README.md
```

---

## 12. 오류 8: 문서와 실제 코드 상태가 다름

### 증상

README, 요구사항 분석서, 기능명세서, PRD 등에 이전 구조가 남아 있었다.

예시:

```text
서울시 멧돼지 자치구/월별 예측
district
month
risk_model.pkl
RandomForestClassifier
```

### 원인

프로젝트 초기에 사용하던 서울시 멧돼지 위험도 예측 구조가 남아 있었다.

현재 프로젝트는 AI Hub 야생동물 JSON 메타데이터 기반 위험 점수 회귀 모델로 변경되었다.

### 해결 방법

다음 문서를 현재 구조에 맞게 수정했다.

| 문서                                   | 수정 내용                         |
| ------------------------------------ | ----------------------------- |
| `README.md`                          | 프로젝트 개요와 실행 방법을 회귀 모델 기준으로 수정 |
| `docs/REQUIREMENTS_ANALYSIS.md`      | 요구사항을 `risk_score` 중심으로 수정    |
| `docs/FUNCTION_SPEC.md`              | 기능 목록과 API 명세 수정              |
| `docs/PRD.md`                        | 제품 요구사항을 현재 구조에 맞게 수정         |
| `docs/ERD.md`                        | 위험 점수 예측 로그 저장 구조 반영          |
| `docs/wildguard_oracle_db_setup.md`  | Oracle 테이블 생성 SQL 수정          |
| `docs/wildguard_web_service_spec.md` | 웹/API 응답 구조 수정                |

---

## 13. 오류 9: API 테스트는 성공했지만 웹 화면은 아직 이전 UI일 수 있음

### 증상

`curl` 테스트에서는 정상적으로 `predicted_score`가 반환되지만, 웹 화면에서는 점수 표시가 제대로 안 될 수 있다.

### 원인

API는 회귀 모델 구조로 수정되었지만, `templates/risk.html`은 아직 기존 위험 등급 중심 UI일 수 있다.

### 해결 방법

`templates/risk.html`에서 다음 항목을 표시하도록 수정해야 한다.

| 표시 항목    | API 필드                   |
| -------- | ------------------------ |
| 예측 위험 점수 | `result.predicted_score` |
| 위험 등급    | `result.risk_grade`      |
| 대응 메시지   | `result.message`         |
| 모델 유형    | `result.model_type`      |
| MAE      | `result.metrics.mae`     |
| RMSE     | `result.metrics.rmse`    |
| R2 Score | `result.metrics.r2`      |

### 관련 파일

```text
templates/risk.html
routes/risk_page_routes.py
routes/risk_routes.py
services/risk_prediction_service.py
```

---

## 14. 오류 10: 한글 출력이 깨져 보임

### 증상

CMD 또는 파일 출력에서 한글이 깨져 보일 수 있다.

예시:

```text
?붿껌
?꾩닔
```

### 원인

터미널 코드 페이지 또는 파일 인코딩 문제로 인해 한글이 깨져 보일 수 있다.

### 해결 방법

CMD에서 UTF-8 코드 페이지로 변경한 뒤 확인한다.

```cmd
chcp 65001
```

그 후 파일을 다시 확인한다.

```cmd
type routes\risk_routes.py
```

### 주의

터미널 출력이 깨져 보여도 Python 파일 자체가 UTF-8로 저장되어 있으면 Flask 실행에는 문제가 없을 수 있다.

---

## 15. 정상 동작 확인 명령어

### Git 상태 확인

```cmd
git status
git log --oneline -5
```

### 회귀 모델 코드 반영 확인

```cmd
findstr /N /I /C:"risk_regression_model.pkl" services\risk_prediction_service.py
findstr /N /I /C:"district" routes\risk_routes.py
findstr /N /I /C:"predicted_score" services\risk_prediction_service.py routes\risk_routes.py
```

정상 기준:

```text
services/risk_prediction_service.py 안에 risk_regression_model.pkl 있음
routes/risk_routes.py 안에 district 없음
predicted_score 있음
```

### 모델 파일 존재 확인

```cmd
dir models\ml
```

확인해야 하는 파일:

```text
risk_regression_model.pkl
```

### Flask 서버 실행

```cmd
python app.py
```

### Medium 위험도 API 테스트

```cmd
curl -X POST http://127.0.0.1:5000/api/risk/predict -H "Content-Type: application/json" -d "{\"day\":\"night\",\"camera_type\":\"IR\",\"weather\":\"cloudy\",\"location\":\"산림\",\"time_zone\":\"night\",\"season\":\"fall\",\"species\":\"멧돼지\",\"object_count\":2,\"max_bbox_area_ratio\":0.03,\"avg_bbox_area_ratio\":0.02}"
```

예상 결과:

```json
{
  "predicted_score": 68.77,
  "risk_grade": "medium",
  "model_type": "regression"
}
```

### High 위험도 API 테스트

```cmd
curl -X POST http://127.0.0.1:5000/api/risk/predict -H "Content-Type: application/json" -d "{\"day\":\"night\",\"camera_type\":\"IR\",\"weather\":\"rain\",\"location\":\"산림\",\"time_zone\":\"night\",\"season\":\"fall\",\"species\":\"멧돼지\",\"object_count\":4,\"max_bbox_area_ratio\":0.08,\"avg_bbox_area_ratio\":0.05}"
```

예상 결과:

```json
{
  "predicted_score": 84.37,
  "risk_grade": "high",
  "model_type": "regression"
}
```

---

## 16. 현재 안정화된 1차 ML 흐름

```text
AI Hub JSON
↓
scripts/convert_aihub_json_to_csv.py
↓
aihub_wildlife_metadata.csv
↓
risk_score 생성
↓
scripts/train_risk_model.py
↓
risk_regression_model.pkl
↓
services/risk_prediction_service.py
↓
routes/risk_routes.py
↓
POST /api/risk/predict
↓
predicted_score, risk_grade, message 반환
```

---

## 17. 향후 남은 수정 사항

| 항목                                            | 상태 |
| --------------------------------------------- | -- |
| `templates/risk.html` 위험 점수 중심 UI 수정          | 예정 |
| 로그인 사용자 예측 결과 DB 저장                           | 예정 |
| `services/risk_log_service.py` 회귀 결과 저장 구조 반영 | 예정 |
| `templates/risk_history.html` 위험 점수 기록 표시     | 예정 |
| YOLO 라벨 변환 및 탐지 API                           | 예정 |
| LLM 상담 기능                                     | 예정 |
| SLM 경량 상담 기능                                  | 예정 |

---

## 18. 결론

현재 1차 ML 기능은 다음 항목까지 정상 동작을 확인했다.

| 작업              | 상태 |
| --------------- | -- |
| AI Hub JSON 변환  | 완료 |
| 위험 점수 생성        | 완료 |
| 회귀 모델 학습        | 완료 |
| 위험 점수 예측 API 연결 | 완료 |
| Medium API 테스트  | 완료 |
| High API 테스트    | 완료 |
| 모델 파일 GitHub 제외 | 완료 |
| 주요 문서 수정        | 진행 |

가장 중요한 주의사항은 다음과 같다.

```text
모델 파일과 원본 데이터는 GitHub에 올리지 않는다.
다른 PC에서는 변환 스크립트와 학습 스크립트를 다시 실행해 모델을 생성한다.
작업 시작 전에는 항상 git pull origin main을 실행한다.
```
