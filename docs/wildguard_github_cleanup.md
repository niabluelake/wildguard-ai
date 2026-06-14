# WildGuard AI GitHub 관리 규칙

## 1. 업로드 대상

GitHub에는 코드, 템플릿, 설정 예시, 문서만 업로드한다.

```text
app.py
routes/
services/
scripts/
templates/
static/
docs/
README.md
requirements.txt
```

---

## 2. 업로드 제외 대상

```text
.venv/
.idea/
__pycache__/
data/
models/ml/
*.pkl
*.joblib
*.pt
*.onnx
```

AI Hub 원본 데이터와 학습 모델 파일은 용량과 라이선스 문제로 로컬에서만 관리한다.

---

## 3. PC 이동 시 작업 규칙

작업 시작:

```cmd
git pull origin main
git status
```

작업 종료:

```cmd
git status
git add <필요한 파일만>
git commit -m "커밋 메시지"
git pull --rebase origin main
git push origin main
git status
```
