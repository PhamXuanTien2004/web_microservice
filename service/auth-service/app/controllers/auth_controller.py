# app/controllers/auth_controller.py
from flask import Blueprint, request, jsonify, make_response, current_app
from config import Config
from app.models.auth_model import Auths
from app.models.token_blacklist import TokenBlacklist
from app.services.token_service import (
    generate_access_token,
    generate_refresh_token,
    decode_token
)
from app import db
from datetime import datetime, timedelta
from app.schemas.register_schema import RegisterSchema
from app.services.auth_service import AuthService
from marshmallow import ValidationError
# Không đặt url_prefix ở đây — sẽ dùng url_prefix khi register blueprint
auth_bp = Blueprint("auth", __name__)

# Cấu hình Cookie (Nên đưa vào config file trong thực tế)
# Lấy từ Config nếu có, fallback an toàn cho development
COOKIE_SECURE = getattr(Config, 'COOKIE_SECURE', False)
COOKIE_SAMESITE = getattr(Config, 'COOKIE_SAMESITE', 'Lax')
COOKIE_PATH = getattr(Config, 'COOKIE_PATH', '/')

@auth_bp.route("/register", methods=["POST"])
def register():
    schema = RegisterSchema()
    try:
        validated_data = schema.load(request.get_json())
        user = AuthService.register_user(validated_data)
        return jsonify({
            "message": "Register successful",
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat()
        }), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    except Exception as e:
        # Bắt các lỗi logic từ Service (ví dụ: User Service chết, DB lỗi)
        # Tùy message bạn muốn hiển thị mà custom lại
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login(): 
    data = request.get_json()
    try:
        # AuthService nên ném ra ngoại lệ (ValueError/Exception) nếu sai pass hoặc user không tồn tại
        user = AuthService.login_user(
            username=data.get("username"),
            password=data.get("password")
        )
        
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        # jwt.encode có thể trả bytes trong một số phiên bản
        if isinstance(access_token, bytes):
            access_token = access_token.decode()
        if isinstance(refresh_token, bytes):
            refresh_token = refresh_token.decode()

        response = make_response(jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "is_active": user.is_active
            }
        }))

        # Thiết lập cookie thống nhất với Config
        # JWT_ACCESS_EXPIRES là phút trong Config -> chuyển sang giây cho max_age
        response.set_cookie(
            'access_token_cookie',
            access_token,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            path=COOKIE_PATH,
            max_age=int(Config.JWT_ACCESS_EXPIRES * 60)
        )

        response.set_cookie(
            'refresh_token_cookie',
            refresh_token,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            path=COOKIE_PATH,
            max_age=int(Config.JWT_REFRESH_EXPIRES * 24 * 60 * 60)
        )
        return response, 200

    except Exception as e:
        # Trả về lỗi chi tiết nếu login thất bại
        return jsonify({"error": str(e)}), 401

@auth_bp.route("/logout", methods=["POST"])
def logout():
    # 1. Lấy token từ Cookie (Nhiệm vụ của Controller)
    access_token = request.cookies.get("access_token_cookie")
    refresh_token = request.cookies.get("refresh_token_cookie")

    # 2. Cố gắng gọi Service để blacklist/revoke token nếu có
    try:
        AuthService.logout_user(access_token, refresh_token)
    except Exception as e:
        # Không trả lỗi cho client — tiếp tục xóa cookie để đảm bảo idempotency
        print(f"Warning: logout service failed: {e}")

    # 3. Tạo Response và Xóa Cookie (LUÔN thực hiện)
    response = make_response(jsonify({
        "message": "Đăng xuất thành công",
        "status": "success"
    }))

    # Xóa Cookie Access Token
    response.set_cookie('access_token_cookie', '', expires=0, httponly=True, path=COOKIE_PATH, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE)
    
    # Xóa Cookie Refresh Token
    response.set_cookie('refresh_token_cookie', '', expires=0, httponly=True, path=COOKIE_PATH, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE)

    return response, 200

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    refresh_token = request.cookies.get("refresh_token_cookie")
    if not refresh_token:
        return jsonify({"error": "No refresh token"}), 401

    # Kiểm tra blacklist (Giả sử bạn có hàm check này trong Service)
    if AuthService.is_token_blacklisted(refresh_token):
        return jsonify({"error": "Token has been revoked"}), 401

    try:
        payload = decode_token(refresh_token, token_type="refresh")
        user = Auths.query.get(payload["sub"]) 
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        new_access_token = generate_access_token(user)
        response = make_response(jsonify({"status": "refreshed"}))
        if isinstance(new_access_token, bytes):
            new_access_token = new_access_token.decode()

        response.set_cookie(
            'access_token_cookie',
            new_access_token,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            path=COOKIE_PATH,
            max_age=int(Config.JWT_ACCESS_EXPIRES * 60)
        )
        return response, 200
    except Exception as e:
        return jsonify({"error": "Invalid refresh token"}), 401