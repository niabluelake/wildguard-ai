from flask import Blueprint, jsonify, request

from services.risk_prediction_service import predict_risk


risk_bp = Blueprint("risk", __name__, url_prefix="/api/risk")


@risk_bp.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if data is None:
            return jsonify({
                "success": False,
                "message": "JSON 요청 데이터가 없습니다.",
            }), 400

        result = predict_risk(data)

        return jsonify({
            "success": True,
            "result": result,
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