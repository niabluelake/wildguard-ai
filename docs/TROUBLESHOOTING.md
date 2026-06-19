# WildGuard AI 트러블슈팅 문서

## 1. 문서 목적

본 문서는 WildGuard AI 프로젝트를 진행하면서 발생한 주요 문제와 해결 과정을 정리한 문서이다.

단순 오류 기록이 아니라, 문제 원인 분석, 해결 방법, 사용한 기술, 결과를 함께 정리하여 프로젝트 구현 과정에서의 문제 해결 능력을 보여주는 것을 목적으로 한다.

---

## 2. 트러블슈팅 요약

| No | 문제                                                        | 원인                                     | 해결 방법                                                 | 결과                       |
| -: | --------------------------------------------------------- | -------------------------------------- | ----------------------------------------------------- | ------------------------ |
|  1 | 기존 ML 서비스가 단순 점수 예측처럼 보임                                  | AI Hub 메타데이터만 사용하여 위험도 근거가 약함          | 한국도로공사 로드킬 데이터를 외부 feature로 결합                        | 위험도 평가 근거 강화             |
|  2 | AI Hub ML CSV에 GPS 컬럼이 없음                                 | 기존 변환 스크립트가 GPS를 저장하지 않음               | 원본 JSON을 다시 읽어 latitude, longitude 추가                 | 로드킬 거리 feature 생성 가능     |
|  3 | 로드킬 데이터와 AI Hub 데이터를 직접 결합할 키가 없음                         | 두 데이터셋에 공통 ID가 없음                      | 위도·경도 기반 Haversine 거리 계산 사용                           | 거리 기반 hotspot feature 생성 |
|  4 | 학습 스크립트 실행 시 필수 컬럼 누락 오류 발생                               | 모델 feature 목록은 새 버전인데 CSV 경로는 기존 파일 사용 | DATA_PATH를 enriched CSV로 수정                           | 회귀 모델 재학습 성공             |
|  5 | API 호출 시 `'dict' object has no attribute 'predict'` 오류 발생 | 모델 pkl이 모델 객체가 아니라 dict 형태로 저장됨        | `loaded["model"]`에서 실제 모델 객체를 꺼내도록 수정                 | API 예측 성공                |
|  6 | 웹 화면 입력값과 새 모델 필수 입력값이 맞지 않음                              | 모델은 상세 feature를 요구하지만 화면 입력값은 단순함      | JavaScript에서 기본 관측 시나리오 값을 함께 전송                      | 웹 화면 예측 정상 동작            |
|  7 | 데이터/모델 Git 업로드 여부 결정 필요                                   | CSV, pkl 파일은 용량 및 라이선스 문제가 있음          | `.gitignore`로 data, models/ml 제외                      | GitHub 저장소 경량화           |
|  8 | 집/학원 PC 작업 충돌 가능성                                         | 여러 PC에서 같은 저장소 작업                      | `git pull → 작업 → commit → pull --rebase → push` 루틴 적용 | 충돌 최소화                   |

---

## 3. 상세 트러블슈팅

## 3.1 기존 머신러닝 서비스가 단순 점수 예측처럼 보이는 문제

### 문제 상황

초기 1차 ML 서비스는 AI Hub 야생동물 라벨링 JSON에서 추출한 메타데이터만 사용하여 위험 점수를 예측했다.

사용 feature는 다음과 같았다.

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

이 구조는 기본적인 관측 조건을 반영할 수는 있었지만, 사용자가 보기에 단순한 규칙 기반 점수 예측처럼 보일 수 있었다.

### 원인

AI Hub 관측 데이터만 사용하면 현재 관측 조건은 반영할 수 있지만, 해당 지역 주변의 과거 야생동물 사고 이력이나 외부 위험 요인을 반영하기 어렵다.

### 해결 방법

한국도로공사 로드킬 다발 구간 데이터를 외부 feature로 추가하였다.

활용한 데이터는 다음과 같다.

```text
data/external/roadkill/roadkill_2019_2025_combined.csv
```

