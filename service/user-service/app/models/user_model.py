from datetime import datetime 
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
    
    # Lưu UTC trong database, convert khi cần hiển thị
    created_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow,  
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,  
        onupdate=datetime.utcnow,  
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

    def to_dict(self) -> dict:
        """
        Chuyển User object → dict để trả về JSON response.
        KHÔNG include password_hash vì lý do bảo mật.
        
        Note: created_at được lưu ở UTC trong DB.
        Nếu cần convert sang timezone khác (VD: Asia/Ho_Chi_Minh),
        có thể thêm logic ở đây hoặc để frontend xử lý.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
            # "Z" = UTC timezone indicator (ISO 8601)
        }

    @classmethod
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

    @classmethod
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

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ──────────────────────────────────────────────────────────────────
# BONUS: Helper function để convert UTC → timezone cụ thể (optional)
# ──────────────────────────────────────────────────────────────────

def convert_utc_to_timezone(utc_datetime, timezone_str='Asia/Ho_Chi_Minh'):
    """
    Convert UTC datetime sang timezone cụ thể.
    
    Args:
        utc_datetime: datetime object (UTC)
        timezone_str: Timezone string (default: Asia/Ho_Chi_Minh)
    
    Returns:
        datetime object đã convert
    
    Ví dụ:
        utc_time = datetime.utcnow()
        vn_time = convert_utc_to_timezone(utc_time, 'Asia/Ho_Chi_Minh')
    """
    try:
        import pytz
        utc = pytz.UTC
        target_tz = pytz.timezone(timezone_str)
        
        # Đảm bảo datetime là UTC-aware
        if utc_datetime.tzinfo is None:
            utc_datetime = utc.localize(utc_datetime)
        
        # Convert sang target timezone
        return utc_datetime.astimezone(target_tz)
    except ImportError:
        # Nếu không có pytz, fallback to manual offset
        from datetime import timedelta
        return utc_datetime + timedelta(hours=7)  # VN = UTC+7


