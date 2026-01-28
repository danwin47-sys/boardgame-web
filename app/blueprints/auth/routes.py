from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from core.auth_service import AuthService
from core.user_model import User

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.route("/login")
def login():
    """導向至 LINE Login"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    login_url = auth_service.generate_login_url()
    return redirect(login_url)


@auth_bp.route("/line/callback")
def callback():
    """LINE Login Callback"""
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        flash("登入失敗：無效的請求", "error")
        return redirect(url_for("main.home"))

    success, profile, error = auth_service.handle_callback(code, state)

    if not success:
        flash(f"登入失敗：{error}", "error")
        return redirect(url_for("main.home"))

    # 檢查此 LINE 帳號是否已綁定
    line_user_id = profile.get("line_user_id")
    user_data = auth_service.check_user_exists(line_user_id)

    if user_data:
        # 已綁定 -> 自動登入
        user = User(user_data)
        login_user(user, remember=True)
        # 更新 Session 中的 LINE ID 備用
        session["line_user_id"] = line_user_id

        flash(f"歡迎回來，{user.name}！", "success")
        return redirect(url_for("main.home"))
    else:
        # 未綁定 -> 暫存 LINE 資料 -> 導向綁定頁面
        session["temp_line_profile"] = profile
        flash("請綁定您的社團工號以完成登入", "info")
        return redirect(url_for("auth.bind"))


@auth_bp.route("/bind", methods=["GET", "POST"])
def bind():
    """綁定工號頁面"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    profile = session.get("temp_line_profile")
    if not profile:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        student_id = request.form.get("student_id")

        success, message = auth_service.bind_student_id(profile.get("line_user_id"), student_id)

        if success:
            # 綁定成功，重新獲取使用者資料並登入
            user_data = auth_service.check_user_exists(profile.get("line_user_id"))
            if user_data:
                user = User(user_data)
                login_user(user, remember=True)
                session["line_user_id"] = profile.get("line_user_id")
                session.pop("temp_line_profile", None)  # 清除暫存

                flash(message, "success")
                return redirect(url_for("main.home"))
        else:
            flash(message, "error")

    return render_template("auth/bind.html", profile=profile)


@auth_bp.route("/logout")
def logout():
    session.clear()  # 清除自定義 session
    logout_user()  # Flask-Login 登出
    flash("已登出", "info")
    return redirect(url_for("main.home"))
