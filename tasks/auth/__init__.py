from datetime import datetime, timedelta
import jwt
from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ...models import User
from .decorators import token_required  # adjust import to your structure

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@auth_bp.route("/register", methods=["POST"])
def register():
    print("register called, current_app:", current_app.name)
    print("db id in auth:", id(db))

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
        return (
            jsonify({
                "error": "VALIDATION_ERROR",
                "message": "Invalid registration data",
                "details": details,
            }),
            400,
        )

    existing = User.query.filter_by(username=username).first()
    if existing:
        # TEMP: clearly incorrect status so we see it
        return (
            jsonify({
                "error": "DUPLICATE_USERNAME",
                "message": "Username already taken",
                "details": {"username": "This username is already in use"},
            }),
            409,
        )

    password_hash = generate_password_hash(password)
    user = User(username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return (
        jsonify({
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at.isoformat(),
        }),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "username and password are required"}, 400

    user = User.query.filter_by(username=username).first()

    # Generic error message – same for unknown user and wrong password
    generic_error = {
        "error": "INVALID_CREDENTIALS",
        "message": "Invalid username or password",
    }
    if user is None:
        return generic_error, 401

    if not check_password_hash(user.password_hash, password):
        return generic_error, 401

    secret = current_app.config["JWT_SECRET"]
    lifetime_minutes = current_app.config["JWT_LIFETIME_MINUTES"]

    now = datetime.utcnow()
    exp = now + timedelta(minutes=lifetime_minutes)

    payload = {
        "sub": str(user.id),  # subject must be string
        "role": "user",  # simple fixed role for now
        "exp": exp,
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    return jsonify({"token": token}), 200


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_me():
    user = User.query.get(g.current_user_id)
    if user is None:
        return (
            jsonify({
                "error": "USER_NOT_FOUND",
                "message": "User not found",
            }),
            404,
        )

    return (
        jsonify({
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at.isoformat(),
        }),
        200,
    )


@auth_bp.route("/me", methods=["PATCH"])
@token_required
def update_me():
    user = User.query.get(g.current_user_id)
    if user is None:
        return (
            jsonify({
                "error": "USER_NOT_FOUND",
                "message": "User not found",
            }),
            404,
        )

    data = request.get_json(silent=True) or {}

    if "password_hash" in data or "password" in data:
        return (
            jsonify({
                "error": "FORBIDDEN_FIELD",
                "message": "Password fields cannot be updated via this endpoint",
            }),
            400,
        )

    if "username" in data:
        username = data.get("username")
        if not isinstance(username, str) or not username:
            return (
                jsonify({
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid profile data",
                    "details": {"username": "Username is required"},
                }),
                400,
            )

        if len(username) < 3 or len(username) > 16:
            return (
                jsonify({
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid profile data",
                    "details": {
                        "username": "Username must be between 3 and 16 characters"
                    },
                }),
                400,
            )

        existing = User.query.filter(
            User.username == username, User.id != user.id
        ).first()
        if existing:
            return (
                jsonify({
                    "error": "DUPLICATE_USERNAME",
                    "message": "Username already taken",
                    "details": {"username": "This username is already in use"},
                }),
                409,
            )

        user.username = username
        db.session.commit()

    return (
        jsonify({
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at.isoformat(),
        }),
        200,
    )


@tasks_bp.route("/", methods=["GET"])
@token_required
def list_tasks():
    return jsonify({"message": "You reached a protected tasks route!"}), 200


@auth_bp.route("/admin/ping", methods=["GET"])
@token_required
def admin_ping():
    user = User.query.get(g.current_user_id)
    if user is None:
        return (
            jsonify({
                "error": "USER_NOT_FOUND",
                "message": "User not found",
            }),
            404,
        )

    if user.role != "admin":
        return (
            jsonify({
                "error": "FORBIDDEN",
                "message": "Admin privileges required",
            }),
            403,
        )

    return (
        jsonify({
            "status": "ok",
            "message": "Welcome, admin",
            "user_id": user.id,
        }),
        200,
    )
