"""
jwt_middleware.py
─────────────────
Đăng ký các callback cho Flask-JWT-Extended.

Vai trò: Tùy chỉnh hành vi của JWT — thay vì trả về
lỗi mặc định (HTML/generic), trả về JSON chuẩn của project.

Cách hoạt động:
    Flask-JWT-Extended gọi các callback này khi:
    - Token hết hạn (@jwt.expired_token_loader)
    - Token không hợp lệ (@jwt.invalid_token_loader)
    - Thiếu token trong header (@jwt.unauthorized_loader)
    - Cần kiểm tra token có bị revoke không (@jwt.token_in_blocklist_loader)
"""

from flask_jwt_extended import JWTManager
from app.services.token_service import TokenService


def register_jwt_callbacks(jwt: JWTManager):
    """
    Đăng ký tất cả JWT callbacks.
    Gọi trong create_app() sau khi init jwt.

    Args:
        jwt: JWTManager instance đã được init_app()
    """

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """
        Callback quan trọng nhất.

        Flask-JWT-Extended gọi hàm này TRƯỚC KHI xử lý request
        khi có @jwt_required() decorator.

        Nếu trả về True → JWT-Extended tự động từ chối request với 401.
        Nếu trả về False → Request tiếp tục vào controller.

        Flow:
            Request → Header "Authorization: Bearer eyJ..."
                → Flask-JWT-Extended decode token
                → Gọi hàm này với jti
                → True: chặn, False: tiếp tục
        """
        jti = jwt_payload.get("jti")
        return TokenService.is_token_blacklisted(jti)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Token hết hạn → 401 với thông báo rõ ràng."""
        return {
            "success": False,
            "error": {
                "code": "TOKEN_EXPIRED",
                "message": "Token đã hết hạn. Vui lòng đăng nhập lại.",
            },
        }, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        """Token sai format hoặc bị chỉnh sửa → 401."""
        return {
            "success": False,
            "error": {
                "code": "INVALID_TOKEN",
                "message": "Token không hợp lệ.",
            },
        }, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        """Thiếu Authorization header → 401."""
        return {
            "success": False,
            "error": {
                "code": "MISSING_TOKEN",
                "message": "Yêu cầu xác thực. Vui lòng đăng nhập.",
            },
        }, 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Token đã bị revoke (nằm trong blacklist) → 401."""
        return {
            "success": False,
            "error": {
                "code": "TOKEN_REVOKED",
                "message": "Token đã bị thu hồi. Vui lòng đăng nhập lại.",
            },
        }, 401