로드킬 데이터의 위도, 경도, 발생건수를 활용하여 AI Hub 관측 지점과의 거리 기반 feature를 생성했다.

생성한 feature는 다음과 같다.

```text
nearest_roadkill_distance_km
roadkill_count_within_5km
roadkill_count_within_10km
roadkill_count_within_20km
roadkill_max_cases_nearby
roadkill_weighted_score
near_roadkill_hotspot
```

### 사용한 기술

* Pandas
* NumPy
* Haversine Distance
* CSV 데이터 통합
* Feature Engineering

### 결과

기존 관측 메타데이터 기반 위험 점수에 로드킬 다발 구간 정보를 결합하여, 위험도 산정 근거를 강화할 수 있었다.

---

## 3.2 AI Hub ML CSV에 GPS 컬럼이 없는 문제

### 문제 상황

로드킬 feature를 생성하려면 AI Hub 관측 지점과 로드킬 다발 구간 사이의 거리를 계산해야 했다.

그러나 기존 ML CSV에는 `latitude`, `longitude` 컬럼이 없었다.

기존 컬럼은 다음과 같았다.

```text
json_file
file_name
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
risk_score
risk_grade
risk_level
```

### 원인

초기 JSON 변환 과정에서는 GPS 값을 학습 feature로 사용하지 않았기 때문에 CSV에 저장하지 않았다.

### 해결 방법

기존 CSV의 `json_file` 경로를 기준으로 원본 JSON을 다시 읽고, JSON 내부의 GPS 정보를 추출하여 `latitude`, `longitude` 컬럼을 추가하는 스크립트를 작성했다.

관련 스크립트:

```text
scripts/add_gps_to_ml_dataset.py
```

생성 파일:

```text
data/aihub/ml_dataset/aihub_wildlife_metadata_with_gps.csv
```

### 사용한 기술

* Python `json`
* Pandas
* Pathlib
* 예외 처리

### 결과

기존 15컬럼 데이터셋에 GPS 컬럼 2개를 추가하여 17컬럼 데이터셋을 생성했다.

```text
aihub_wildlife_metadata.csv
→ aihub_wildlife_metadata_with_gps.csv
```

---

## 3.3 AI Hub 데이터와 로드킬 데이터를 직접 결합할 키가 없는 문제

### 문제 상황

AI Hub 야생동물 관측 데이터와 한국도로공사 로드킬 데이터는 서로 다른 출처의 데이터이기 때문에 공통 ID가 없었다.

즉, 일반적인 방식의 merge가 불가능했다.

### 원인

AI Hub 데이터는 관측 이미지와 라벨링 JSON 중심이고, 로드킬 데이터는 고속도로 구간별 다발 지점 중심 데이터이다.

두 데이터는 다음과 같이 구조가 다르다.

| 데이터             | 주요 기준                 |
| --------------- | --------------------- |
| AI Hub 야생동물 데이터 | 이미지 파일, 관측 위치, GPS    |
| 로드킬 데이터         | 노선명, 구간, 위도, 경도, 발생건수 |

### 해결 방법

공통 ID 대신 위도·경도를 기준으로 거리 계산을 수행했다.

Haversine Distance를 사용하여 관측 지점과 모든 로드킬 지점 사이의 거리를 계산하고, 반경별 발생건수를 집계했다.

관련 스크립트:

```text
scripts/enrich_ml_dataset_with_roadkill.py
```

생성 파일:

```text
data/aihub/ml_dataset/aihub_wildlife_metadata_enriched.csv
```

### 사용한 기술

* Haversine Distance
* NumPy 벡터 연산
* Pandas DataFrame 결합
* 거리 기반 feature engineering

### 결과

최종 학습 데이터셋에 로드킬 외부 feature를 추가했다.

```text
기존 GPS 포함 CSV: 30,700행 × 17컬럼
로드킬 결합 CSV: 30,700행 × 25컬럼
```

---

## 3.4 학습 스크립트에서 필수 컬럼 누락 오류 발생

