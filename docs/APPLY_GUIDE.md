# 적용 방법

이 zip은 프로젝트 루트 기준 폴더 구조를 그대로 맞춘 수정 파일입니다.

## 포함 파일

- README.md
- templates/risk.html
- services/risk_prediction_service.py

## 적용 위치

압축을 풀어 아래 프로젝트에 덮어씌우면 됩니다.

```cmd
E:\Projects\wildguard-ai
```

## 적용 후 테스트

```cmd
cd /d E:\Projects\wildguard-ai
python app.py
```

브라우저에서 확인:

```text
http://127.0.0.1:5000/risk
```

API 테스트:

```cmd
curl -X POST http://127.0.0.1:5000/api/risk/predict ^
-H "Content-Type: application/json" ^
-d "{\"day\":\"night\",\"camera_type\":\"IR\",\"weather\":\"rain\",\"location\":\"산림\",\"time_zone\":\"night\",\"season\":\"fall\",\"species\":\"멧돼지\",\"object_count\":4,\"max_bbox_area_ratio\":0.08,\"avg_bbox_area_ratio\":0.05}"
```

## 커밋

```cmd
git status
git add README.md templates\risk.html services\risk_prediction_service.py
git commit -m "feat: show roadkill risk details on risk page"
git pull --rebase origin main
git push origin main
```
