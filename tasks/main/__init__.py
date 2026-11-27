from flask import Blueprint, jsonify, g, request
from datetime import datetime
from ...models import Task, User, Commission
from ..extensions import db
from ..auth.decorators import token_required

main_bp = Blueprint("main", __name__)



@main_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

@main_bp.route("/commissions", methods=["POST"])
@token_required
def create_commission():
    data = request.get_json() or {}

    title = data.get("title")
    status = data.get("status")
    price = data.get("price")
    due_date = data.get("due_date")

    details = {}

    if not isinstance(title, str) or not title.strip():
        details["title"] = "Title is required and must be a non-empty string."

    if not isinstance(status, str) or not status.strip():
        details["status"] = "Status is required and must be a non-empty string."

    # Check if price is missing, a boolean (since bool is a subclass of int in Python), or not a number
    if price is None or isinstance(price, bool) or not isinstance(price, (int, float)):
        details["price"] = "Price is required and must be a valid number."

    parsed_due_date = None

    if due_date is not None and due_date != "":
        if not isinstance(due_date, str):
            details["due_date"] = "Due date must be an ISO-formatted date string."
        else:
            try:
                parsed_due_date = datetime.fromisoformat(due_date)
            except ValueError:
                details["due_date"] = "Invalid date format. Expected ISO 8601 date string (e.g., YYYY-MM-DD)."
    
    if details:
        return jsonify({
            "error": "VALIDATION_ERROR",
            "message": "Invalid commission data",
            "details": details
        }), 400

    commission = Commission(
        title=title.strip(),
        status=status.strip(),
        price=float(price),
        due_date=parsed_due_date,
        user_id=g.current_user_id
    )

    db.session.add(commission)
    db.session.commit()

    return jsonify({
        "id": commission.id,
        "title": commission.title,
        "status": commission.status,
        "price": commission.price,
        "due_date": commission.due_date.isoformat() if commission.due_date else None,
        "created_at": commission.created_at.isoformat(),
        "user_id": commission.user_id
    }), 201


@main_bp.route("/commissions", methods=["GET"])
@token_required
def get_commissions():
    commissions = Commission.query.filter_by(user_id=g.current_user_id).all()

    results = [
        {
            "id": commission.id,
            "title": commission.title,
            "status": commission.status,
            "price": commission.price,
            "due_date": commission.due_date.isoformat() if commission.due_date else None,
            "created_at": commission.created_at.isoformat(),
            "user_id": commission.user_id,
        }
        for commission in commissions
    ]

    return jsonify(results), 200