### 오류 메시지

```text
ValueError: 필수 컬럼이 없습니다:
['nearest_roadkill_distance_km',
 'roadkill_count_within_5km',
 'roadkill_count_within_10km',
 'roadkill_count_within_20km',
 'roadkill_max_cases_nearby',
 'roadkill_weighted_score',
 'near_roadkill_hotspot']
```

### 문제 상황

로드킬 feature를 추가한 뒤 `train_risk_model.py`를 실행했지만, 학습 스크립트에서 필수 컬럼이 없다는 오류가 발생했다.

### 원인

`numeric_features` 목록은 로드킬 feature를 포함하도록 수정했지만, 실제 `DATA_PATH`는 여전히 기존 CSV를 바라보고 있었다.

문제가 된 경로:

```python
DATA_PATH = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_wildlife_metadata.csv"
```

이 파일에는 로드킬 feature가 없었다.

### 해결 방법

학습 데이터 경로를 최종 enriched CSV로 수정했다.

```python
DATA_PATH = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_wildlife_metadata_enriched.csv"
```

### 결과

로드킬 feature가 포함된 최종 CSV를 사용하여 회귀 모델 재학습에 성공했다.

학습 결과:

```text
MAE: 0.0276
RMSE: 0.2472
R2 Score: 0.9991
```

---

## 3.5 API 호출 시 dict object has no attribute predict 오류 발생

### 오류 메시지

```text
'dict' object has no attribute 'predict'
```

### 문제 상황

`/api/risk/predict` API를 호출했을 때 서버 오류가 발생했다.

### 원인

`risk_regression_model.pkl` 파일은 모델 객체만 저장한 것이 아니라, 모델과 메타데이터를 함께 담은 dictionary 형태로 저장되어 있었다.

실제 구조 확인 결과:

```text
dict_keys([
  'model',
  'model_type',
  'target_col',
  'feature_cols',
  'categorical_features',
  'numeric_features',
  'metrics',
  'grade_rule'
])
```

기존 서비스 코드는 pkl 전체를 모델 객체로 보고 `.predict()`를 호출했기 때문에 오류가 발생했다.

### 해결 방법

`joblib.load()`로 불러온 객체가 dict인 경우, `loaded["model"]`에서 실제 모델 객체를 꺼내도록 수정했다.

관련 파일:

```text
services/risk_prediction_service.py
```

수정 코드:

```python
loaded = joblib.load(MODEL_PATH)

if isinstance(loaded, dict):
    _model = loaded["model"]
else:
    _model = loaded
```

### 결과

API 호출이 정상 동작했다.

응답 예시:

```json
{
  "success": true,
  "result": {
    "predicted_score": 86.98,
    "predicted_grade": "high",
    "predicted_grade_ko": "높음"
  }
}
```

---

## 3.6 웹 화면 입력값과 새 모델 필수 입력값이 맞지 않는 문제

### 문제 상황

새로운 위험도 회귀 모델은 다음 필수 입력값을 요구한다.

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

그러나 웹 화면에서는 사용자 편의를 위해 아래 값만 입력받고 있었다.

```text
region_name
location
weather
time_zone
season
```

### 원인

모델은 상세 관측 feature를 필요로 하지만, 웹 화면에서 모든 feature를 직접 입력받으면 사용성이 떨어질 수 있다.

### 해결 방법

웹 화면에서는 사용자가 이해하기 쉬운 조건만 입력받고, JavaScript에서 기본 관측 시나리오 값을 함께 전송하도록 수정했다.

관련 파일:

```text
templates/risk.html
```

보정 입력값:

```javascript
day: timeZone === "day" ? "day" : "night",
camera_type: timeZone === "day" ? "RGB" : "IR",
species: "멧돼지",
object_count: 4,
max_bbox_area_ratio: 0.08,
avg_bbox_area_ratio: 0.05
```

### 결과

웹 화면에서 버튼 클릭만으로 위험도 예측 API가 정상 호출되었다.

---

