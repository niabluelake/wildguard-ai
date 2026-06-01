import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

JSON_DIR = BASE_DIR / "data" / "aihub" / "aihub_json" / "TL-quadruped"
OUTPUT_DIR = BASE_DIR / "data" / "aihub" / "ml_dataset"
OUTPUT_PATH = OUTPUT_DIR / "aihub_wildlife_metadata.csv"


def safe_get(data, *keys, default=None):
    current = data

    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)

    return current if current is not None else default


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

    if "boar" in value.lower() or "멧돼지" in value:
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


def parse_json_file(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    image_info = first_dict(
        data.get("image")
        or data.get("images")
        or data.get("image_info")
        or {}
    )

    meta = first_dict(
        data.get("metadata")
        or data.get("meta")
        or data.get("info")
        or {}
    )

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

    image_width = (
        image_info.get("width")
        or meta.get("width")
        or safe_get(data, "image", "width")
        or 1920
    )
    image_height = (
        image_info.get("height")
        or meta.get("height")
        or safe_get(data, "image", "height")
        or 1080
    )

    file_name = (
        image_info.get("file_name")
        or image_info.get("filename")
        or data.get("file_name")
        or json_path.stem
    )

    day = (
        image_info.get("day")
        or meta.get("day")
        or data.get("day")
        or "unknown"
    )

    weather = (
        image_info.get("weather")
        or meta.get("weather")
        or data.get("weather")
        or "unknown"
    )

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

    date_created = image_info.get("date_created") or ""

    date_value = (
        meta.get("date")
        or data.get("date")
        or image_info.get("date")
        or date_created
        or ""
    )

    time_value = (
        image_info.get("time")
        or meta.get("time")
        or data.get("time")
        or ""
    )

    hour = None
    month = None

    # date_created 예: "2021.10.26 20:22:20"
    if isinstance(date_created, str) and " " in date_created:
        date_part, time_part = date_created.split(" ", 1)

        date_parts = date_part.replace("-", ".").replace("/", ".").split(".")
        if len(date_parts) >= 2:
            month = date_parts[1]

        if ":" in time_part:
            hour = time_part.split(":")[0]

    # date_created가 없으면 파일명/기존 time에서 보조 추출
    if hour is None and isinstance(time_value, str):
        if ":" in time_value:
            hour = time_value.split(":")[0]
        elif len(time_value) >= 2 and time_value[:2].isdigit():
            hour = time_value[:2]

    if month is None and isinstance(date_value, str):
        parts = date_value.replace("-", ".").replace("/", ".").split(".")
        if len(parts) >= 2:
            month = parts[1]

    bbox_ratios = []
    species_list = []

    for annotation in annotations:
        if not isinstance(annotation, dict):
            continue

        species = (
            annotation.get("species")
            or annotation.get("class")
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
        "time": str(time_value),
        "time_zone": get_time_zone(hour),
        "season": get_season(month),
        "species": species_list[0] if species_list else "unknown",
        "object_count": object_count,
        "max_bbox_area_ratio": max_bbox_area_ratio,
        "avg_bbox_area_ratio": avg_bbox_area_ratio,
    }

    row["risk_level"] = make_risk_level(row)
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
