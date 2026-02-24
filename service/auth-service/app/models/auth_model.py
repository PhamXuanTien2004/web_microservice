from datetime import datetime, timedelta, timezone
from app.extensions import db
import bcrypt


class User(db.Model):
    """
    Đại diện cho bảng `users` trong database.
    Dùng SQLAlchemy ORM — không cần viết raw SQL.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(
        db.Enum("user", "admin", name="user_role"),
        nullable=False,
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=7), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=7), 
        onupdate=lambda: datetime.now(timezone.utc) + timedelta(hours=7),
        nullable=False,
    )

    # Relationship: 1 user có nhiều refresh tokens
    refresh_tokens = db.relationship(
        "TokenBlacklist", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    # ──────────────────────────────────────────────
    # CLASS METHODS
    # ──────────────────────────────────────────────

    @classmethod
    def find_by_username(cls, username: str):
        """Tìm user theo username. Trả về User object hoặc None."""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str):
        """Tìm user theo email. Trả về User object hoặc None."""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, user_id: int):
        """Tìm user theo id. Trả về User object hoặc None."""
        return cls.query.get(user_id)

    # ──────────────────────────────────────────────
    # INSTANCE METHODS
    # ──────────────────────────────────────────────

    def set_password(self, plain_password: str) -> None:
        """
        Hash password và lưu vào password_hash.
        Gọi khi tạo user hoặc đổi password.

        Ví dụ:
            user = User(username='john')
            user.set_password('Password123!')
            db.session.add(user)
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        """
        Kiểm tra password nhập vào có khớp với hash không.
        Trả về True nếu đúng, False nếu sai.

        Ví dụ:
            user.check_password('Password123!')  → True
            user.check_password('WrongPass')     → False
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                self.password_hash.encode("utf-8"),
            )
        except Exception:
            return False

    def to_dict(self) -> dict:
        """
        Chuyển User object → dict để trả về JSON response.
        KHÔNG include password_hash vì lý do bảo mật.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"