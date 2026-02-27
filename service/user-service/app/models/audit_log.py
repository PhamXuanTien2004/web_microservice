from datetime import datetime  
from app.extensions import db  


class AuditLog(db.Model):
    """
    Ghi lại mọi thay đổi do user thực hiện.
    
    Dùng để:
    - Admin xem ai đã làm gì, khi nào, từ đâu
    - Debug khi có vấn đề ("Ai đã xóa sensor X?")
    - Compliance (tuân thủ quy định) - audit trail
    - Security monitoring - phát hiện hành vi bất thường
    
    Ví dụ log entry:
        User admin (IP 192.168.1.10) đã UPDATE_PROFILE của user john_doe
        từ email old@x.com → new@x.com lúc 10:30 AM
    """
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # User thực hiện hành động
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Loại hành động
    # Ví dụ: "UPDATE_PROFILE", "CHANGE_PASSWORD", "DELETE_ACCOUNT", "CREATE_SENSOR"
    action = db.Column(db.String(100), nullable=False, index=True)
    
    # Loại tài nguyên bị ảnh hưởng
    # Ví dụ: "user", "sensor", "alert", "notification"
    resource_type = db.Column(db.String(50), nullable=True)
    
    # ID của tài nguyên bị ảnh hưởng
    # Ví dụ: user_id=5, sensor_id=10
    resource_id = db.Column(db.Integer, nullable=True)
    
    # Địa chỉ IP của user khi thực hiện hành động
    # Support IPv4 (15 chars) và IPv6 (45 chars)
    ip_address = db.Column(db.String(45), nullable=True)
    
    # User agent (trình duyệt, thiết bị)
    # Ví dụ: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    user_agent = db.Column(db.Text, nullable=True)
    
    # Chi tiết về thay đổi (JSON)
    # Ví dụ: {"email": {"old": "old@x.com", "new": "new@x.com"}}
    details = db.Column(db.JSON, nullable=True)
    
    # Thời gian hành động được thực hiện
    created_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow,
        nullable=False,
        index=True  # Index để query theo thời gian nhanh hơn
    )
    
    # ──────────────────────────────────────────────
    # INSTANCE METHODS
    # ──────────────────────────────────────────────
    
    # ← FIX Issue 16: Added to_dict() method
    def to_dict(self) -> dict:
        """
        Convert AuditLog object → dict để trả về JSON.
        
        Returns:
            {
                "id": 123,
                "user_id": 1,
                "action": "UPDATE_PROFILE",
                "resource_type": "user",
                "resource_id": 5,
                "ip_address": "192.168.1.10",
                "user_agent": "Mozilla/5.0...",
                "details": {"email": {"old": "...", "new": "..."}},
                "created_at": "2025-02-12T10:30:00Z"
            }
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "details": self.details,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None
        }
    
    def __repr__(self):
        return f"<AuditLog id={self.id} user={self.user_id} action={self.action}>"