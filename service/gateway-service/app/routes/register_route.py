from flask import Blueprint, request, jsonify
import requests 
from app.services.auth_client import register_auth
from app.services.user_client import create_user_profile

register_bp = Blueprint("register", __name__)

@register_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    # 0️⃣ Validate input
    required_fields = ["username", "password", "name", "email", "telphone"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing
        }), 400

    # 1️⃣ Auth payload
    auth_payload = {
        "username": data["username"],
        "password": data["password"]
    }

    try:
        auth_res = requests.post(
            "http://localhost:5001/api/auth/register",
            json=auth_payload,
            timeout=5
        )
    except requests.exceptions.RequestException:
        return jsonify({"error": "Auth service unavailable"}), 503

    if auth_res.status_code != 201:
        return auth_res.json(), auth_res.status_code

    user_id = auth_res.json()["user_id"]

    # 2️⃣ User payload
    user_payload = {
        "user_id": user_id,
        "name": data["name"],
        "email": data["email"],
        "telphone": data["telphone"]
    }

    try:
        user_res = requests.post(
            "http://localhost:5002/api/user/internal/users",
            json=user_payload,
            timeout=5
        )
    except requests.exceptions.RequestException:
        return jsonify({"error": "User service unavailable"}), 503

    if user_res.status_code != 201:
        # rollback auth
        requests.delete(
            f"http://localhost:5001/api/auth/internal/users/{user_id}",
            timeout=5
        )
        return user_res.json(), user_res.status_code

    return jsonify({
        "message": "Register successful",
        "user_id": user_id
    }), 201
