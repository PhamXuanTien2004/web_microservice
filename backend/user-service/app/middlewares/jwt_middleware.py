# app/middleware/jwt_middleware.py
from functools import wraps
from flask import request, jsonify, g
from app.services.TokenService import decode_token

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 1. Ưu tiên lấy từ Cookie (Bảo mật hơn)
        if 'access_token_cookie' in request.cookies:
            token = request.cookies.get('access_token_cookie')
        
        # 2. Fallback: Nếu không có cookie, thử kiểm tra Header 
        elif 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            # Decode và verify token như cũ
            payload = decode_token(token, token_type="access")
            # Lưu user_id vào biến global g để dùng trong controller
            g.user_id = payload['sub']
            g.role = payload.get('role', 'user')
            g.token_payload = payload
        except Exception as e:
            return jsonify({"message": str(e)}), 401

        return f(*args, **kwargs)

    return decorated