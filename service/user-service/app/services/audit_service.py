from flask import request, has_request_context
import logging
from app.extensions import db
from app.models.audit_log import AuditLog
class AuditService:
    @staticmethod
    def log(user_id: int, action: str, resource_type: str = None,
            resoure_id: int = None, details: dict = None):
        
        """
        Ghi audit log.
        
        Được gọi sau mỗi hành động quan trọng để ghi lại lịch sử thay đổi.
        
        Args:
            user_id:       ID của user thực hiện hành động
            action:        Tên hành động (VD: "UPDATE_PROFILE", "CHANGE_PASSWORD")
            resource_type: Loại tài nguyên bị ảnh hưởng (VD: "user", "sensor", "alert")
            resource_id:   ID của tài nguyên bị ảnh hưởng
            details:       Chi tiết thay đổi dạng dict (VD: {"old": "...", "new": "..."})
        
        Ví dụ:
            AuditService.log(
                user_id=1,
                action="UPDATE_PROFILE",
                resource_type="user",
                resource_id=5,
                details={"field": "email", "old": "old@x.com", "new": "new@x.com"}
            )
        """
        
        # Khởi tại 2 giá trị ban đầu 
        ip_address = None
        user_agent = None

        # 1. Lấy IP và User-Agent từ request
        if has_request_context():
            user_agent = request.user_agent.string
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip_address:
                ip_address = ip_address.split(',')[0].strip()
        try:
            # 2. Tạo AuditLog record
            log_record = AuditLog(user_id, action, resource_type, resoure_id, ip_address, user_agent, details)
            
            db.session.add(log_record)

             # 3. Commit

            db.session.commit()
        except Exception as e:
            db.session.rollback()

            logging.error(f"Lỗi khi ghi Audit Log: {str(e)}")
    
    @staticmethod
    def get_logs (user_id: int = None, action: str = None,
                start_date = None, end_date = None,
                page: int = 1, per_page: int = 50) -> tuple:
        
        """
        Lấy audit logs với filter (ADMIN ONLY).
        
        Controller phải kiểm tra role admin trước khi gọi method này.
        
        Args:
            user_id:    Lọc theo user (optional) - None = lấy tất cả users
            action:     Lọc theo action (optional) - support LIKE search
            start_date: Từ ngày (datetime, optional)
            end_date:   Đến ngày (datetime, optional)
            page:       Trang hiện tại (bắt đầu từ 1)
            per_page:   Số logs mỗi trang (max 100)
        
        Returns:
            tuple (result_dict, http_status_code)
        
        Ví dụ:
            # Lấy tất cả logs của user 5
            get_logs(user_id=5)
            
            # Lấy logs UPDATE_PROFILE của tất cả users
            get_logs(action="UPDATE_PROFILE")
            
            # Lấy logs trong khoảng thời gian
            get_logs(start_date=datetime(2025, 2, 1), end_date=datetime(2025, 2, 28))
        """
        
        # 1. Build query với filters
        query = AuditLog.query

        if action:
            action_pattern = f"%{action}"
            query = query.filter(
                    AuditLog.action.ilike(action_pattern)
                )
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)

        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        query = query.order_by(AuditLog.user_id.desc())

        

        # 2. Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False  # Không raise error nếu page > total_pages
        )
        
        #Convert logs to dict

        logs = [log.to_dict() for log in pagination.iteams]

        # Trả về 
        return {
            "success": True,
            "data": {
                "logs": logs,
                "pagination": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages
                }
            }
        }, 200
        