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
    page_raw = request.args.get("page", "1")
    per_page_raw = request.args.get("per_page", "10")

    details = {}

    try:
        page = int(page_raw)
        if page < 1:
            details["page"] = "Page must be a positive integer (>= 1)."
    except ValueError:
        details["page"] = "Page must be a valid integer."

    try:
        per_page = int(per_page_raw)
        if per_page < 1 or per_page > 50:
            details["per_page"] = "Per page must be an integer between 1 and 50."
    except ValueError:
        details["per_page"] = "Per page must be a valid integer."

    if details:
        return jsonify({
            "error": "VALIDATION_ERROR",
            "message": "Invalid query parameters",
            "details": details
        }), 400

    base_query = Commission.query.filter_by(user_id=g.current_user_id)
    total = base_query.count()
    pages = (total + per_page - 1) // per_page

    offset = (page - 1) * per_page

    commissions = (
        base_query
        .order_by(Commission.id)
        .limit(per_page)
        .offset(offset)
        .all()
    )

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

    return jsonify({
        "items": results,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
        }
    }), 200




@main_bp.route("/commissions/<int:commission_id>", methods=["GET"])
@token_required
def get_commission(commission_id):
    commission = db.session.get(Commission, commission_id)

    if commission is None:
        return jsonify({
            "error": "NOT_FOUND",
            "message": "Commission not found"
        }), 404

    if commission.user_id != g.current_user_id:
        return jsonify({
            "error": "FORBIDDEN",
            "message": "Unauthorized"
        }), 403

    return jsonify({
        "id": commission.id,
        "title": commission.title,
        "status": commission.status,
        "price": commission.price,
        "due_date": commission.due_date.isoformat() if commission.due_date else None,
        "created_at": commission.created_at.isoformat(),
        "user_id": commission.user_id,
    }), 200


@main_bp.route("/commissions/<int:commission_id>", methods=["PATCH"])
@token_required
def update_commission(commission_id):
    commission = db.session.get(Commission, commission_id)

    if commission is None:
        return jsonify({
            "error": "NOT_FOUND",
            "message": "Commission not found"
        }), 404

    if commission.user_id != g.current_user_id:
        return jsonify({
            "error": "FORBIDDEN",
            "message": "Unauthorized"
        }), 403

    data = request.get_json() or {}
    allowed_fields = {"title", "status", "price", "due_date"}

    if not any(field in data for field in allowed_fields):
        return jsonify({
            "error": "BAD_REQUEST",
            "message": "At least one field (title, status, price, or due_date) must be provided"
        }), 400

    if "title" in data:
        commission.title = data["title"]

    if "status" in data:
        commission.status = data["status"]

    if "price" in data:
        commission.price = data["price"]

    if "due_date" in data:
        commission.due_date = data["due_date"]

    db.session.commit()

    return jsonify({
        "id": commission.id,
        "title": commission.title,
        "status": commission.status,
        "price": commission.price,
        "due_date": commission.due_date.isoformat() if commission.due_date else None,
        "created_at": commission.created_at.isoformat(),
        "user_id": commission.user_id,
    }), 200


@main_bp.route("/commissions/<int:commission_id>", methods=["DELETE"])
@token_required
def delete_commission(commission_id):
    commission = db.session.get(Commission, commission_id)

    if commission is None:
        return jsonify({
            "error": "NOT_FOUND",
            "message": "Commission not found"
        }), 404

    if commission.user_id != g.current_user_id:
        return jsonify({
            "error": "FORBIDDEN",
            "message": "Unauthorized"
        }), 403

    db.session.delete(commission)
    db.session.commit()

    return "", 204