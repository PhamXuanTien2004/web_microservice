# app/controllers/auth_controller.py
from flask import Blueprint, request, jsonify, make_response
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
from app.middleware.jwt_middleware import jwt_required 

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Cấu hình Cookie (Nên đưa vào config file trong thực tế)
COOKIE_SECURE = False # Đổi thành True khi chạy Production (HTTPS)
COOKIE_SAMESITE = 'Strict' 

@auth_bp.route("/register", methods=["POST"])
def register():
    schema = RegisterSchema()
    try:
        validated_data = schema.load(request.get_json())
        user = AuthService.register_user(validated_data)
        return jsonify({
            "message": "Register successful",
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None
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
        user = AuthService.login_user(
            username=data.get("username"),
            password=data.get("password")
        )
    except Exception as e:
         return jsonify({"error": str(e)}), 401

    if not user:
        return jsonify({"error": "Sai tên đăng nhập hoặc mật khẩu"}), 401

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    response = make_response(jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "access": access_token,
            "refresh": refresh_token,
            "is active": user.is_active
        }
    }))

    response.set_cookie(
        'access_token_cookie', # Tên cookie
        access_token,
        httponly=True,  
        secure=COOKIE_SECURE,     
        samesite=COOKIE_SAMESITE, 
        max_age=Config.JWT_ACCESS_EXPIRES 
    )

    response.set_cookie(
        'refresh_token_cookie',
        refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
            path='/auth/refresh', 
            max_age=Config.JWT_REFRESH_EXPIRES * 24 * 60 * 60
    )

    return response, 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required
def logout():
    # 1. Lấy token từ Cookie (Nhiệm vụ của Controller)
    access_token = request.cookies.get("access_token_cookie")
    refresh_token = request.cookies.get("refresh_token_cookie")

    # 2. Gọi Service để xử lý logic DB (Nếu có token)
    # Dù có token hay không, ta vẫn tiến hành bước 3 (xóa cookie)
    success = AuthService.logout_user(access_token, refresh_token)
    if not success:
         return jsonify({"message": "Lỗi hệ thống hoặc Token không hợp lệ"}), 500

    # 3. Tạo Response và Xóa Cookie (QUAN TRỌNG)
    response = make_response(jsonify({
        "message": "Đăng xuất thành công",
        "status": "success"
    }))

    # Xóa Cookie Access Token
    response.set_cookie('access_token_cookie', '', expires=0, httponly=True)
    
    # Xóa Cookie Refresh Token (Nhớ đúng path đã tạo lúc login)
    response.set_cookie('refresh_token_cookie', '', expires=0, httponly=True, path='/auth/refresh')

    return response, 200

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    # 1. Lấy refresh token từ Cookie (Chỉ cookie, không lấy header nữa)
    refresh_token = request.cookies.get("refresh_token_cookie")

    if not refresh_token:
        return jsonify({"error": "Thiếu refresh token trong cookie"}), 401

    try:
        payload = decode_token(refresh_token, token_type="refresh")
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

    user = Users.query.get(payload["sub"])
    if not user:
        return jsonify({"error": "User không tồn tại"}), 404

    # 2. Tạo Access Token mới
    new_access_token = generate_access_token(user)

    # 3. Trả về response kèm Cookie mới
    response = make_response(jsonify({"message": "Token refreshed"}))
    
    response.set_cookie(
        'access_token_cookie',
        new_access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=current_app.config.get('JWT_ACCESS_EXPIRES', 15) * 60
    )

    return response, 200