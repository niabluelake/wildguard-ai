# 임시 문서 정리 안내

`docs/APPLY_GUIDE.md`는 이전에 zip 적용을 위해 만들어진 임시 가이드 문서입니다.

프로젝트 공식 문서로 유지할 필요가 없다면 삭제하는 것을 권장합니다.

```cmd
del docs\APPLY_GUIDE.md
git add README.md docs\REQUIREMENTS_ANALYSIS.md docs\FUNCTION_SPEC.md docs\PRD.md docs\wildguard_web_service_spec.md docs\APPLY_GUIDE.md
git commit -m "docs: update project docs for roadkill risk model"
git pull --rebase origin main
git push origin main
```

삭제하지 않고 남겨도 서비스 실행에는 영향이 없습니다.
