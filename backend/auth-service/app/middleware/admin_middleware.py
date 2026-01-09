# app/middleware/admin_middleware.py
from functools import wraps
from flask import request, jsonify, g
from app.services.user_service import get_user_by_id
from app.middleware.jwt_middleware import jwt_required

def admin_required(f):
    @wraps(f)
    @jwt_required  # Đảm bảo người dùng đã được xác thực trước
    def decorated(*args, **kwargs):
        token = None

        # 1. Ưu tiên lấy từ Cookie (Bảo mật hơn)
        if 'access_token_cookie' in request.cookies:
            token = request.cookies.get('access_token_cookie')
        
        # 2. Fallback: Nếu không có cookie, thử kiểm tra Header (để hỗ trợ testing bằng Postman hoặc Mobile
        elif 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:    
            payload = decode_token(token, token_type="access")
            user_role = payload.get('role')
            if user_role != 'admin':
                return jsonify({"message": "Admin access required"}), 403
        except Exception as e:
            return jsonify({"message": str(e)}), 401

        return f(*args, **kwargs)

    return decorated