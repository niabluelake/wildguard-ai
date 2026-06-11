from flask import Blueprint, render_template, request, jsonify, session

from services.vision_service import run_prediction, run_video_prediction


vision_bp = Blueprint("vision", __name__)


@vision_bp.route("/vision")
def vision_page():
    return render_template("vision.html")


@vision_bp.route("/api/vision/predict", methods=["POST"])
def predict_image():
    try:
        if "image" not in request.files:
            return jsonify({
                "success": False,
                "message": "이미지 파일이 없습니다."
            }), 400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({
                "success": False,
                "message": "선택된 이미지 파일이 없습니다."
            }), 400

        result = run_prediction(file)

        result["success"] = True
        result["saved_to_db"] = bool(session.get("user_id"))

        return jsonify(result)

    except Exception as error:
        return jsonify({
            "success": False,
            "message": f"이미지 분석 중 오류가 발생했습니다: {error}"
        }), 500


@vision_bp.route("/api/vision/video", methods=["POST"])
def video_predict():
    try:
        if "video" not in request.files:
            return jsonify({
                "success": False,
                "message": "영상 파일이 없습니다."
            }), 400

        file = request.files["video"]

        if file.filename == "":
            return jsonify({
                "success": False,
                "message": "선택된 영상 파일이 없습니다."
            }), 400

        result = run_video_prediction(file)

        result["success"] = True
        result["saved_to_db"] = bool(session.get("user_id"))

        return jsonify(result)

    except Exception as error:
        return jsonify({
            "success": False,
            "message": f"영상 분석 중 오류가 발생했습니다: {error}"
        }), 500