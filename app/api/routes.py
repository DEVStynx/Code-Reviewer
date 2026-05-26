from flask import Blueprint, request, render_template, redirect
from flask_jwt_extended import jwt_required, get_current_user, verify_jwt_in_request

from app.service.user_service import register_user, login_user
from app.service.ai_service import review_code, review_code_frontend

index_bp = Blueprint("index", __name__, url_prefix="")
api_bp = Blueprint("api", __name__, url_prefix="/api")


@index_bp.route("/login", methods=["GET"])
def login_site():
    return render_template("login.html")


@index_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", None)
    password = request.form.get("password", None)
    return login_user(username=username, password=password)


@index_bp.route("/register", methods=["GET"])
def register_site():
    return render_template("register.html")


@index_bp.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", " ")
    password = request.form.get("password", " ")
    return register_user(username=username, password=password)


@index_bp.route("/", methods=["GET"])
def index():
    try:
        verify_jwt_in_request(locations=["cookies"])
    except Exception:
        return redirect("/login")
    return render_template("index.html")


@index_bp.route("/review", methods=["POST"])
@jwt_required(locations=["cookies"])
def review():
    files = review_code_frontend(files=request.files.getlist("files"), code=request.form.get("code", None))
    return render_template("review.html", files=files)


@api_bp.route("/review", methods=["POST"])
@jwt_required()
def api_review():
    return review_code(files=request.files, code=request.form.get("code", None))


@api_bp.route("/me")
@jwt_required()
def test_thing():
    user = get_current_user()
    return {
        "id": user.user_id,
        "username": user.username
    }