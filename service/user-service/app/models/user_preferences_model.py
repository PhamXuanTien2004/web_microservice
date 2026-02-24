from datetime import datetime, timezone, timedelta
from app import db

class UserPreferences(db.Model):
    """
    Model lưu trữ các tùy chọn và cài đặt của user.
    Mỗi user sẽ có một bản ghi trong bảng này, liên kết qua user_id.

    Các trường có thể bao gồm:
    - user_id: khóa ngoại liên kết với bảng User
    - Phuong thức thông báo (email, SMS)
    """
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    # Các cài đặt tùy chọn của user để gửi cảnh báo, thông báo, v.v.
    email_alerts = db.Column(db.Boolean, default=True, nullable=False)
    sms_alerts = db.Column(db.Boolean, default=False, nullable=False)

    # Thời gian tạo và cập nhật bản ghi
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=7), nullable=False)
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=7), 
        onupdate=lambda: datetime.now(timezone.utc) + timedelta(hours=7), 
        nullable=False
    )