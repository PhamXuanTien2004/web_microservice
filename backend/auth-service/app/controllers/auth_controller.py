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
@jwt_required
def logout():

    # 1. Debug xem cookie có tồn tại không
    access_token = request.cookies.get("access_token_cookie")
    refresh_token = request.cookies.get("refresh_token_cookie")
    
    print(f"DEBUG: Access Token found: {access_token is not None}")
    print(f"DEBUG: Refresh Token found: {refresh_token is not None}")

    response = make_response(jsonify({"message": "Logout thành công"}))
    
    # Xóa cookie
    response.set_cookie('access_token_cookie', '', expires=0, httponly=True)
    response.set_cookie('refresh_token_cookie', '', expires=0, httponly=True, path='/auth/refresh')

    try:
        # Xử lý Blacklist Access Token
        if access_token:
            decoded_acc = decode_token(access_token)
            # Dùng .get() để tránh lỗi nếu không có jti
            jti_acc = decoded_acc.get("jti") or access_token[-10:] 
            exp_acc = datetime.fromtimestamp(decoded_acc["exp"])
            
            acc_blacklist = TokenBlacklist(
                token=access_token, # Lưu ý độ dài
                expired_at=exp_acc
            )
            db.session.add(acc_blacklist)
            print("DEBUG: Added Access Token to Session")

        # Xử lý Blacklist Refresh Token
        if refresh_token:
            decoded_ref = decode_token(refresh_token)
            exp_ref = datetime.fromtimestamp(decoded_ref["exp"])
            
            ref_blacklist = TokenBlacklist(
                token=refresh_token,
                expired_at=exp_ref
            )
            db.session.add(ref_blacklist)
            print("DEBUG: Added Refresh Token to Session")

        # Commit DB
        db.session.commit()
        print("DEBUG: Commit to DB Successful!")

    except Exception as e:
        db.session.rollback() # Rollback nếu lỗi
        print(f"🔴 LỖI CRITICAL KHI BLACKLIST: {str(e)}")
        # Không return lỗi cho user, nhưng phải in ra console để dev biết

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