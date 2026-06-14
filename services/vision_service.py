from ultralytics import YOLO
import os
import uuid
import cv2
from PIL import Image

MODEL_PATH = "models/vision/best.pt"
UPLOAD_DIR = "static/vision_uploads"
OUTPUT_DIR = "static/vision_outputs"

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)


def get_risk_level(confidence):
    if confidence >= 0.8:
        return "danger"
    if confidence >= 0.5:
        return "warning"
    return "safe"


def _build_detection(result, box):
    cls_id = int(box.cls[0])
    confidence = float(box.conf[0])
    x1, y1, x2, y2 = box.xyxy[0].tolist()

    return {
        "class_name": result.names[cls_id],
        "confidence": round(confidence, 4),
        "bbox": [
            round(x1, 2),
            round(y1, 2),
            round(x2, 2),
            round(y2, 2),
        ],
        "risk_level": get_risk_level(confidence),
    }


def run_prediction(file):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("지원하지 않는 이미지 형식입니다. jpg, jpeg, png, webp만 가능합니다.")

    input_filename = f"{uuid.uuid4().hex}.jpg"
    upload_path = os.path.join(UPLOAD_DIR, input_filename)

    try:
        image = Image.open(file.stream)
        image = image.convert("RGB")
        image.save(upload_path, format="JPEG", quality=95)
    except Exception as error:
        raise ValueError(f"이미지 파일을 읽을 수 없습니다. 다른 jpg/png 파일로 테스트해주세요. 원인: {error}")

    yolo_results = model(upload_path, conf=0.25)
    result = yolo_results[0]

    detections = [_build_detection(result, box) for box in result.boxes]

    result_image = result.plot()
    output_filename = f"result_{uuid.uuid4().hex}.jpg"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    if not cv2.imwrite(output_path, result_image):
        raise RuntimeError("결과 이미지 저장에 실패했습니다.")

    return {
        "detected": len(detections) > 0,
        "count": len(detections),
        "detections": detections,
        "result_image_url": f"/static/vision_outputs/{output_filename}",
    }


def run_video_prediction(file):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValueError("지원하지 않는 영상 형식입니다. mp4, avi, mov, mkv, webm만 가능합니다.")

    input_filename = f"{uuid.uuid4().hex}{ext}"
    video_path = os.path.join(UPLOAD_DIR, input_filename)
    file.save(video_path)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        cap.release()
        raise ValueError("영상 파일을 열 수 없습니다. 다른 mp4 파일로 테스트해주세요.")

    frame_count = 0
    analyzed_count = 0
    saved_frames = []

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            # 30프레임마다 1장 분석한다. 일반적인 30fps 영상 기준 약 1초 간격이다.
            if frame_count % 30 == 0:
                yolo_results = model(frame, conf=0.5)
                result = yolo_results[0]
                result_image = result.plot()

                output_filename = f"video_frame_{frame_count}_{uuid.uuid4().hex}.jpg"
                output_path = os.path.join(OUTPUT_DIR, output_filename)

                if cv2.imwrite(output_path, result_image):
                    saved_frames.append(f"/static/vision_outputs/{output_filename}")

                analyzed_count += 1

            frame_count += 1
    finally:
        cap.release()

    return {
        "count": len(saved_frames),
        "frames": saved_frames,
        "total_frames": frame_count,
        "analyzed_frames": analyzed_count,
    }
