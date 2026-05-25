from flask import Blueprint, request, render_template
from app.service.ai_service import review_code, review_code_frontend

index_bp = Blueprint("index", __name__, url_prefix="")
api_bp = Blueprint("api", __name__, url_prefix="/api")


@index_bp.route("/login", methods=["GET"])
def login_site():
    return render_template("login.html")


@index_bp.route("/login", methods=["POST"])
def login():
    pass


@index_bp.route("/register", methods=["GET"])
def register_site():
    return render_template("register.html")


@index_bp.route("/register", methods=["POST"])
def register():
    pass


@index_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@index_bp.route("/review", methods=["POST"])
def review():
    files = review_code_frontend(files=request.files.getlist("files"), code=request.form.get("code", None))
    return render_template("review.html", files=files)


@api_bp.route("/review", methods=["POST"])
def api_review():
    return review_code(files=request.files, code=request.form.get("code", None))
