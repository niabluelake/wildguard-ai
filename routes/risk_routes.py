from flask import Blueprint, render_template, request
from services.risk_service import predict_risk

risk_bp = Blueprint("risk", __name__, url_prefix="/risk")


@risk_bp.route("/", methods=["GET", "POST"])
def risk_page():
    result = None

    if request.method == "POST":
        form_data = {
            "species_name": request.form.get("species_name"),
            "habitat_name": request.form.get("habitat_name"),
            "area_name": request.form.get("area_name"),
            "year": request.form.get("year"),
        }

        result = predict_risk(form_data)

    return render_template("risk.html", result=result)