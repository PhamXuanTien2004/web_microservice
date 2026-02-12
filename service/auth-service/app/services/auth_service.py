from app.models.auth_model import User
from app.services.token_service import TokenService
from app.extensions import db


class AuthService:
    """
    Xử lý business logic của authentication.

    AuthService biết về "việc gì cần làm":
        - Kiểm tra user tồn tại không
        - Kiểm tra password đúng không
        - User có bị inactive không
        - Gọi TokenService để tạo/hủy tokens

    Tách biệt với TokenService vì:
        - AuthService quan tâm đến USER (có tồn tại, có hợp lệ)
        - TokenService quan tâm đến TOKEN (tạo, hủy, kiểm tra)
    """

    @staticmethod
    def login(username: str, password: str) -> tuple:
        """
        Xử lý đăng nhập.

        Luồng:
            1. Tìm user theo username
            2. Kiểm tra user tồn tại
            3. Kiểm tra user active
            4. Kiểm tra password
            5. Tạo và trả về tokens

        Args:
            username: Tên đăng nhập
            password: Mật khẩu plain text

        Returns:
            tuple (result_dict, http_status_code)

            Success (200):
                {
                    "success": True,
                    "data": {
                        "access_token": "eyJ...",
                        "refresh_token": "eyJ...",
                        "token_type": "Bearer",
                        "expires_in": 3600,
                        "user": { id, username, email, role }
                    }
                }

            Failure (401):
                {
                    "success": False,
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "Sai username hoặc password."
                    }
                }
        """
        # 1. Tìm user theo username
        user = User.find_by_username(username)

        # 2. Kiểm tra user tồn tại
        #    Dùng thông báo mơ hồ → không tiết lộ username có tồn tại không
        if user is None:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Sai username ",
                },
            }, 401

        # 3. Kiểm tra user có bị vô hiệu hóa không
        if not user.is_active:
            return {
                "success": False,
                "error": {
                    "code": "ACCOUNT_DISABLED",
                    "message": "Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ admin.",
                },
            }, 403

        # 4. Kiểm tra password
        if not user.check_password(password):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Sai password.",
                },
            }, 401

        # 5. Tạo tokens
        tokens = TokenService.create_tokens(user)

        return {
            "success": True,
            "data": {
                **tokens,
                "user": user.to_dict(),
            },
        }, 200

    @staticmethod
    def logout(access_token_jti: str, refresh_token_jti: str,
               user_id: int, access_expires_at, refresh_expires_at) -> tuple:
        """
        Xử lý đăng xuất.

        Blacklist cả access token VÀ refresh token.
        Sau đó cả 2 token đều không dùng được nữa.

        Args:
            access_token_jti:   JTI của access token hiện tại
            refresh_token_jti:  JTI của refresh token (lấy từ request body)
            user_id:            ID của user đang logout
            access_expires_at:  Expiry datetime của access token
            refresh_expires_at: Expiry datetime của refresh token

        Returns:
            tuple (result_dict, http_status_code)
        """
        # Blacklist access token
        TokenService.blacklist_token(
            jti=access_token_jti,
            token_type="access",
            user_id=user_id,
            expires_at=access_expires_at,
        )

        # Blacklist refresh token (nếu được cung cấp)
        if refresh_token_jti:
            TokenService.blacklist_token(
                jti=refresh_token_jti,
                token_type="refresh",
                user_id=user_id,
                expires_at=refresh_expires_at,
            )

        return {"success": True, "message": "Đăng xuất thành công."}, 200

    @staticmethod
    def refresh(user_id: int, refresh_token_jti: str, refresh_expires_at) -> tuple:
        """
        Tạo access token mới từ refresh token.

        Luồng:
            1. Tìm user theo user_id
            2. Kiểm tra user còn active không
            3. Blacklist refresh token cũ (optional: rotate refresh token)
            4. Tạo và trả về access token mới

        Args:
            user_id:            ID của user (từ JWT identity)
            refresh_token_jti:  JTI của refresh token hiện tại
            refresh_expires_at: Expiry của refresh token

        Returns:
            tuple (result_dict, http_status_code)
        """
        # 1. Tìm user
        user = User.find_by_id(int(user_id))

        if user is None:
            return {
                "success": False,
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": "User không tồn tại.",
                },
            }, 404

        # 2. Kiểm tra user còn active (có thể bị disable sau khi lấy refresh token)
        if not user.is_active:
            return {
                "success": False,
                "error": {
                    "code": "ACCOUNT_DISABLED",
                    "message": "Tài khoản đã bị vô hiệu hóa.",
                },
            }, 403

        # 3. Tạo access token mới
        new_tokens = TokenService.create_new_access_token(user)

        return {"success": True, "data": new_tokens}, 200

    @staticmethod
    def register(username: str, email: str, password: str, phone: str = None) -> tuple:
        """
        Đăng ký tài khoản mới.

        Luồng:
            1. Kiểm tra username đã tồn tại chưa
            2. Kiểm tra email đã tồn tại chưa
            3. Tạo user mới với hashed password
            4. Lưu vào database
            5. Trả về thông tin user (không trả token — yêu cầu login)

        Args:
            username: Tên đăng nhập
            email:    Địa chỉ email
            password: Mật khẩu plain text (sẽ được hash)
            phone:    Số điện thoại (optional)

        Returns:
            tuple (result_dict, http_status_code)
        """
        # 1. Kiểm tra username
        if User.find_by_username(username):
            return {
                "success": False,
                "error": {
                    "code": "DUPLICATE_USERNAME",
                    "message": f"Username '{username}' đã được sử dụng.",
                },
            }, 409  # 409 Conflict

        # 2. Kiểm tra email
        if User.find_by_email(email):
            return {
                "success": False,
                "error": {
                    "code": "DUPLICATE_EMAIL",
                    "message": f"Email '{email}' đã được đăng ký.",
                },
            }, 409

        # 3. Tạo user mới
        user = User(
            username=username,
            email=email,
            phone=phone,
            role="user",
            is_active=True,
        )
        user.set_password(password)  # Hash password trước khi lưu

        # 4. Lưu vào database
        db.session.add(user)
        db.session.commit()

        # 5. Trả về thông tin user
        return {
            "success": True,
            "message": "Đăng ký thành công. Vui lòng đăng nhập.",
            "data": {"user": user.to_dict()},
        }, 201  # 201 Created

    @staticmethod
    def get_me(user_id: int) -> tuple:
        """
        Lấy thông tin user hiện tại từ token.

        Args:
            user_id: ID của user (từ JWT identity)

        Returns:
            tuple (result_dict, http_status_code)
        """
        user = User.find_by_id(int(user_id))

        if user is None:
            return {
                "success": False,
                "error": {"code": "USER_NOT_FOUND", "message": "User không tồn tại."},
            }, 404

        return {"success": True, "data": {"user": user.to_dict()}}, 200