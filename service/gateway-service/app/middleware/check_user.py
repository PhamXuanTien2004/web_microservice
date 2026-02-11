import jwt
from flask import request, jsonify, current_app

def check_user():
    """
    Kiểm tra Token (Ưu tiên lấy từ Cookie -> sau đó mới check Header nếu cần)

    Trả về tuple:
      (True, payload, None) khi thành công
      (False, error_dict, status_code) khi thất bại
    """
    token = None

    # CÁCH 1: Lấy từ Cookie (Khuyên dùng cho Web App)
    token = request.cookies.get('access_token_cookie')

    # CÁCH 2: Nếu không có cookie, thử tìm trong Header (Cho Mobile/Postman check nhanh)
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    # Nếu tìm cả 2 nơi đều không thấy
    if not token:
        return False, {"error": "Unauthorized", "message": "Không tìm thấy Access Token"}, 401

    # Giải mã Token
    try:
        secret_key = current_app.config.get("SECRET_KEY")

        payload = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"]
        )

        if payload.get("type") != "access":
            return False, {"error": "Invalid Token Type", "message": "Đây không phải là Access Token"}, 401

        # --- THÀNH CÔNG ---
        # Trả về payload để dùng nếu cần (ví dụ lấy user_id forward sang service khác)
        return True, payload, None

    except jwt.ExpiredSignatureError:
        return False, {"error": "Token Expired", "message": "Phiên đăng nhập hết hạn"}, 401
    except jwt.InvalidTokenError:
        return False, {"error": "Invalid Token", "message": "Token không hợp lệ"}, 401
    except Exception as e:
        return False, {"error": "Internal Error", "message": str(e)}, 500