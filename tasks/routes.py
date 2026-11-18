from flask import jsonify
from . import tasks_bp
from tasks.models import Task, User


@tasks_bp.get("/tasks/health")
def tasks_health():
    return jsonify({"status": "ok"}), 200