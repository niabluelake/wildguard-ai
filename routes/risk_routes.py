from flask import Blueprint, jsonify, request, session

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

        required_fields = ["district", "month"]

        missing_fields = [
            field for field in required_fields
            if field not in input_data or input_data[field] in [None, ""]
        ]

        if missing_fields:
            return jsonify({
                "success": False,
                "message": f"필수 입력이 없습니다: {missing_fields}",
            }), 400

        result = predict_risk({
            "district": input_data.get("district"),
            "month": input_data.get("month"),
        })

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