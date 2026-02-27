"""
Preferences Controller - Xử lý HTTP requests liên quan đến cài đặt cá nhân

Endpoints:
    GET  /api/users/me/preferences   - Xem preferences của mình
    PUT  /api/users/me/preferences   - Cập nhật preferences
"""

from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError
from app.schemas.user_schema import PreferencesSchema
from app.services.preferences_service import PreferencesService
from app.middleware.auth_middleware import require_auth


# ══════════════════════════════════════════════════════════════════
# BLUEPRINT SETUP
# ══════════════════════════════════════════════════════════════════

# Prefix: /api/users/me/preferences
pref_bp = Blueprint("preferences", __name__, url_prefix="/api/users/me/preferences")


# ══════════════════════════════════════════════════════════════════
# SCHEMA INSTANCE
# ══════════════════════════════════════════════════════════════════

preferences_schema = PreferencesSchema()


# ══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════════

@pref_bp.get("")
@require_auth
def get_preferences():
    """
    User xem cài đặt của mình.
    
    Nếu chưa có preferences → tự động tạo với defaults.
    
    Request:
        GET /api/users/me/preferences
        Headers: Authorization: Bearer <token>
    
    Response 200:
        {
            "success": true,
            "data": {
                "preferences": {
                    "email_alerts": true,
                    "sms_alerts": false,
                    "theme": "light",
                    "language": "vi",
                    "timezone": "Asia/Ho_Chi_Minh",
                    "updated_at": "2025-02-12T10:30:00Z"
                }
            }
        }
    
    Response 500: Database error
    """
    # Lấy user_id từ g (đã set bởi @require_auth)
    user_id = g.current_user_id
    
    # Gọi service
    result, status = PreferencesService.get_preferences(user_id)
    
    # Trả về
    return jsonify(result), status


@pref_bp.put("")
@require_auth
def update_preferences():
    """
    User cập nhật cài đặt của mình.
    
    Chỉ update các fields được truyền vào.
    Các fields không truyền → giữ nguyên.
    
    Request:
        PUT /api/users/me/preferences
        Headers: Authorization: Bearer <token>
        Body: {
            "email_alerts": false,      // optional
            "sms_alerts": true,         // optional
            "theme": "dark",            // optional: "light" | "dark"
            "language": "en",           // optional: "vi" | "en"
            "timezone": "Asia/Bangkok"  // optional
        }
    
    Response 200:
        {
            "success": true,
            "message": "Cập nhật preferences thành công.",
            "data": {
                "preferences": {...}
            }
        }
    
    Response 400: Validation error
        - email_alerts không phải boolean
        - theme không phải "light"/"dark"
        - language không phải "vi"/"en"
    
    Response 500: Database error
    """
    # 1. Đọc body
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success": False,
            "error": {
                "code": "MISSING_BODY",
                "message": "Request body trống."
            }
        }), 400
    
    # 2. Validate
    errors = preferences_schema.validate(data)
    if errors:
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu không hợp lệ.",
                "details": errors
            }
        }), 400
    
    # 3. Load validated data
    validated_data = preferences_schema.load(data)
    
    # 4. Gọi service
    user_id = g.current_user_id
    result, status = PreferencesService.update_preferences(
        user_id=user_id,
        **validated_data  # Unpack all fields: email_alerts, sms_alerts, theme, ...
    )
    
    # 5. Trả về
    return jsonify(result), status


# ══════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ══════════════════════════════════════════════════════════════════

@pref_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({
        "success": False,
        "error": {
            "code": "BAD_REQUEST",
            "message": str(error)
        }
    }), 400


@pref_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    return jsonify({
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Lỗi server. Vui lòng thử lại sau."
        }
    }), 500


