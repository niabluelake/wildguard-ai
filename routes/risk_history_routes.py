from flask import Blueprint, render_template

from services.risk_log_service import get_recent_risk_logs


risk_history_bp = Blueprint("risk_history", __name__)


@risk_history_bp.route("/risk/history")
def risk_history():
    logs = get_recent_risk_logs(limit=50)
    return render_template("risk_history.html", logs=logs)
