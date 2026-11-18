from flask import Blueprint, jsonify, request
from ..models import User
from ..extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    details = {}
    
    if not username:
        details["username"] = "Username is required"
    elif len(username) < 3 or len(username) > 16:
        details["username"] = "Username must be between 3 and 16 characters"

    if not password:
        details["password"] = "Password is required"
    elif len(password) < 8:
        details["password"] = "Password must be at least 8 characters long"

    if details:
        return jsonify({
            "error": "VALIDATION_ERROR",
            "message": "Invalid registration data",
            "details": details,
        }), 400

    existing = User.query.filter_by(username=username).first()
    if existing:
        # TEMP: clearly incorrect status so we see it
        return jsonify({
            "error": "DUPLICATE_USERNAME",
            "message": "Username already taken",
            "details": {
            "username": "This username is already in use"}
            }), 409

    password_hash = generate_password_hash(password)
    user = User(username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at.isoformat()
    }), 201
