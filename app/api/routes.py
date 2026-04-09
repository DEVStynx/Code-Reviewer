from flask import Blueprint, request, render_template
from app.service.ai_service import review_code, review_code_frontend

index_bp = Blueprint("index", __name__, url_prefix="")
api_bp = Blueprint("api", __name__, url_prefix="/api")


@index_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@index_bp.route("/review", methods=["POST"])
def review():
    files = review_code_frontend(files=request.files, code=request.form.get("code", None))
    return render_template("review.html", files=files)


@api_bp.route("/review", methods=["POST"])
def api_review():
    return review_code(files=request.files, code=request.form.get("code", None))
