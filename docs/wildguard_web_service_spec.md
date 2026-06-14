# WildGuard AI 웹 서비스 명세서

## 1. 서비스 URL

| URL | Method | 설명 |
| --- | --- | --- |
| `/` | GET | 메인 화면 |
| `/risk` | GET | 위험도 예측 화면 |
| `/api/risk/predict` | POST | 위험도 예측 API |
| `/vision` | GET | 이미지/영상 탐지 화면 |
| `/api/vision/predict` | POST | 이미지/영상 탐지 API |
| `/chat` | GET | 대응 상담 챗봇 화면 |
| `/api/chat/message` | POST | 대응 상담 API |
| `/auth/register` | GET/POST | 회원가입 |
| `/auth/login` | GET/POST | 로그인 |
| `/auth/logout` | GET | 로그아웃 |
| `/risk/history` | GET | 예측 기록 조회 |

---

## 2. 화면 명세

### 2.1 메인 화면

- 서비스 소개
- 위험도 예측, 이미지/영상 탐지, 대응 상담 챗봇으로 이동
- 로그인 상태에 따라 예측 기록 또는 회원가입 버튼 표시

### 2.2 위험도 예측 화면

입력값:

| 필드 | 설명 |
| --- | --- |
| 지역 이름 | 사용자가 알아보기 쉬운 별칭 |
| 위험도를 확인할 지역 | AI Hub 관측 지역 |
| 날씨 | sunny, cloudy, rain, snow |
| 시간대 | dawn, day, evening, night |
| 계절 | spring, summer, fall, winter |

출력값:

- 위험 점수
- 위험 등급
- 주요 위험 동물
- 과거 유사 관측 수
- 권장 행동 요령
- 모델 성능 지표

### 2.3 대응 상담 화면

입력값:

- 상담 모드
- 지역 조건
- 사용자 질문

상담 모드:

| 모드 | 설명 |
| --- | --- |
| 상세 상담 모드 | 위험도 해석과 행동 요령을 자세히 설명 |
| 현장 대응 모드 | 빠르게 확인할 수 있는 체크리스트 중심 안내 |

---

## 3. API 명세

### 3.1 위험도 예측 API

```text
POST /api/risk/predict
```

Request:

```json
{
  "region_name": "집 근처",
  "location": "진전면",
  "weather": "rain",
  "time_zone": "night",
  "season": "fall"
}
```

Response:

```json
{
  "success": true,
  "result": {
    "predicted_score": 74.81,
    "risk_grade_korean": "높음",
    "main_risk_species": "멧돼지",
    "historical_count": 136,
    "actions": []
  }
}
```

### 3.2 대응 상담 API

```text
POST /api/chat/message
```

Request:

```json
{
  "region_name": "집 근처",
  "location": "진전면",
  "weather": "rain",
  "time_zone": "night",
  "season": "fall",
  "consultation_mode": "field",
  "message": "지금 바로 어떻게 해야 돼?"
}
```

Response:

```json
{
  "success": true,
  "result": {
    "answer": "[현장 대응 모드] ...",
    "consultation_mode": "field",
    "mode_name": "현장 대응 모드",
    "risk_result": {}
  }
}
```
