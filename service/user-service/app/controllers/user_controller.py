##### 📄 `app/controllers/user_controller.py`
"""
**Các endpoints cần implement:**

```
┌─────────────────────────────────────────────────────────────────┐
│ PROFILE CÁ NHÂN (User thường và Admin)                         │
└─────────────────────────────────────────────────────────────────┘
GET    /api/users/me                  Xem profile của chính mình
PUT    /api/users/me                  Cập nhật profile (email, phone)
POST   /api/users/me/change-password  Đổi password

┌─────────────────────────────────────────────────────────────────┐
│ QUẢN LÝ USERS (Admin only)                                      │
└─────────────────────────────────────────────────────────────────┘
GET    /api/users                     Danh sách users (phân trang)
GET    /api/users/:id                 Chi tiết 1 user
PUT    /api/users/:id                 Cập nhật user khác
PATCH  /api/users/:id/status          Kích hoạt/khóa user
DELETE /api/users/:id                 Xóa user

┌─────────────────────────────────────────────────────────────────┐
│ AUDIT LOGS (Admin only)                                         │
└─────────────────────────────────────────────────────────────────┘
GET    /api/users/audit-logs          Xem logs
```
"""
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from datetime import datetime
from app.extensions import db
from app.schemas import PreferencesSchema, UpdateProfileSchema, UserQuerySchema, ChangePasswordSchema
from app.middleware.auth_middleware import requires_auth
from app.middleware.role_middleware import require_role
from app.services import UserService, PreferencesService, AuditService

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

# Khởi tạo schemas
update_profile_schema = UpdateProfileSchema()
change_password_schema = ChangePasswordSchema()
user_query_schema = UserQuerySchema()

# ─────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────
@user_bp.get("/health")
def health():
    """Kiểm tra service có đang chạy không. Dùng bởi Docker healthcheck."""
    return jsonify({"status": "ok", "service": "auth-service"}), 200

# ─────────────────────────────────────────────────────────────
# XEM THÔNG TIN CÁ NHÂN - USER
# ─────────────────────────────────────────────────────────────
@user_bp.get("/me")
@requires_auth
def getMyProfile():
    """
    User xem profile của chính mình.
    
    Request:
        GET /api/users/me
        Headers: Authorization: Bearer <token>
    
    Response 200 - Hiển thị thành công
        {
            "success": true,
            "data": {
                "user": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "phone": "+84901234567",
                    "role": "user",
                    "is_active": true,
                    "created_at": "2025-02-12T10:00:00Z"
                }
            }
        }



    Response 404 - Không thấy user (đã có tại user_service)

    Response 401 - Chưa đăng nhập (đã có tại auth_middleware)

    Response 500 - Internal Server Error
    """

    user_id = g.curren_user_id

    result, status_code = UserService.get_user_profile(user_id= user_id)

    return jsonify(result), status_code

# ─────────────────────────────────────────────────────────────
# Update Email/Phone - USER
# ─────────────────────────────────────────────────────────────
@user_bp.put("/me")
@requires_auth
def updateMyProfile():
    """
    User cập nhật profile của mình.
    
    Request:
        PUT /api/users/me
        Headers: Authorization: Bearer <token>
        Body: {
            "email": "newemail@example.com",  // optional
            "phone": "+84912345678"           // optional
        }
    
    Response 200:
        {
            "success": true,
            "message": "Cập nhật profile thành công.",
            "data": {"user": {...}}
        }
    
    Response 400: Validation error
    Response 409: Email đã tồn tại
    """

    # Đọc body
    data = request.get_json(silent= True)

    if not data:
        return jsonify({
            "success": False,
            "error": {
                "code": "MISSING_DATA", 
                "message": "Request data trống."
                
        }}), 400

    # validate input - email/phone
    errors = update_profile_schema.validate(data)

    if errors: 
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu không hợp lệ.",
                "details": errors,  # {'username': ['...'], 'email': ['...']}
            },
        }), 400
    
    # Load validate data
    validated_data = update_profile_schema.load(data)

    # Lấy user_id 
    user_id = g.current_user_id

    # Gọi service xử lý logic
    result, status_code = UserService.update_user_profile(
        user_id= user_id,
        email= validated_data.get("email"),
        phone= validated_data.get("phone")
    )

    return jsonify(result), status_code
