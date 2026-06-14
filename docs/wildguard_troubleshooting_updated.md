# WildGuard AI 트러블슈팅 문서

## 1. GitHub 동기화

작업 시작 전:

```cmd
cd /d E:\Projects\wildguard-ai
git pull origin main
git status
```

작업 종료 후:

```cmd
git status
git add <수정한 파일>
git commit -m "커밋 메시지"
git pull --rebase origin main
git push origin main
git status
```

---

## 2. rebase 실패

### 증상

```text
error: cannot pull with rebase: You have unstaged changes.
```

### 원인

커밋하지 않은 수정 파일이 있는 상태에서 `git pull --rebase`를 실행했다.

### 해결

수정이 필요한 파일이면 커밋한다.

```cmd
git add <파일>
git commit -m "커밋 메시지"
git pull --rebase origin main
```

수정이 실수면 되돌린다.

```cmd
git restore <파일>
git status
```

---

## 3. 모델 파일 없음

### 증상

```text
models/ml/area_risk_model.pkl
```

파일을 찾을 수 없다는 오류가 발생한다.

### 원인

모델 파일은 GitHub에 업로드하지 않기 때문에 PC마다 직접 생성해야 한다.

### 해결

```cmd
python scripts\create_area_risk_dataset.py
python scripts\train_area_risk_model.py
```

---

## 4. CSV 파일 없음

### 증상

```text
data/aihub/ml_dataset/aihub_wildlife_metadata.csv
```

파일을 찾을 수 없다.

### 해결

AI Hub 원본 JSON이 로컬에 있는지 확인한 뒤 변환 스크립트를 실행한다.

```cmd
python scripts\convert_aihub_json_to_csv.py
```

---

## 5. location fallback 문제

### 증상

위험도 예측 결과의 `historical_count`가 전체 데이터 수처럼 크게 나온다.

### 원인

입력한 `location` 값이 AI Hub 데이터의 실제 지역명과 일치하지 않아 fallback이 발생했다.

### 확인

```cmd
python -c "import pandas as pd; df=pd.read_csv(r'data\aihub\ml_dataset\aihub_wildlife_metadata.csv'); print(df['location'].value_counts().head(30))"
```

### 해결

`진전면`, `경남임곡리`, `경남화전동` 등 실제 데이터에 존재하는 지역명을 사용한다.
