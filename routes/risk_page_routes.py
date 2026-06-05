from flask import Blueprint, render_template, session


risk_page_bp = Blueprint("risk_page", __name__)


@risk_page_bp.route("/risk")
def risk_page():
    return render_template("risk.html", user=session.get("user"))
