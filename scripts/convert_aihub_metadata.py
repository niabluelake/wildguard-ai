import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

JSON_DIR = BASE_DIR / "data" / "aihub_json" / "TL-quadruped"
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


def make_risk_level(row):
    score = 0

    # 객체 수가 많을수록 위험도 증가
    if row["object_count"] >= 3:
        score += 2
    elif row["object_count"] == 2:
        score += 1

    # bbox가 클수록 카메라에 가까운 상황으로 판단
    if row["max_bbox_area_ratio"] >= 0.05:
        score += 2
    elif row["max_bbox_area_ratio"] >= 0.02:
        score += 1

    # 야간/새벽이면 대응 위험 증가
    if row["time_zone"] in ["night", "dawn"]:
        score += 1

    # IR 카메라 + night 조합이면 야간 출현 상황으로 판단
    if row["day"] == "night":
        score += 1

    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


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

    row["risk_level"] = make_risk_level(row)

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

    print("[INFO] species 분포")
    print(df["species"].value_counts().head(20))
    print()

    print("[INFO] 미리보기")
    print(df.head())