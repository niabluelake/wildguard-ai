from pathlib import Path
import json
import re

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_CSV = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_wildlife_metadata.csv"
OUTPUT_CSV = BASE_DIR / "data" / "aihub" / "ml_dataset" / "aihub_wildlife_metadata_with_gps.csv"


def parse_gps_value(gps_value):
    """
    AI Hub JSON의 GPS 값을 latitude, longitude로 변환한다.
    GPS가 dict, list, 문자열 중 어떤 형태여도 최대한 처리한다.
    """
    if gps_value is None:
        return None, None

    if isinstance(gps_value, dict):
        lat = (
            gps_value.get("latitude")
            or gps_value.get("lat")
            or gps_value.get("위도")
            or gps_value.get("Latitude")
        )
        lon = (
            gps_value.get("longitude")
            or gps_value.get("lon")
            or gps_value.get("lng")
            or gps_value.get("경도")
            or gps_value.get("Longitude")
        )
        return to_float(lat), to_float(lon)

    if isinstance(gps_value, (list, tuple)) and len(gps_value) >= 2:
        return to_float(gps_value[0]), to_float(gps_value[1])

    if isinstance(gps_value, str):
        nums = re.findall(r"[-+]?\d+\.\d+|[-+]?\d+", gps_value)
        if len(nums) >= 2:
            return to_float(nums[0]), to_float(nums[1])

    return None, None


def to_float(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def find_gps_in_json(data):
    """
    JSON 내부에서 GPS 값을 찾는다.
    주로 images 영역에 있으나, 구조가 조금 달라도 최대한 탐색한다.
    """
    images = data.get("images")

    if isinstance(images, list) and images:
        image_info = images[0]
        if isinstance(image_info, dict):
            gps_value = (
                image_info.get("GPS")
                or image_info.get("gps")
                or image_info.get("Gps")
                or image_info.get("location_gps")
            )
            lat, lon = parse_gps_value(gps_value)

            if lat is not None and lon is not None:
                return lat, lon

            lat = (
                image_info.get("latitude")
                or image_info.get("lat")
                or image_info.get("위도")
            )
            lon = (
                image_info.get("longitude")
                or image_info.get("lon")
                or image_info.get("lng")
                or image_info.get("경도")
            )
            return to_float(lat), to_float(lon)

    if isinstance(images, dict):
        gps_value = images.get("GPS") or images.get("gps")
        lat, lon = parse_gps_value(gps_value)

        if lat is not None and lon is not None:
            return lat, lon

    return None, None


def resolve_json_path(json_file_value):
    """
    CSV의 json_file 값이 절대경로/상대경로 모두 가능하게 처리한다.
    """
    path = Path(str(json_file_value))

    if path.is_absolute():
        return path

    return BASE_DIR / path


def main():
    print("[INFO] Load ML dataset")
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")

    latitudes = []
    longitudes = []

    total = len(df)

    for idx, json_file in enumerate(df["json_file"], start=1):
        json_path = resolve_json_path(json_file)

        lat = None
        lon = None

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            lat, lon = find_gps_in_json(data)

        except Exception as e:
            if idx <= 5:
                print(f"[WARN] Failed to read {json_path}: {e}")

        latitudes.append(lat)
        longitudes.append(lon)

        if idx % 1000 == 0:
            print(f"[INFO] Processed {idx:,}/{total:,}")

    df["latitude"] = latitudes
    df["longitude"] = longitudes

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print("[DONE] Saved:", OUTPUT_CSV)
    print("[INFO] Shape:", df.shape)
    print("[INFO] Missing GPS count")
    print(df[["latitude", "longitude"]].isna().sum())
    print("[INFO] GPS sample")
    print(df[["json_file", "latitude", "longitude"]].head())


if __name__ == "__main__":
    main()