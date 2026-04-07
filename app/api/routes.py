from flask import Blueprint, request, jsonify, render_template
from app.service.ai_service import review_code

index_bp = Blueprint("index", __name__, url_prefix="")
api_bp = Blueprint("api", __name__, url_prefix="/api")


@index_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@api_bp.route("/review", methods=["POST"])
def review():
    return review_code()