# ─────────────────────────────────────────────────────────────
# ĐỔI PASSWORD - USER
# ─────────────────────────────────────────────────────────────
@user_bp.post("/me/change-password")
@requires_auth
def changePassword():
    """
    User đổi password của mình.
    
    Request:
        POST /api/users/me/change-password
        Headers: Authorization: Bearer <token>
        Body: {
            "old_password": "OldPass123!",
            "new_password": "NewPass456!"
        }
    
    Response 200:
        {
            "success": true,
            "message": "Đổi password thành công. Vui lòng đăng nhập lại."
        }
    
    Response 400: Validation error (password yếu, thiếu field)
    Response 401: Old password sai
    """
    # Đọc body
    data = request.get_json(silent= True)

    if not data:
        return jsonify({
            "success": False,
            "error": {
                "code": "MISSING_DATA", 
                "message": "Request data trống."
                
        }}), 400

    # Validate input
    errors = change_password_schema.validate(data)
    if errors:
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu không hợp lệ.",
                "details": errors,
            }
        }), 400

    # Load validate data
    data = change_password_schema.load(data=data)

    # Lấy user_id
    user_id = g.current_user_id

    # Gọi service 
    result, status_code = UserService.change_password(
        user_id= user_id,
        old_password= data.get("old_password"),
        new_password= data.get("new_password")
    )

    return jsonify(result), status_code

# ─────────────────────────────────────────────────────────────
# LIST USERS - ADMIN
# ─────────────────────────────────────────────────────────────

@user_bp.get("/list-users")
@requires_auth
@require_role("admin")
def listUsers():
    """
    Admin xem danh sách users.
    
    Request:
        GET /api/users?page=1&per_page=20&search=john&role=user
        Headers: Authorization: Bearer <admin_token>
    
    Query Params:
        - page: Trang hiện tại (default: 1)
        - per_page: Số users mỗi trang (default: 20, max: 100)
        - search: Tìm trong username hoặc email (optional)
        - role: Lọc theo role "user" hoặc "admin" (optional)
    
    Response 200:
        {
            "success": true,
            "data": {
                "users": [{...}, {...}],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 150,
                    "pages": 8
                }
            }
        }
    """

    # Đọc query params từ URL
    # request.args là dict của query params
    # Ví dụ: /api/users?page=2 → request.args = {"page": "2"}

    # Validate query params 
    erros = user_query_schema.validate(request.args)
    if errors: 
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu không hợp lệ.",
                "details": errors,  
            },
        }), 400

    # Validate input
    params = user_query_schema.validate(request.args)

    # Gọi service 
    result, status_code = UserService.list_users(
        page= params["page"],
        per_page= params["per_page"],
        search= params.get("search"),
        role= params.get("role")
    )

    return jsonify(result), status_code

# ─────────────────────────────────────────────────────────────
#   XEM CHI TIẾT 1 USER - ADMIN
# ─────────────────────────────────────────────────────────────
@user_bp.get("/<int:user_id>")
@require_role
def getUserDetail(user_id):
    """
    Xem chi tiết 1 user.
    
    Phân quyền:
        - User thường: Chỉ xem chính mình (user_id == current_user_id)
        - Admin: Xem bất kỳ ai
    
    Request:
        GET /api/users/5
        Headers: Authorization: Bearer <token>
    
    Response 200: {"success": true, "data": {"user": {...}}}
    Response 403: Không có quyền xem user khác
    Response 404: User không tồn tại
    """

    # Lấy thông tin từ middleware
    current_user_id = g.current_user_id
    current_user_role = g.current_user_role

    # Check quyền
    # Admin: xem tất cả
    # User thường: chỉ xem chính mình

    if current_user_id != user_id and current_user_role == "user":
        return jsonify({
            "success": False,
            "error":{
                "code": "FORBIDDEN",
                "message": "Bạn không có quyền xem thông tin người khác."
            }
        }), 403
    
    result, status_code = UserService.get_user_profile(user_id= user_id)

    return jsonify(result), status_code

