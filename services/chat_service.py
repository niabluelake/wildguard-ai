from services.risk_prediction_service import predict_risk


def get_korean_weather(weather: str) -> str:
    mapping = {
        "sunny": "맑음",
        "cloudy": "흐림",
        "rain": "비",
        "snow": "눈",
    }
    return mapping.get(weather, weather)


def get_korean_time_zone(time_zone: str) -> str:
    mapping = {
        "dawn": "새벽",
        "day": "낮",
        "evening": "해질 무렵",
        "night": "밤",
    }
    return mapping.get(time_zone, time_zone)


def get_korean_season(season: str) -> str:
    mapping = {
        "spring": "봄",
        "summer": "여름",
        "fall": "가을",
        "winter": "겨울",
    }
    return mapping.get(season, season)


def build_context(risk_result: dict) -> dict:
    return {
        "region_name": risk_result.get("region_name") or risk_result.get("location", "선택 지역"),
        "location": risk_result.get("location", "선택 지역"),
        "weather": get_korean_weather(risk_result.get("weather", "")),
        "time_zone": get_korean_time_zone(risk_result.get("time_zone", "")),
        "season": get_korean_season(risk_result.get("season", "")),
        "predicted_score": risk_result.get("predicted_score"),
        "risk_grade_korean": risk_result.get("risk_grade_korean", "확인 필요"),
        "main_species": risk_result.get("main_risk_species", "확인 필요"),
        "message": risk_result.get("message", ""),
        "actions": risk_result.get("actions", []),
        "historical_count": risk_result.get("historical_count", 0),
    }


def make_detailed_answer(risk_result: dict, user_message: str = "") -> str:
    context = build_context(risk_result)
    action_text = "\n".join([f"- {action}" for action in context["actions"]])

    answer = f"""[상세 상담 모드]

현재 {context["region_name"]} 기준으로 야생동물 출몰 위험도를 확인했습니다.

지역: {context["location"]}
조건: {context["weather"]}, {context["time_zone"]}, {context["season"]}
예상 위험 점수: {context["predicted_score"]}점
위험 수준: {context["risk_grade_korean"]}
주의 가능성이 높은 동물: {context["main_species"]}
과거 유사 관측 수: {context["historical_count"]}건

{context["message"]}

상황 해석:
현재 조건에서는 야간 이동, 시야 확보 어려움, 야생동물과의 갑작스러운 마주침 가능성을 주의해야 합니다.
특히 {context["main_species"]} 출현 가능성이 높게 예측되므로 단독 이동이나 접근은 피하는 것이 좋습니다.

권장 행동:
{action_text}

추가 안내:
이 결과는 AI Hub 야생동물 관측 데이터를 기반으로 한 참고용 예측입니다.
실제로 야생동물을 발견했다면 사진 촬영이나 접근을 시도하지 말고, 안전한 장소로 이동한 뒤 필요 시 관계 기관에 신고하세요."""

    if user_message:
        answer = f"질문: {user_message}\n\n" + answer

    return answer


def make_field_answer(risk_result: dict, user_message: str = "") -> str:
    context = build_context(risk_result)

    answer = f"""[현장 대응 모드]

위험 수준: {context["risk_grade_korean"]}
예상 점수: {context["predicted_score"]}점
주의 동물: {context["main_species"]}
지역: {context["location"]}
조건: {context["weather"]}, {context["time_zone"]}, {context["season"]}

바로 할 일:
1. 야간 이동이나 단독 접근을 피하세요.
2. 주변에 음식물, 사료, 쓰레기가 있으면 정리하세요.
3. 야생동물을 발견하면 가까이 가지 말고 즉시 거리를 확보하세요.
4. 반복 출현하거나 위협이 느껴지면 관계 기관에 신고하세요.

한 줄 요약:
현재 조건에서는 {context["main_species"]} 출현 가능성에 주의해야 하며, 불필요한 이동은 피하는 것이 좋습니다."""

    if user_message:
        answer = f"질문: {user_message}\n\n" + answer

    return answer


def generate_chat_response(input_data: dict) -> dict:
    risk_input = {
        "region_name": input_data.get("region_name", ""),
        "location": input_data.get("location", ""),
        "weather": input_data.get("weather", ""),
        "time_zone": input_data.get("time_zone", ""),
        "season": input_data.get("season", ""),
    }

    user_message = input_data.get("message", "").strip()
    consultation_mode = input_data.get("consultation_mode", "detail")

    risk_result = predict_risk(risk_input)

    if consultation_mode == "field":
        answer = make_field_answer(risk_result, user_message)
        mode_name = "현장 대응 모드"
    else:
        answer = make_detailed_answer(risk_result, user_message)
        mode_name = "상세 상담 모드"

    return {
        "answer": answer,
        "consultation_mode": consultation_mode,
        "mode_name": mode_name,
        "risk_result": risk_result,
    }