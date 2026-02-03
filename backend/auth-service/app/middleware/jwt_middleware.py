# app/middleware/jwt_middleware.py
from functools import wraps
from flask import request, jsonify, g
from app.services.token_service import decode_token
import jwt # Nếu hàm decode_token của bạn raise lỗi thư viện jwt

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 1. Ưu tiên lấy từ Cookie (Logic của bạn đúng rồi)
        if 'access_token_cookie' in request.cookies:
            token = request.cookies.get('access_token_cookie')
        
        # 2. Fallback: Check Header
        elif 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        # --- PHẦN BỔ SUNG QUAN TRỌNG ---
        try:
            # 3. Xác thực và giải mã token
            # Hàm này sẽ ném lỗi nếu token hết hạn hoặc sai chữ ký
            payload = decode_token(token) 
            
            # 4. Gắn thông tin vào biến g để Controller sử dụng
            # Giả sử trong token bạn lưu user_id ở key 'sub' hoặc 'id'
            g.user_id = payload.get("sub") 
            g.user_role = payload.get("role") # (Tùy chọn) Lưu thêm role nếu cần
            
        except Exception as e:
            # Trả về 401 nếu token sai/hết hạn
            return jsonify({
                "message": "Invalid or Expired Token", 
                "error": str(e)
            }), 401
        # -------------------------------

        return f(*args, **kwargs)

    return decorated