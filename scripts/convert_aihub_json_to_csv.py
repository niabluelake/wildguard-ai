import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

# 집/학원 공통 프로젝트 구조
JSON_DIR = BASE_DIR / "data" / "aihub" / "aihub_json" / "TL-quadruped"
OUTPUT_DIR = BASE_DIR / "data" / "aihub" / "ml_dataset"
OUTPUT_PATH = OUTPUT_DIR / "aihub_wildlife_metadata.csv"


def first_dict(value):
    if isinstance(value, dict):
        return value

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                return item

    return {}


def as_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        return [value]

    return []


def get_time_zone(hour):
    if hour is None:
        return "unknown"

    try:
        hour = int(hour)
    except ValueError:
        return "unknown"

    if 0 <= hour < 6:
        return "dawn"
    if 6 <= hour < 18:
        return "day"
    if 18 <= hour < 21:
        return "evening"
    return "night"


def get_season(month):
    if month is None:
        return "unknown"

    try:
        month = int(month)
    except ValueError:
        return "unknown"

    if month in [3, 4, 5]:
        return "spring"
    if month in [6, 7, 8]:
        return "summer"
    if month in [9, 10, 11]:
        return "fall"
    return "winter"


def normalize_species(value):
    if value is None:
        return "unknown"

    value = str(value)

    if "boar" in value.lower() or "scrofa" in value.lower() or "멧돼지" in value:
        return "멧돼지"
    if "water deer" in value.lower() or "고라니" in value:
        return "고라니"
    if "bear" in value.lower() or "반달가슴곰" in value:
        return "반달가슴곰"
    if "hare" in value.lower() or "rabbit" in value.lower() or "멧토끼" in value:
        return "멧토끼"

    return value


def get_bbox_area_ratio(annotation, image_width, image_height):
    bbox = annotation.get("bbox") or []
    bbox_area = 0

    # AI Hub 구조: [[x1, y1], [x2, y2]]
    if (
        isinstance(bbox, list)
        and len(bbox) == 2
        and isinstance(bbox[0], list)
        and isinstance(bbox[1], list)
        and len(bbox[0]) >= 2
        and len(bbox[1]) >= 2
    ):
        x1, y1 = bbox[0][:2]
        x2, y2 = bbox[1][:2]
        bbox_area = abs(float(x2) - float(x1)) * abs(float(y2) - float(y1))

    # 일반 구조: [x, y, w, h]
    elif isinstance(bbox, list) and len(bbox) >= 4:
        x, y, w, h = bbox[:4]
        bbox_area = float(w) * float(h)

    # dict 구조 대응
    elif isinstance(bbox, dict):
        if all(k in bbox for k in ["x", "y", "w", "h"]):
            bbox_area = float(bbox["w"]) * float(bbox["h"])
        elif all(k in bbox for k in ["xmin", "ymin", "xmax", "ymax"]):
            bbox_area = (float(bbox["xmax"]) - float(bbox["xmin"])) * (
                float(bbox["ymax"]) - float(bbox["ymin"])
            )

    image_area = max(float(image_width or 0) * float(image_height or 0), 1)
    return bbox_area / image_area


def make_risk_level(row):
    score = 0

    if row["object_count"] >= 3:
        score += 2
    elif row["object_count"] == 2:
        score += 1

    if row["max_bbox_area_ratio"] >= 0.05:
        score += 2
    elif row["max_bbox_area_ratio"] >= 0.02:
        score += 1

    if row["time_zone"] in ["night", "dawn"]:
        score += 1

    if row["day"] == "night":
        score += 1

    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"

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

    return max(
        [species_weights.get(species, 8) for species in species_list],
        default=8
    )


