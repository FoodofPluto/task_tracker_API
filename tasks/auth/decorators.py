from functools import wraps
import jwt
from flask import current_app, g, jsonify, request


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]

        jwt_secret = current_app.config.get("JWT_SECRET")
        if not jwt_secret:
            raise RuntimeError("JWT_SECRET configuration is required")

        try:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            g.current_user_id = int(payload["sub"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token expired, please log in again"}), 401
        except (jwt.PyJWTError, KeyError, TypeError, ValueError):
            return jsonify({"error": "invalid token"}), 401

        g.role = payload.get("role", "user")

        return f(*args, **kwargs)
    return wrapper
