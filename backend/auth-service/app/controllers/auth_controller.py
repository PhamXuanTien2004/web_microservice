# app/controllers/auth_controller.py
from flask import Blueprint, request, jsonify, make_response
from config import Config
from app.models.user_model import Users
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
            "user_id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "telphone": user.telphone,
            "role": user.role.value,
            "sensors": user.sensors,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

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
            "role": user.role.value,
            "access": access_token,
            "refresh": refresh_token
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
def logout():
    # 1. Lấy token từ Cookie để đưa vào blacklist (nếu cần)
    # Lưu ý: Với cookie, client chỉ cần xóa cookie là logout, 
    # nhưng để an toàn phía server, ta vẫn nên blacklist token cũ.
    token = request.cookies.get("access_token_cookie")

    response = make_response(jsonify({"message": "Logout thành công"}))

    # 2. Xóa Cookies (Set value rỗng và hết hạn ngay lập tức)
    response.set_cookie('access_token_cookie', '', expires=0, httponly=True)
    response.set_cookie('refresh_token_cookie', '', expires=0, httponly=True, path='/auth/refresh')

    # 3. Blacklist logic (Optional nhưng khuyên dùng)
    if token:
        try:
            payload = decode_token(token, token_type="access")
            blacklist = TokenBlacklist(
                token=token,
                expired_at=datetime.fromtimestamp(payload["exp"])
            )
            db.session.add(blacklist)
            db.session.commit()
        except Exception:
            pass # Token lỗi hoặc hết hạn thì bỏ qua

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