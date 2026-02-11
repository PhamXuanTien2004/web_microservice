# backend\user-service\app\middlewares\jwt_middleware.py

from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from datetime import datetime

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Ưu tiên lấy từ Header nếu có và hợp lệ
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                temp_token = auth_header.split(" ")[1]
                # CHỈ lấy nếu token không phải là chuỗi "undefined" hoặc rỗng
                if temp_token and temp_token != "undefined" and temp_token != "null":
                    token = temp_token
        
        # Nếu Header không có token hợp lệ, mới lấy từ Cookie
        if not token and 'access_token_cookie' in request.cookies:
            token = request.cookies.get('access_token_cookie')

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            # 3. Giải mã và kiểm tra Chữ ký + Hạn dùng
            # PyJWT tự động kiểm tra trường 'exp' trong payload
            secret_key = current_app.config.get('SECRET_KEY') or "SECRET_KEY"
            
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=["HS256"]
            )
            
            # 4. Trích xuất ID và lưu vào biến g (để Controller sử dụng)
            g.user_id = int (payload.get('sub'))
            
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token đã hết hạn!"}), 401
        except jwt.InvalidSignatureError:
            return jsonify({"message": "Chữ ký Token không hợp lệ!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token không hợp lệ!"}), 401
        except Exception as e:
            return jsonify({"message": f"Lỗi xác thực: {str(e)}"}), 401

        return f(*args, **kwargs)

    return decorated