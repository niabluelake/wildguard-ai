from flask import Blueprint, render_template
from services.risk_log_service import get_recent_risk_logs

risk_history_bp = Blueprint("risk_history", __name__)


@risk_history_bp.route("/risk/history")
def risk_history():
    db_error = None
    logs = []

    try:
        logs = get_recent_risk_logs(limit=50)

    except Exception:
        db_error = (
            "DB 연결에 실패했습니다. Oracle DB가 실행 중인지 확인해주세요. "
            "현재는 저장된 예측 기록을 불러올 수 없습니다."
        )

    return render_template(
        "risk_history.html",
        logs=logs,
        db_error=db_error,
    )