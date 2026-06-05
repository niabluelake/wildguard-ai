from flask import Blueprint, jsonify, request, session

from services.risk_log_service import save_risk_prediction_log
from services.risk_prediction_service import predict_risk


risk_bp = Blueprint("risk", __name__, url_prefix="/api/risk")


@risk_bp.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = request.get_json()

        if input_data is None:
            return jsonify({
                "success": False,
                "message": "JSON 요청 데이터가 없습니다.",
            }), 400

        result = predict_risk(input_data)

        day = input_data.get("day")
        camera_type = input_data.get("camera_type")
        weather = input_data.get("weather")
        location = input_data.get("location")
        time_zone = input_data.get("time_zone")
        season = input_data.get("season")
        object_count = input_data.get("object_count")
        max_bbox_area_ratio = input_data.get("max_bbox_area_ratio")
        avg_bbox_area_ratio = input_data.get("avg_bbox_area_ratio")
        risk_level = result.get("risk_level")
        risk_message = result.get("message")

        if "user_id" in session:
            save_risk_prediction_log(
                user_id=session["user_id"],
                day=day,
                camera_type=camera_type,
                weather=weather,
                location=location,
                time_zone=time_zone,
                season=season,
                object_count=object_count,
                max_bbox_area_ratio=max_bbox_area_ratio,
                avg_bbox_area_ratio=avg_bbox_area_ratio,
                risk_level=risk_level,
                risk_message=risk_message,
            )
            saved_to_db = True
        else:
            saved_to_db = False

        return jsonify({
            "success": True,
            "result": result,
            "saved": saved_to_db,
            "saved_to_db": saved_to_db,
        })

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error),
        }), 400

    except FileNotFoundError as error:
        return jsonify({
            "success": False,
            "message": str(error),
        }), 500

    except Exception as error:
        return jsonify({
            "success": False,
            "message": f"서버 오류가 발생했습니다: {error}",
        }), 500
