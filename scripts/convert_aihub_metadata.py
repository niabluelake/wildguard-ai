import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

JSON_DIR = BASE_DIR / "data" / "aihub" / "aihub_json" / "TL-quadruped"
OUTPUT_PATH = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_wildlife_metadata.csv"


def get_season_from_date(date_text):
    if not date_text:
        return "unknown"

    try:
        month = int(str(date_text).split(".")[1])
    except (IndexError, ValueError):
        return "unknown"

    if month in [3, 4, 5]:
        return "spring"
    if month in [6, 7, 8]:
        return "summer"
    if month in [9, 10, 11]:
        return "fall"
    if month in [12, 1, 2]:
        return "winter"

    return "unknown"


def parse_hour(date_text):
    if not date_text or " " not in str(date_text):
        return None

    try:
        time_part = str(date_text).split(" ")[1]
        return int(time_part.split(":")[0])
    except (IndexError, ValueError):
        return None


def get_time_zone(hour):
    if hour is None:
        return "unknown"

    if 5 <= hour < 8:
        return "dawn"
    if 8 <= hour < 18:
        return "day"
    if 18 <= hour < 21:
        return "evening"

    return "night"


def calc_bbox_area_ratio(bbox, image_width, image_height):
    try:
        x1, y1 = bbox[0]
        x2, y2 = bbox[1]

        box_width = max(0, x2 - x1)
        box_height = max(0, y2 - y1)

        image_area = image_width * image_height
        box_area = box_width * box_height

        if image_area == 0:
            return 0

        return box_area / image_area

    except (TypeError, IndexError, ValueError):
        return 0


def get_species_score(species_text):
    species_weights = {
        "멧토끼": 3,
        "고라니": 10,
        "멧돼지": 18,
        "반달가슴곰": 35,
    }

    if not species_text:
        return 8

    species_list = [item.strip() for item in str(species_text).split(",")]

    # 여러 종이 한 이미지에 있으면 가장 위험한 종 기준
    return max(
        [species_weights.get(species, 8) for species in species_list],
        default=8
    )


def make_risk_score(row):
    """
    AI Hub 야생동물 메타데이터를 기반으로 0~100 위험 점수를 생성한다.

    실제 사고/피해 점수 라벨이 없기 때문에,
    동물 종, 시간대, 날씨, 객체 수, bbox 면적 비율, 야간 촬영 여부에
    도메인 가중치를 부여해 초기 risk_score를 설계한다.
    """

    base_score = 3

    species = row.get("species", "unknown")
    time_zone = str(row.get("time_zone", "unknown")).lower()
    weather = str(row.get("weather", "unknown")).lower()
    camera_type = str(row.get("camera_type", "unknown")).upper()
    day = str(row.get("day", "unknown")).lower()

    try:
        object_count = float(row.get("object_count", 0))
    except (TypeError, ValueError):
        object_count = 0

    try:
        max_bbox_area_ratio = float(row.get("max_bbox_area_ratio", 0))
    except (TypeError, ValueError):
        max_bbox_area_ratio = 0

    try:
        avg_bbox_area_ratio = float(row.get("avg_bbox_area_ratio", 0))
    except (TypeError, ValueError):
        avg_bbox_area_ratio = 0

    # 1. 동물 종 위험도
    species_score = get_species_score(species)

    # 2. 시간대 위험도
    time_weights = {
        "dawn": 8,
        "day": 0,
        "evening": 6,
        "night": 10,
        "unknown": 3,
    }
    time_score = time_weights.get(time_zone, 3)

    # 3. 날씨 위험도
    weather_weights = {
        "sunny": 0,
        "cloudy": 3,
        "rain": 7,
        "snow": 8,
        "unknown": 2,
    }
    weather_score = weather_weights.get(weather, 2)

    # 4. 객체 수 위험도
    # 1마리는 기본 관측으로 보고, 2마리 이상부터 위험도 증가
    object_count_score = max(0, object_count - 1) * 4
    object_count_score = min(object_count_score, 12)

    # 5. bbox 면적 비율 위험도
    # 카메라 화면에서 동물이 크게 잡힐수록 근접 출현으로 판단
    bbox_score = (max_bbox_area_ratio * 600) + (avg_bbox_area_ratio * 250)
    bbox_score = min(bbox_score, 30)

    # 6. 야간 촬영 보정
    night_camera_score = 0

    if camera_type == "IR" and time_zone in ["night", "dawn"]:
        night_camera_score += 4

    if day == "night":
        night_camera_score += 3

    risk_score = (
        base_score
        + species_score
        + time_score
        + weather_score
        + object_count_score
        + bbox_score
        + night_camera_score
    )

    risk_score = max(0, min(100, risk_score))

    return round(risk_score, 2)


