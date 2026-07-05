from typing import List, Dict, Any

from flask import redirect, render_template
from flask_jwt_extended import get_current_user
from app.database import db
from app.models.query import Query



def get_reviews():
    current_user = get_current_user()
    if not current_user:
        return redirect("/")

    queries : List[Dict[str, Any]] = []
    queries = current_user.get_user_queries()
    return render_template("queries.html", queries=queries)
