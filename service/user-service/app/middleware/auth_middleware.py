import requests
from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import get_jwt

def validate_token_with_auth_service(token: str) -> dict:
    """
    Gọi auth-service endpoint POST api/auth/validate-token
    để xác thực token của user có hợp lệ hay không.
    returns:
        {
            "valid": True/False,
            "user_id": 123,
            "username": "john_doe",
            "roles": ["admin", "user"]
        }
    """
    auth_service_url = "http://auth-service:5001/api/auth/validate-token"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(auth_service_url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()  # Trả về thông tin user nếu token hợp lệ
        else:
            return None  # Token không hợp lệ
    except Exception as e:
        print(f"Error validating token with auth service: {e}")
        return None

def requires_auth(f):
    """
    Decorator để bảo vệ các endpoint cần xác thực.
    Sử dụng validate_token_with_auth_service để kiểm tra token.
    Nếu token hợp lệ, thông tin user sẽ được truyền vào hàm view.
    Nếu không, trả về 401 Unauthorized.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": {"code": "MISSING_TOKEN", "message": "Thiếu token."}
            }), 401
        
        token = auth_header.split(" ")[1]

        #Validate token với auth-service
        user_info = validate_token_with_auth_service(token)
        if not user_info:
            return jsonify({
                "success": False, 
                "error": {"code": "INVALID_TOKEN", "message": "Token đã hết hạn hoặc không hợp lệ."}
                }), 401
        
        # Lưu user_info vào g (global) để controller có thể truy cập thông tin user
        g.current_user_id = user_info.get("user_id")
        g.current_username = user_info.get("username")
        g.current_user_roles = user_info.get("roles")

        # Truyền thông tin user vào hàm view
        return f(user_info=user_info, *args, **kwargs)

    return decorated