def make_risk_score(row):
    """
    AI Hub 야생동물 메타데이터를 기반으로 0~100 위험 점수를 생성한다.
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

    species_score = get_species_score(species)

    time_weights = {
        "dawn": 8,
        "day": 0,
        "evening": 6,
        "night": 10,
        "unknown": 3,
    }
    time_score = time_weights.get(time_zone, 3)

    weather_weights = {
        "sunny": 0,
        "cloudy": 3,
        "rain": 7,
        "snow": 8,
        "unknown": 2,
    }
    weather_score = weather_weights.get(weather, 2)

    object_count_score = max(0, object_count - 1) * 4
    object_count_score = min(object_count_score, 12)

    bbox_score = (max_bbox_area_ratio * 600) + (avg_bbox_area_ratio * 250)
    bbox_score = min(bbox_score, 30)

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

def parse_datetime_parts(image_info):
    date_created = image_info.get("date_created") or ""
    time_value = image_info.get("time") or ""

    hour = None
    month = None

    # 예: "2021.10.26 20:22:20"
    if isinstance(date_created, str) and " " in date_created:
        date_part, time_part = date_created.split(" ", 1)

        date_parts = date_part.replace("-", ".").replace("/", ".").split(".")
        if len(date_parts) >= 2:
            month = date_parts[1]

        if ":" in time_part:
            hour = time_part.split(":")[0]

    # 보조: time 값 예: "000001.682"
    if hour is None and isinstance(time_value, str):
        if ":" in time_value:
            hour = time_value.split(":")[0]
        elif len(time_value) >= 2 and time_value[:2].isdigit():
            hour = time_value[:2]

    return hour, month


def parse_json_file(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    image_info = first_dict(data.get("images") or data.get("image") or data.get("image_info"))
    meta = first_dict(data.get("metadata") or data.get("meta") or data.get("info"))

    annotations = (
        data.get("annotations")
        or data.get("annotation")
        or data.get("objects")
        or data.get("labeling")
        or []
    )

    if isinstance(annotations, dict):
        annotations = (
            annotations.get("objects")
            or annotations.get("annotations")
            or annotations.get("items")
            or [annotations]
        )

    annotations = as_list(annotations)

    image_width = image_info.get("width") or meta.get("width") or 1920
    image_height = image_info.get("height") or meta.get("height") or 1080

    file_name = (
        image_info.get("file_name")
        or image_info.get("filename")
        or data.get("file_name")
        or json_path.stem
    )

    day = image_info.get("day") or meta.get("day") or data.get("day") or "unknown"
    weather = image_info.get("weather") or meta.get("weather") or data.get("weather") or "unknown"

    camera_type = (
        image_info.get("type")
        or image_info.get("camera_type")
        or meta.get("type")
        or meta.get("camera_type")
        or data.get("type")
        or data.get("camera_type")
        or "unknown"
    )

    location = (
        image_info.get("location")
        or meta.get("location")
        or data.get("location")
        or "unknown"
    )

    hour, month = parse_datetime_parts(image_info)

    bbox_ratios = []
    species_list = []

    for annotation in annotations:
        if not isinstance(annotation, dict):
            continue

        species = (
            annotation.get("species")
            or annotation.get("category_name")
            or annotation.get("class_name")
            or annotation.get("label")
            or annotation.get("name")
            or data.get("species")
            or "unknown"
        )

        species_list.append(normalize_species(species))
        bbox_ratios.append(get_bbox_area_ratio(annotation, image_width, image_height))

    object_count = len(bbox_ratios)
    max_bbox_area_ratio = max(bbox_ratios) if bbox_ratios else 0
    avg_bbox_area_ratio = sum(bbox_ratios) / len(bbox_ratios) if bbox_ratios else 0

    row = {
        "json_file": str(json_path.relative_to(BASE_DIR)),
        "file_name": file_name,
        "day": str(day),
        "camera_type": str(camera_type),
        "weather": str(weather),
        "location": str(location),
        "time_zone": get_time_zone(hour),
        "season": get_season(month),
        "species": species_list[0] if species_list else "unknown",
        "object_count": object_count,
        "max_bbox_area_ratio": max_bbox_area_ratio,
        "avg_bbox_area_ratio": avg_bbox_area_ratio,
    }

    risk_score = make_risk_score(row)

    row["risk_score"] = risk_score
    row["risk_grade"] = make_risk_grade(risk_score)

    # 기존 API나 코드가 risk_level을 참조할 수 있으므로 일단 호환용으로 유지
    row["risk_level"] = row["risk_grade"]
    return row


def main():
    if not JSON_DIR.exists():
        raise FileNotFoundError(f"JSON 폴더가 없습니다: {JSON_DIR}")

    json_files = list(JSON_DIR.rglob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"JSON 파일이 없습니다: {JSON_DIR}")

    print(f"[INFO] JSON 파일 수: {len(json_files)}")

    rows = []

    for index, json_path in enumerate(json_files, start=1):
        try:
            rows.append(parse_json_file(json_path))
        except Exception as error:
            print(f"[WARN] 변환 실패: {json_path} / {error}")

        if index % 1000 == 0:
            print(f"[INFO] 처리 중: {index}/{len(json_files)}")

    df = pd.DataFrame(rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"[INFO] CSV 저장 완료: {OUTPUT_PATH}")
    print(f"[INFO] 데이터 크기: {df.shape}")
    print()
    print("[INFO] risk_level 분포")
    print(df["risk_level"].value_counts())
    print()
    print("[INFO] species 분포")
    print(df["species"].value_counts())


if __name__ == "__main__":
    main()