"""
auth_controller.py
──────────────────
Xử lý HTTP requests liên quan đến authentication.

Vai trò: Controller CHỈ làm 3 việc:
    1. Đọc dữ liệu từ request (JSON body, headers)
    2. Validate input dùng Schema
    3. Gọi Service để xử lý logic
    4. Trả về JSON response

Controller KHÔNG chứa business logic (để trong Service).
Controller KHÔNG query database trực tiếp (để trong Model/Service).

Endpoints:
    POST /api/auth/register         Đăng ký tài khoản mới (chỉ dành cho admin)
    POST /api/auth/login            Đăng nhập
    POST /api/auth/logout           Đăng xuất
    POST /api/auth/refresh          Làm mới access token
    GET  /api/auth/me               Lấy thông tin user hiện tại
    POST /api/auth/validate-token   Validate token (dùng bởi API Gateway)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from app.schemas import LoginSchema, RegisterSchema, RefreshSchema
from app.services.auth_service import AuthService
from app.services.token_service import TokenService
from app.extensions import db
from datetime import datetime
from typing import Optional
from app.middleware.role_middleware import require_role

# Blueprint nhóm tất cả routes auth dưới prefix /api/auth
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Schema instances — tái sử dụng, không tạo mới mỗi request
login_schema = LoginSchema()
register_schema = RegisterSchema()


# ─────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────

@auth_bp.get("/health")
def health():
    """Kiểm tra service có đang chạy không. Dùng bởi Docker healthcheck."""
    return jsonify({"status": "ok", "service": "auth-service"}), 200


# ─────────────────────────────────────────────────────────────
# ĐĂNG KÝ
# ─────────────────────────────────────────────────────────────

@auth_bp.post("/register")
@jwt_required()
@require_role("admin")
def register():
    """
    Đăng ký tài khoản mới.

    Request body:
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "Password123!",
            "phone": "+84901234567"   (optional)
        }

    Response 201:
        {
            "success": true,
            "message": "Đăng ký thành công.",
            "data": { "user": { id, username, email, role } }
        }

    Response 400 (validation error):
        {
            "success": false,
            "error": { "code": "VALIDATION_ERROR", "details": {...} }
        }
    Response 403 (insufficient role):
        {
            "success": false,
            "error": { "code": "INSUFFICIENT_ROLE", "message": "Bạn không có quyền truy cập tài nguyên này." }
        }
    Response 409 (duplicate):
        {
            "success": false,
            "error": { "code": "DUPLICATE_USERNAME", "message": "..." }
        }
    """
    body = request.get_json(silent=True)

    # Validate input
    errors = register_schema.validate(body or {})
    if errors:
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu không hợp lệ.",
                "details": errors,  # {'username': ['...'], 'email': ['...']}
            },
        }), 400

    data = register_schema.load(body)

    # Gọi service xử lý logic
    result, status_code = AuthService.register(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        phone=data.get("phone"),
    )

    return jsonify(result), status_code


# ─────────────────────────────────────────────────────────────
# ĐĂNG NHẬP
# ─────────────────────────────────────────────────────────────

@auth_bp.post("/login")
def login():
    """
    Đăng nhập và nhận JWT tokens.

    Request body:
        {
            "username": "admin",
            "password": "Password123!"
        }

    Response 200:
        {
            "success": true,
            "data": {
                "access_token": "eyJ...",
                "refresh_token": "eyJ...",
                "token_type": "Bearer",
                "expires_in": 3600,
                "user": { id, username, email, role }
            }
        }

    Response 400: validation error
    Response 401: sai credentials
    Response 403: tài khoản bị khóa
    """
    body = request.get_json(silent=True)

    # Validate input
    errors = login_schema.validate(body or {})
    if errors:
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu không hợp lệ.",
                "details": errors,
            },
        }), 400

    data = login_schema.load(body)

    # Gọi service xử lý login
    result, status_code = AuthService.login(
        username=data["username"],
        password=data["password"],
    )

    return jsonify(result), status_code


# ─────────────────────────────────────────────────────────────
# ĐĂNG XUẤT
# ─────────────────────────────────────────────────────────────

@auth_bp.post("/logout")
@jwt_required()
def logout():
    """
    Đăng xuất — blacklist cả access token và refresh token.

    Yêu cầu: Header Authorization: Bearer <access_token>

    Request body (optional, để blacklist refresh token ngay):
        {
            "refresh_token": "eyJ..."
        }

    Response 200:
        {
            "success": true,
            "message": "Đăng xuất thành công."
        }
    """
    # Lấy thông tin từ access token hiện tại
    current_user_id = get_jwt_identity()
    jwt_payload = get_jwt()
    access_jti = jwt_payload.get("jti")
    access_expires_at = TokenService.get_expiry_from_decoded(jwt_payload)

    # Lấy refresh token từ body (nếu client gửi kèm)
    refresh_jti = None
    refresh_expires_at = None

    body = request.get_json(silent=True)
    if body and body.get("refresh_token"):
        try:
            decoded_refresh = TokenService.decode_token(body["refresh_token"])
            refresh_jti = decoded_refresh.get("jti")
            refresh_expires_at = TokenService.get_expiry_from_decoded(decoded_refresh)
        except Exception:
            # Refresh token invalid — bỏ qua, vẫn logout access token
            pass

    # Gọi service xử lý logout
    result, status_code = AuthService.logout(
        access_token_jti=access_jti,
        refresh_token_jti=refresh_jti,
        user_id=int(current_user_id),
        access_expires_at=access_expires_at,
        refresh_expires_at=refresh_expires_at,
    )

    return jsonify(result), status_code


# ─────────────────────────────────────────────────────────────
# LÀM MỚI TOKEN
# ─────────────────────────────────────────────────────────────

@auth_bp.post("/refresh")
@jwt_required(refresh=True)  # Yêu cầu refresh token, không phải access token
def refresh():
    """
    Tạo access token mới từ refresh token.

    Yêu cầu: Header Authorization: Bearer <refresh_token>
             (Lưu ý: truyền REFRESH token, không phải access token)

    Response 200:
        {
            "success": true,
            "data": {
                "access_token": "eyJ...",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        }

    Response 401: refresh token hết hạn hoặc bị revoke
    """
    current_user_id = get_jwt_identity()
    jwt_payload = get_jwt()
    refresh_jti = jwt_payload.get("jti")
    refresh_expires_at = TokenService.get_expiry_from_decoded(jwt_payload)

    result, status_code = AuthService.refresh(
        user_id=current_user_id,
        refresh_token_jti=refresh_jti,
        refresh_expires_at=refresh_expires_at,
    )

    return jsonify(result), status_code


# ─────────────────────────────────────────────────────────────
# LẤY THÔNG TIN USER HIỆN TẠI
# ─────────────────────────────────────────────────────────────

@auth_bp.get("/me")
@jwt_required()
def get_me():
    """
    Lấy thông tin của user đang đăng nhập.

    Yêu cầu: Header Authorization: Bearer <access_token>

    Response 200:
        {
            "success": true,
            "data": {
                "user": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "phone": "+84901234567",
                    "role": "admin",
                    "is_active": true,
                    "created_at": "2025-02-12T10:00:00"
                }
            }
        }
    """
    current_user_id = get_jwt_identity()
    result, status_code = AuthService.get_me(user_id=current_user_id)
    return jsonify(result), status_code


# ─────────────────────────────────────────────────────────────
# VALIDATE TOKEN (INTERNAL — dùng bởi API Gateway)
# ─────────────────────────────────────────────────────────────

@auth_bp.post("/validate-token")
@jwt_required()
def validate_token():
    """
    Kiểm tra access token có hợp lệ không.
    INTERNAL endpoint — chỉ gọi từ API Gateway.

    Nếu request đến được đây thì token đã hợp lệ
    (Flask-JWT-Extended + middleware đã kiểm tra rồi).

    Response 200:
        {
            "success": true,
            "data": {
                "valid": true,
                "user_id": 1,
                "username": "admin",
                "role": "admin",
                "email": "admin@example.com"
            }
        }
    """
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    return jsonify({
        "success": True,
        "data": {
            "valid": True,
            "user_id": int(current_user_id),
            "username": claims.get("username"),
            "role": claims.get("role"),
            "email": claims.get("email"),
        },
    }), 200