# ─────────────────────────────────────────────────────────────
# ADMIN Update Email/Phone - ADMIN
# ─────────────────────────────────────────────────────────────
@user_bp.put("/<int:user_id>")
@require_auth
@require_role("admin")  
def update_user(user_id):
    """
    Admin cập nhật thông tin user khác.
    
    Request:
        PUT /api/users/5
        Headers: Authorization: Bearer <admin_token>
        Body: {"email": "newemail@example.com", "phone": "..."}
    
    Response 200: Cập nhật thành công
    Response 400: Validation error
    Response 404: User không tồn tại
    Response 409: Email trùng
    """
    # Read data
    data = request.get_json(silent= True)

    if not data:
        return jsonify({
            "success": False,
            "error": {
                "code": "MISSING_DATA", 
                "message": "Request data trống."
                
        }}), 400

    # Validate input 
    errors = update_profile_schema.validate(data)
    if errors:
        return jsonify({
            "success": False,
            "error": {"code": "VALIDATION_ERROR", "details": errors}
        }), 400
    
    # Load validate data

    validate_data = update_profile_schema.load(user_id)

    # Call service
    result, status_code = UserService.update_user_profile(
        user_id= user_id,
        email= validated_data.get("email"),
        phone= validated_data.get("phone")
    )

    return jsonify(result), status_code

@user_bp.patch("/<int:user_id>/status")
@require_auth
@require_role("admin")
def toggleUserStatus(user_id):
    """
    Admin kích hoạt hoặc vô hiệu hóa user.
    
    Use cases:
        - Khóa tài khoản vi phạm
        - Mở khóa tài khoản
        - Tạm ngưng tài khoản
    
    Request:
        PATCH /api/users/5/status
        Headers: Authorization: Bearer <admin_token>
        Body: {
            "is_active": false  // true để kích hoạt, false để khóa
        }
    
    Response 200:
        {
            "success": true,
            "message": "Đã vô hiệu hóa user thành công.",
            "data": {"user": {...}}
        }
    
    Response 400: is_active không phải boolean
    Response 403: Không phải admin
    Response 404: User không tồn tại
    """
    # Đọc body
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success": False,
            "error": {
                "code": "MISSING_BODY",
                "message": "Request body trống."
            }
        }), 400

    # Get is_active
    is_active = data.get("is_active")

    # Validate is_active must boolean
    if not isinstance(is_active, bool):
        return jsonify({
            "success": False,
            "errors": {
                "code": "INVALID_INPUT",
                "message": "is_active phải là boolean."
            }
        }), 400

    result, status_code = UserService.toggle_user_status(
        user_id= user_id,
        is_active= is_active,
        current_user_id= g.current_user_id
    )

    return jsonify(result), status_code

# ─────────────────────────────────────────────────────────────
# DELETE USER - ADMIN
# ─────────────────────────────────────────────────────────────
@user_bp.delete("/<int:user_id>")
@requires_auth
@require_role("admin")
def deleteUser(user_id):
    """
    Admin xóa user (soft delete).
    
    Lưu ý:
        - Đây là soft delete: set is_active = false
        - Không xóa hẳn khỏi database để giữ audit logs
        - User bị xóa không thể login
    
    Request:
        DELETE /api/users/5
        Headers: Authorization: Bearer <admin_token>
    
    Response 200:
        {
            "success": true,
            "message": "Đã vô hiệu hóa user thành công.",
            "data": {"user": {...}}
        }
    
    Response 403: Không phải admin
    Response 404: User không tồn tại
    """
    result, status_code = UserService.delete_user(
        user_id= user_id,
        current_user_id= g.current_user_id
    )

    return jsonify(result), status_code

# ══════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ══════════════════════════════════════════════════════════════════

@user_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({
        "success": False,
        "error": {
            "code": "BAD_REQUEST",
            "message": str(error)
        }
    }), 400


@user_bp.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({
        "success": False,
        "error": {
            "code": "NOT_FOUND",
            "message": "Resource không tồn tại."
        }
    }), 404


@user_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    return jsonify({
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Lỗi server. Vui lòng thử lại sau."
        }
    }), 500
