from ultralytics import YOLO
import os
import uuid
import cv2
from PIL import Image
MODEL_PATH = "models/vision/best.pt"
UPLOAD_DIR = "static/vision_uploads"
OUTPUT_DIR = "static/vision_outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)

def run_video_prediction(file):
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    video_path = os.path.join(UPLOAD_DIR, filename)
    file.save(video_path)

    cap = cv2.VideoCapture(video_path)

    frame_count = 0
    results = []
    saved_images = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 30프레임마다 1장 (대략 1초)
        if frame_count % 30 == 0:
            yolo_results = model(frame)
            result = yolo_results[0]

            result_image = result.plot()
            out_name = f"frame_{frame_count}_{filename}.jpg"
            out_path = os.path.join(OUTPUT_DIR, out_name)

            cv2.imwrite(out_path, result_image)

            saved_images.append(f"/static/vision_outputs/{out_name}")

        frame_count += 1

    cap.release()

    return {
        "frames": saved_images,
        "count": len(saved_images)
    }
def get_risk_level(conf):
    if conf >= 0.8:
        return "danger"
    elif conf >= 0.5:
        return "warning"
    return "safe"

def run_prediction(file):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise ValueError("지원하지 않는 이미지 형식입니다. jpg, jpeg, png, webp만 가능합니다.")

    # 업로드 이미지를 먼저 jpg로 변환해서 저장
    input_filename = f"{uuid.uuid4().hex}.jpg"
    upload_path = os.path.join(UPLOAD_DIR, input_filename)

    try:
        image = Image.open(file.stream)
        image = image.convert("RGB")
        image.save(upload_path, format="JPEG", quality=95)

    except Exception as error:
        raise ValueError(f"이미지 파일을 읽을 수 없습니다. 다른 jpg/png 파일로 테스트해주세요. 원인: {error}")

    results = model(upload_path, conf=0.25)
    result = results[0]

    detections = []

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        detections.append({
            "class_name": result.names[cls_id],
            "confidence": round(conf, 4),
            "bbox": [
                round(x1, 2),
                round(y1, 2),
                round(x2, 2),
                round(y2, 2)
            ],
            "risk_level": get_risk_level(conf)
        })

    result_image = result.plot()

    output_filename = f"result_{uuid.uuid4().hex}.jpg"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    success = cv2.imwrite(output_path, result_image)

    if not success:
        raise RuntimeError("결과 이미지 저장에 실패했습니다.")

    return {
        "detected": len(detections) > 0,
        "count": len(detections),
        "detections": detections,
        "result_image_url": f"/static/vision_outputs/{output_filename}"
    }

def run_video_prediction(file):
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    video_path = os.path.join(UPLOAD_DIR, filename)
    file.save(video_path)

    cap = cv2.VideoCapture(video_path)

    frame_count = 0
    saved_frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 30프레임마다 1장 분석 = 대략 1초당 1프레임
        if frame_count % 30 == 0:
            results = model(frame, conf=0.5)
            result = results[0]

            result_image = result.plot()
            output_filename = f"video_frame_{frame_count}_{uuid.uuid4()}.jpg"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            cv2.imwrite(output_path, result_image)

            saved_frames.append(f"/static/vision_outputs/{output_filename}")

        frame_count += 1

    cap.release()

    return {
        "count": len(saved_frames),
        "frames": saved_frames
    }