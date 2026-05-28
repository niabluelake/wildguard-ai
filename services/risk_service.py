DANGER_SPECIES = ["멧돼지", "고라니", "너구리", "삵", "오소리", "들고양이"]


def predict_risk(form_data):
    species_name = form_data.get("species_name", "")
    habitat_name = form_data.get("habitat_name", "")
    area_name = form_data.get("area_name", "")
    year = form_data.get("year", "")

    score = 0
    reasons = []

    if species_name in DANGER_SPECIES:
        score += 2
        reasons.append(f"{species_name}은 주의가 필요한 야생동물입니다.")

    try:
        year_int = int(year)
        if year_int >= 2010:
            score += 1
            reasons.append("비교적 최근 출현 기록입니다.")
    except ValueError:
        reasons.append("출현년도 정보가 올바르지 않아 연도 점수는 제외했습니다.")

    if habitat_name:
        score += 1
        reasons.append(f"{habitat_name} 서식지 출현 기록이 있습니다.")

    if score >= 4:
        risk_level = "높음"
    elif score >= 2:
        risk_level = "보통"
    else:
        risk_level = "낮음"

    message = " ".join(reasons) if reasons else "입력된 정보만으로는 주의도를 높게 판단하기 어렵습니다."

    return {
        "species_name": species_name,
        "habitat_name": habitat_name,
        "area_name": area_name,
        "year": year,
        "risk_level": risk_level,
        "score": score,
        "message": message,
    }