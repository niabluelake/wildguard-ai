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


def make_chat_answer(risk_result: dict, user_message: str = "") -> str:
    region_name = risk_result.get("region_name") or risk_result.get("location", "선택 지역")
    location = risk_result.get("location", "선택 지역")
    weather = get_korean_weather(risk_result.get("weather", ""))
    time_zone = get_korean_time_zone(risk_result.get("time_zone", ""))
    season = get_korean_season(risk_result.get("season", ""))

    predicted_score = risk_result.get("predicted_score")
    risk_grade_korean = risk_result.get("risk_grade_korean", "확인 필요")
    main_species = risk_result.get("main_risk_species", "확인 필요")
    message = risk_result.get("message", "")
    actions = risk_result.get("actions", [])

    action_text = "\n".join([f"- {action}" for action in actions])

    answer = f"""현재 {region_name} 기준으로 확인한 결과입니다.

지역: {location}
조건: {weather}, {time_zone}, {season}
예상 위험 점수: {predicted_score}점
위험 수준: {risk_grade_korean}
주의 가능성이 높은 동물: {main_species}

{message}

권장 행동:
{action_text}

이 결과는 AI Hub 야생동물 관측 데이터를 기반으로 한 참고용 예측입니다. 실제로 야생동물을 발견했다면 가까이 가지 말고 안전한 장소로 이동하세요."""

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

    risk_result = predict_risk(risk_input)
    answer = make_chat_answer(risk_result, user_message)

    return {
        "answer": answer,
        "risk_result": risk_result,
    }