# WildGuard AI

AI Hub 야생동물 라벨링 데이터를 활용하여 야생동물 출현 위험도를 예측하고, 이미지 탐지와 대응 상담을 제공하는 AI 서비스입니다.

## 프로젝트 개요

WildGuard AI는 하나의 야생동물 데이터셋을 기반으로 1차부터 4차까지 확장하는 AI 서비스 프로젝트입니다.

| 단계 | 내용 |
|---|---|
| 1차 ML | AI Hub 라벨링 JSON 메타데이터를 정형 데이터로 변환하여 야생동물 출현 위험도 예측 |
| 2차 Vision | 원천 이미지와 bbox 라벨을 활용한 YOLO 기반 사족보행 야생동물 탐지 |
| 3차 LLM | 위험도 예측 결과와 탐지 결과 기반 야생동물 대응 상담 |
| 4차 SLM | 현장용 경량 야생동물 대응 상담 모델 |

## 현재 진행 상황

| 작업 | 상태 |
|---|---|
| GitHub 저장소 생성 | 완료 |
| Flask 기본 구조 구성 | 완료 |
| AI Hub JSON 데이터 배치 | 완료 |
| JSON 메타데이터 CSV 변환 | 완료 |
| 위험도 라벨 생성 | 완료 |
| 위험도 분포 조정 | 완료 |
| RandomForest 위험도 예측 모델 학습 | 완료 |
| Flask 위험도 예측 API 연결 | 진행 |
| 위험도 예측 웹 화면 | 진행 |
| YOLO 라벨 변환 | 예정 |
| LLM 상담 기능 | 예정 |
| Oracle DB 연동 | 예정 |

## 1차 ML 프로젝트

### 목표

AI Hub 야생동물 라벨링 JSON에서 이미지 메타데이터와 annotation 정보를 추출하여 정형 데이터셋을 만들고, 야생동물 출현 상황의 위험도를 예측합니다.

### 사용 데이터

원본 데이터는 GitHub에 업로드하지 않습니다.

```text
data/aihub_json/TL-quadruped/

데이터 변환 결과

현재 AI Hub JSON 30,700개를 변환했습니다.

항목	결과
JSON 파일 수	30,700
CSV 행 수	30,700
CSV 컬럼 수	22

주요 종 분포:

species	count
멧돼지	30,613
고라니	64
반달가슴곰	21
멧토끼	2

위험도 분포:

risk_level	count
medium	18,694
high	10,196
low	1,810
주요 Feature
구분	컬럼
범주형	day, camera_type, weather, location, time_zone, season
수치형	object_count, max_bbox_area_ratio, avg_bbox_area_ratio
Target	risk_level
위험도 라벨 생성 기준

원본 JSON에는 서비스용 위험도 라벨이 없으므로, 프로젝트 목적에 맞게 규칙 기반으로 risk_level을 생성했습니다.

조건	점수
object_count >= 3	+2
object_count == 2	+1
max_bbox_area_ratio >= 0.05	+2
max_bbox_area_ratio >= 0.02	+1
time_zone이 night 또는 dawn	+1
day가 night	+1
점수	risk_level
0~1	low
2~3	medium
4 이상	high
모델 학습 결과

RandomForestClassifier를 사용하여 위험도 분류 모델을 학습했습니다.

Accuracy: 0.9996

Classification Report:

              precision    recall  f1-score   support

        high       1.00      1.00      1.00      2039
         low       1.00      0.99      1.00       362
      medium       1.00      1.00      1.00      3739

    accuracy                           1.00      6140
   macro avg       1.00      1.00      1.00      6140
weighted avg       1.00      1.00      1.00      6140

단, 현재 risk_level은 규칙 기반으로 생성된 라벨이므로 모델 성능은 실제 현장 정답에 대한 성능이 아니라, 생성된 위험도 규칙을 얼마나 잘 학습했는지를 의미합니다.

프로젝트 구조
WildGuard_AI/
│
├── app.py
├── README.md
├── requirements.txt
│
├── docs/
│   ├── REQUIREMENTS_ANALYSIS.md
│   ├── FUNCTION_SPEC.md
│   └── PRD.md
│
├── routes/
│   ├── main_routes.py
│   ├── risk_routes.py
│   └── risk_page_routes.py
│
├── services/
│   └── risk_prediction_service.py
│
├── scripts/
│   ├── convert_aihub_metadata.py
│   └── train_risk_model.py
│
├── templates/
│   ├── index.html
│   └── risk.html
│
├── static/
│
├── data/
│   ├── aihub_json/
│   └── aihub/
│       └── ml_dataset/
│
└── models/
    └── ml/
실행 방법
1. 가상환경 활성화

CMD 기준:

cd /d E:\WildGuard_AI
.venv\Scripts\activate
2. 패키지 설치
pip install -r requirements.txt
3. AI Hub JSON 메타데이터 변환
python scripts\convert_aihub_metadata.py
4. 위험도 예측 모델 학습
python scripts\train_risk_model.py
5. Flask 서버 실행
python app.py

브라우저 접속:

http://127.0.0.1:5000/

위험도 예측 화면:

http://127.0.0.1:5000/risk
API
위험도 예측 API
POST /api/risk/predict

Request 예시:

{
  "day": "night",
  "camera_type": "IR",
  "weather": "cloudy",
  "location": "대산농원",
  "time_zone": "night",
  "season": "fall",
  "object_count": 2,
  "max_bbox_area_ratio": 0.0235,
  "avg_bbox_area_ratio": 0.0206
}

Response 예시:

{
  "success": true,
  "result": {
    "risk_level": "medium",
    "message": "야생동물 출현 가능성이 있어 주의가 필요합니다. 직접 접근하지 말고 주변을 확인하세요."
  }
}
GitHub 업로드 제외 대상

AI Hub 원본 데이터와 학습 결과물은 GitHub에 업로드하지 않습니다.

.gitignore 예시:

.venv/
__pycache__/
*.pyc
.env

data/aihub_json/
data/aihub/ml_dataset/

*.pkl
*.joblib
models/ml/
문서
문서	설명
docs/REQUIREMENTS_ANALYSIS.md	요구사항 분석서
docs/FUNCTION_SPEC.md	기능명세서
docs/PRD.md	제품 요구사항 문서