def make_risk_grade(risk_score):
    if risk_score < 45:
        return "low"
    if risk_score < 70:
        return "medium"
    return "high"


def parse_aihub_json(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    images = data.get("images", [])
    annotations = data.get("annotations", [])

    if not images:
        return None

    image = images[0]

    width = image.get("width", 0)
    height = image.get("height", 0)
    date_created = image.get("date_created")

    hour = parse_hour(date_created)

    species_set = set()
    category_set = set()
    hazardous_set = set()
    nocturnality_set = set()
    bbox_area_ratios = []

    for ann in annotations:
        species_set.add(ann.get("species", "unknown"))
        category_set.add(ann.get("category_name", "unknown"))
        hazardous_set.add(ann.get("hazardous", "unknown"))
        nocturnality_set.add(ann.get("nocturnality", "unknown"))

        bbox_area_ratios.append(
            calc_bbox_area_ratio(
                ann.get("bbox"),
                width,
                height
            )
        )

    object_count = len(annotations)

    max_bbox_area_ratio = max(bbox_area_ratios) if bbox_area_ratios else 0
    avg_bbox_area_ratio = (
        sum(bbox_area_ratios) / len(bbox_area_ratios)
        if bbox_area_ratios
        else 0
    )

    row = {
        "json_file": json_path.name,
        "image_id": image.get("id"),
        "file_name": image.get("file_name"),
        "width": width,
        "height": height,
        "date_created": date_created,
        "hour": hour,
        "time_zone": get_time_zone(hour),
        "season": get_season_from_date(date_created),
        "day": image.get("day", "unknown"),
        "camera_type": image.get("type", "unknown"),
        "location": image.get("location", "unknown"),
        "gps": image.get("GPS", None),
        "weather": image.get("weather", "unknown"),
        "object_count": object_count,
        "species": ",".join(sorted(species_set)),
        "category_name": ",".join(sorted(category_set)),
        "hazardous": "yes" if "yes" in hazardous_set else "no",
        "nocturnality": "yes" if "yes" in nocturnality_set else "no",
        "max_bbox_area_ratio": max_bbox_area_ratio,
        "avg_bbox_area_ratio": avg_bbox_area_ratio,
    }

    risk_score = make_risk_score(row)

    row["risk_score"] = risk_score
    row["risk_grade"] = make_risk_grade(risk_score)

    # 기존 API나 코드가 risk_level을 참조할 수 있으므로 일단 호환용으로 유지
    row["risk_level"] = row["risk_grade"]

    return row


def convert_all_json():
    rows = []
    json_files = list(JSON_DIR.rglob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"JSON 파일이 없습니다: {JSON_DIR}")

    for json_path in json_files:
        try:
            row = parse_aihub_json(json_path)
            if row:
                rows.append(row)
        except Exception as error:
            print(f"[WARN] 변환 실패: {json_path} / {error}")

    df = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    return df


if __name__ == "__main__":
    df = convert_all_json()

    print("[INFO] AI Hub JSON 메타데이터 변환 완료")
    print("[INFO] 데이터 크기:", df.shape)
    print("[INFO] 저장 위치:", OUTPUT_PATH)
    print()

    print("[INFO] risk_level 분포")
    print(df["risk_level"].value_counts())
    print()

    print("[INFO] risk_score 통계")
    print(df["risk_score"].describe())
    print()

    print("[INFO] risk_grade 분포")
    print(df["risk_grade"].value_counts())
    print()

    print("[INFO] species 분포")
    print(df["species"].value_counts().head(20))
    print()

    print("[INFO] 미리보기")
    print(df.head())