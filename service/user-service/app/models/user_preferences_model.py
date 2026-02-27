from datetime import datetime, timezone, timedelta
from app.extensions import db


class UserPreferences(db.Model):
    """
    Lưu cài đặt cá nhân của user.
    
    Mỗi user có 1 record duy nhất trong bảng này.
    Relationship: 1 User - 1 UserPreferences
    """
    
    __tablename__ = "user_preferences"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to users table
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id'), 
        unique=True,  # Mỗi user chỉ có 1 preferences record
        nullable=False
    )
    
    # Alert settings - Có gửi notifications không?
    email_alerts = db.Column(db.Boolean, default=True, nullable=False)
    sms_alerts = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # ──────────────────────────────────────────────
    # CLASS METHODS
    # ──────────────────────────────────────────────
    
    @classmethod
    def find_by_user_id(cls, user_id: int):
        """
        Tìm preferences theo user_id.
        Trả về UserPreferences object hoặc None.
        
        Ví dụ:
            prefs = UserPreferences.find_by_user_id(1)
        """
        return cls.query.filter_by(user_id=user_id).first()
    
    @classmethod
    def get_or_create(cls, user_id: int):
        """
        Lấy preferences của user, tạo mới nếu chưa có.
        
        Returns:
            (preferences_object, is_created: bool)
        
        Ví dụ:
            prefs, created = UserPreferences.get_or_create(1)
            if created:
                print("Đã tạo preferences mới")
        """
        prefs = cls.find_by_user_id(user_id)
        
        if prefs:
            return prefs, False  # Đã tồn tại
        
        # Tạo mới với defaults
        prefs = cls(
            user_id=user_id,
            email_alerts=True,
            sms_alerts=False,
        )
        db.session.add(prefs)
        db.session.commit()
        
        return prefs, True  # Vừa tạo
    
    # ──────────────────────────────────────────────
    # INSTANCE METHODS
    # ──────────────────────────────────────────────
    
    def to_dict(self) -> dict:
        """
        Convert UserPreferences object → dict để trả về JSON.
        
        Returns:
            {
                "email_alerts": True,
                "sms_alerts": False,
                "updated_at": "2025-02-12T10:30:00Z"
            }
        """
        return {
            "email_alerts": self.email_alerts,
            "sms_alerts": self.sms_alerts, 
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<UserPreferences user_id={self.user_id} theme={self.theme}>"