## 3.7 데이터와 모델 파일을 GitHub에 올릴지에 대한 문제

### 문제 상황

AI Hub 원본 데이터, 변환 CSV, 학습된 pkl 모델 파일을 GitHub에 올릴지 결정해야 했다.

### 원인

데이터와 모델 파일은 다음과 같은 문제가 있다.

* 파일 용량이 큼
* 원본 데이터 라이선스 문제가 있을 수 있음
* 모델 파일은 재생성 가능함
* GitHub 저장소가 무거워질 수 있음

### 해결 방법

데이터와 모델 파일은 GitHub에 업로드하지 않고, 전처리 및 학습 스크립트만 관리하도록 결정했다.

`.gitignore` 관리 대상:

```text
data/
models/ml/
*.csv
*.pkl
.venv/
.idea/
__pycache__/
```

### 결과

GitHub에는 코드, 문서, 템플릿만 업로드하고, 데이터와 모델은 로컬에서 재생성하는 구조로 정리했다.

---

## 3.8 여러 PC에서 작업할 때 Git 충돌 가능성

### 문제 상황

집 PC와 학원 PC를 오가며 같은 프로젝트를 작업하면서 충돌 가능성이 있었다.

### 원인

두 PC에서 같은 파일을 수정한 뒤 pull/push 순서가 꼬이면 충돌이 발생할 수 있다.

### 해결 방법

작업 시작과 종료 루틴을 정했다.

작업 시작 전:

```cmd
git pull origin main
git status
```

작업 종료 시:

```cmd
git status
git add <수정한 파일>
git commit -m "커밋 메시지"
git pull --rebase origin main
git push origin main
```

### 결과

집 PC와 학원 PC 간 작업 내용을 안정적으로 동기화할 수 있었다.

---

## 4. 최종 확인 테스트

### 4.1 데이터 생성 테스트

```cmd
python scripts\add_gps_to_ml_dataset.py
python scripts\enrich_ml_dataset_with_roadkill.py
```

확인 파일:

```text
data/aihub/ml_dataset/aihub_wildlife_metadata_with_gps.csv
data/aihub/ml_dataset/aihub_wildlife_metadata_enriched.csv
```

### 4.2 모델 학습 테스트

```cmd
python scripts\train_risk_model.py
```

확인 결과:

```text
MAE: 0.0276
RMSE: 0.2472
R2 Score: 0.9991
```

### 4.3 API 테스트

```cmd
curl -X POST http://127.0.0.1:5000/api/risk/predict ^
-H "Content-Type: application/json" ^
-d "{\"day\":\"night\",\"camera_type\":\"IR\",\"weather\":\"rain\",\"location\":\"산림\",\"time_zone\":\"night\",\"season\":\"fall\",\"species\":\"멧돼지\",\"object_count\":4,\"max_bbox_area_ratio\":0.08,\"avg_bbox_area_ratio\":0.05}"
```

확인 항목:

```text
success: true
predicted_score 반환
predicted_grade 반환
risk_reasons 반환
action_message 반환
roadkill_features 반환
```

### 4.4 웹 화면 테스트

```cmd
python app.py
```

접속 URL:

```text
http://127.0.0.1:5000/risk
```

확인 항목:

```text
위험 점수 표시
위험 등급 표시
주요 위험 요인 표시
현장 대응 가이드 표시
로드킬 다발 구간 기반 외부 feature 표시
```

---

## 5. 정리

본 프로젝트의 주요 트러블슈팅은 단순 오류 수정이 아니라, 서비스 완성도를 높이기 위한 구조 개선 과정이었다.

초기에는 AI Hub 관측 메타데이터 기반의 단순 위험 점수 예측 구조였지만, GPS 추출과 로드킬 다발 구간 데이터 결합을 통해 위험도 평가 근거를 강화했다.

또한 새 모델 구조에 맞춰 학습 스크립트, Flask API, 웹 화면 입력 방식을 수정하여 사용자가 웹 화면에서 위험도 예측 결과를 안정적으로 확인할 수 있도록 개선했다.
