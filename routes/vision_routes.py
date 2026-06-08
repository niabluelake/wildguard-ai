from flask import Blueprint, render_template, request, jsonify
from services.vision_service import run_prediction, run_video_prediction

vision_bp = Blueprint("vision", __name__)

@vision_bp.route("/vision")
def vision_page():
    return render_template("vision.html")

@vision_bp.route("/api/vision/video", methods=["POST"])
def video_predict():
    if "video" not in request.files:
        return jsonify({"error": "video required"}), 400

    file = request.files["video"]
    result = run_video_prediction(file)

    return jsonify(result)

@vision_bp.route("/api/vision/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "image required"}), 400

    file = request.files["image"]
    result = run_prediction(file)

    return jsonify(result)

