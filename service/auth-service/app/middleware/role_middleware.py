"""
role_middleware.py
──────────────────
Decorator kiểm tra role của user sau khi đã xác thực JWT.

Dùng như sau:
    @auth_bp.post("/register")
    @jwt_required()           ← Bước 1: Kiểm tra token hợp lệ
    @require_role("admin")    ← Bước 2: Kiểm tra role
    def register(): ...
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def require_role(required_role: str):
    """
    Decorator kiểm tra role của user.

    Phải đặt SAU @jwt_required() để chắc chắn token đã được xác thực
    và ta có thể lấy claims từ token.

    Args:
        required_role: Role cần có để truy cập endpoint
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Lấy role từ JWT claims
            claims = get_jwt()
            # Giải thích: role được lưu trong claims khi tạo token
            user_role = claims.get("role")

            if user_role != required_role:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "INSUFFICIENT_ROLE",
                        "message": "Bạn không có quyền truy cập tài nguyên này.",
                    },
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator