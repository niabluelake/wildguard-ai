from flask import Blueprint, jsonify, render_template, request

from services.chat_service import generate_chat_response


chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["GET"])
def chat_page():
    return render_template("chat.html")


@chat_bp.route("/api/chat/message", methods=["POST"])
def chat_message():
    try:
        input_data = request.get_json()

        if input_data is None:
            return jsonify({
                "success": False,
                "message": "JSON 요청 데이터가 없습니다.",
            }), 400

        required_fields = [
            "location",
            "weather",
            "time_zone",
            "season",
        ]

        missing_fields = [
            field for field in required_fields
            if field not in input_data or input_data[field] in [None, ""]
        ]

        if missing_fields:
            return jsonify({
                "success": False,
                "message": f"필수 입력이 없습니다: {missing_fields}",
            }), 400

        result = generate_chat_response(input_data)

        return jsonify({
            "success": True,
            "result": result,
        })

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