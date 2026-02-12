from datetime import datetime, timezone
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.token_blacklist import TokenBlacklist
from app.extensions import db


class TokenService:
    """
    Xử lý toàn bộ logic liên quan đến JWT tokens.

    Tách riêng khỏi AuthService để:
        - Single Responsibility: mỗi service 1 nhiệm vụ
        - Reusability: TokenService có thể dùng ở nhiều nơi
        - Testability: test logic token độc lập

    Các chức năng:
        - Tạo access token + refresh token
        - Decode token để lấy thông tin
        - Blacklist token khi logout
        - Kiểm tra token có bị blacklist không
    """

    @staticmethod
    def create_tokens(user) -> dict:
        """
        Tạo cặp access token + refresh token cho user.

        Access token:
            - Thời hạn: 1 giờ (config JWT_ACCESS_TOKEN_EXPIRES)
            - Chứa: user_id, username, role, email
            - Dùng để: xác thực mỗi API request

        Refresh token:
            - Thời hạn: 7 ngày (config JWT_REFRESH_TOKEN_EXPIRES)
            - Chứa: user_id
            - Dùng để: tạo access token mới khi hết hạn

        Args:
            user: User object từ database

        Returns:
            {
                "access_token": "eyJ...",
                "refresh_token": "eyJ...",
                "token_type": "Bearer",
                "expires_in": 3600
            }

        Ví dụ:
            tokens = TokenService.create_tokens(user)
            return jsonify({'data': tokens}), 200
        """
        # Claims nhúng trong token — client có thể đọc nhưng không sửa được
        additional_claims = {
            "username": user.username,
            "role": user.role,
            "email": user.email,
        }

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims,
        )

        refresh_token = create_refresh_token(
            identity=str(user.id),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,  # seconds
        }

    @staticmethod
    def create_new_access_token(user) -> dict:
        """
        Tạo access token mới (dùng khi refresh).
        Chỉ tạo access token, KHÔNG tạo refresh token mới.

        Args:
            user: User object

        Returns:
            {"access_token": "eyJ...", "expires_in": 3600}
        """
        additional_claims = {
            "username": user.username,
            "role": user.role,
            "email": user.email,
        }

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims,
        )

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    @staticmethod
    def blacklist_token(jti: str, token_type: str, user_id: int, expires_at: datetime):
        """
        Thêm token vào blacklist (vô hiệu hóa token).

        Gọi khi:
            - User logout → blacklist cả access + refresh token
            - Admin revoke token của user

        Args:
            jti:        JWT ID (unique identifier của token)
            token_type: "access" hoặc "refresh"
            user_id:    ID của user sở hữu token
            expires_at: Thời điểm token hết hạn (để cleanup sau)

        Ví dụ (trong logout):
            decoded = TokenService.decode_token(access_token)
            TokenService.blacklist_token(
                jti=decoded['jti'],
                token_type='access',
                user_id=current_user_id,
                expires_at=datetime.fromtimestamp(decoded['exp'])
            )
        """
        TokenBlacklist.add(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires_at,
        )

    @staticmethod
    def is_token_blacklisted(jti: str) -> bool:
        """
        Kiểm tra token có trong blacklist không.
        Gọi bởi middleware trước mỗi request.

        Args:
            jti: JWT ID cần kiểm tra

        Returns:
            True nếu đã bị blacklist, False nếu còn hợp lệ
        """
        return TokenBlacklist.is_blacklisted(jti)

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode JWT token để lấy payload (jti, exp, user_id...).
        Dùng khi cần blacklist token khi logout.

        Args:
            token: JWT token string ("eyJ...")

        Returns:
            {
                "sub": "1",        ← user_id
                "jti": "abc-123",  ← unique token ID
                "exp": 1707654321, ← expiry timestamp
                "type": "access",
                "username": "admin",
                "role": "admin"
            }

        Raises:
            Exception nếu token invalid hoặc expired
        """
        return decode_token(token)

    @staticmethod
    def get_expiry_from_decoded(decoded: dict) -> datetime:
        """
        Lấy expiry datetime từ decoded token payload.

        Args:
            decoded: dict từ decode_token()

        Returns:
            datetime object của thời điểm hết hạn
        """
        exp_timestamp = decoded.get("exp")
        return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc).replace(
            tzinfo=None
        )