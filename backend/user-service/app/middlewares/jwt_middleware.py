# app/middleware/jwt_middleware.py
from functools import wraps
from flask import request, jsonify, g
from app.services.TokenService import decode_token
from app.models.TokenBlacklist import TokenBlacklist

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
            payload = decode_token(token, token_type="access")
            
            # KIỂM TRA BLACKLIST: Nếu token đã nằm trong DB thì không cho đi tiếp
            is_blacklisted = TokenBlacklist.query.filter_by(token=token).first()
            if is_blacklisted:
                return jsonify({"message": "Token has been revoked (Already Logged out)"}), 401

            g.user_id = payload['sub']
        except Exception as e:
            return jsonify({"message": str(e)}), 401

        return f(*args, **kwargs)
    return decorated