from datetime import datetime
from app.extensions import db


class TokenBlacklist(db.Model):
    """
    Lưu các JWT token đã bị vô hiệu hóa (sau khi logout).

    Tại sao cần?
        JWT là stateless — server không "biết" token đang dùng.
        Khi user logout, access token vẫn valid đến khi hết hạn.
        → Blacklist giải quyết: mỗi request kiểm tra jti có bị blacklist không.

    jti (JWT ID) là unique ID của mỗi token, nằm trong payload.
    """

    __tablename__ = "token_blacklist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(36), unique=True, nullable=False, index=True)  # UUID
    token_type = db.Column(
        db.Enum("access", "refresh", name="token_type"),
        nullable=False,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ──────────────────────────────────────────────
    # CLASS METHODS
    # ──────────────────────────────────────────────

    @classmethod
    def is_blacklisted(cls, jti: str) -> bool:
        """
        Kiểm tra jti có trong blacklist không.
        Dùng bởi middleware để block các token đã bị logout.

        Ví dụ:
            TokenBlacklist.is_blacklisted("abc-123")  → True/False
        """
        token = cls.query.filter_by(jti=jti).first()
        return token is not None

    @classmethod
    def add(cls, jti: str, token_type: str, user_id: int, expires_at: datetime):
        """
        Thêm token vào blacklist.
        Gọi khi user logout hoặc revoke token.

        Ví dụ:
            TokenBlacklist.add(
                jti="abc-123",
                token_type="access",
                user_id=1,
                expires_at=datetime(2025, 2, 20)
            )
        """
        entry = cls(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires_at,
        )
        db.session.add(entry)
        db.session.commit()

    @classmethod
    def cleanup_expired(cls) -> int:
        """
        Xóa các token đã hết hạn khỏi blacklist (tiết kiệm dung lượng DB).
        Gọi định kỳ bằng cron job hoặc Celery task.

        Trả về số lượng records đã xóa.
        """
        now = datetime.utcnow()
        deleted = cls.query.filter(cls.expires_at < now).delete()
        db.session.commit()
        return deleted

    def __repr__(self):
        return f"<TokenBlacklist jti={self.jti} type={self.token_type}>"