from datetime import datetime, timezone, timedelta
from app import db

class AuditLog(db.Model):
    """
    Ghi lại mọi thay đổi do user thực hiện.
    
    Dùng để:
    - Admin xem ai đã làm gì
    - Debug khi có vấn đề
    - Compliance (tuân thủ quy định)
    """
    __tablename__ = "audit_logs"
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # Loại hành động (ví dụ: "UPDATE_PROFILE", "CHANGE_PASSWORD", "DELETE_ACCOUNT")
    action = db.Column(db.String(100))  # "UPDATE_PROFILE", "UPDATE_PREFERENCES"
    # Loại tài nguyên bị ảnh hưởng (ví dụ: "user", "sensor", "alert")
    resource_type = db.Column(db.String(50))  # "user", "sensor", "alert"
    # ID của tài nguyên bị ảnh hưởng (ví dụ: user_id, sensor_id)
    resource_id = db.Column(db.Integer)
    # Địa chỉ IP của user khi thực hiện hành động
    ip_address = db.Column(db.String(45))
    # User agent (trình duyệt, thiết bị) của user khi thực hiện hành động
    user_agent = db.Column(db.Text)
    # Chi tiết về thay đổi (có thể là JSON chứa dữ liệu cũ và mới)
    details = db.Column(db.JSON)  # Chi tiết thay đổi
    # Thời gian hành động được thực hiện
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=7))