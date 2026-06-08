from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.auth_service import authenticate_user, register_user


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = authenticate_user(username, password)

        if user is None:
            flash("아이디 또는 비밀번호가 올바르지 않습니다.")
            return render_template("login.html", username=username), 401

        session["user"] = {
            "user_id": user.get("user_id"),
            "username": user.get("username"),
            "name": user.get("name"),
            "role": user.get("role") or "지자체 담당자",
        }
        session["user_id"] = user.get("user_id")
        session["name"] = user.get("name") or user.get("username")
        session["role"] = user.get("role") or "지자체 담당자"

        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        name = request.form.get("name", "").strip() or None

        if not username or not password:
            flash("아이디와 비밀번호를 입력해 주세요.")
            return render_template("register.html"), 400

        if password != password_confirm:
            flash("비밀번호 확인이 일치하지 않습니다.")
            return render_template("register.html", username=username, name=name), 400

        try:
            register_user(username=username, password=password, name=name)
        except ValueError as error:
            flash(str(error))
            return render_template("register.html", username=username, name=name), 409

        flash("회원가입이 완료되었습니다. 로그인해 주세요.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    session.pop("name", None)
    session.pop("role", None)
    return redirect(url_for("main.index"))
