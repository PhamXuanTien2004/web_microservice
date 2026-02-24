from datetime import datetime, timezone, timedelta
from app import db
from sqlalchemy import or_
from app.models.user_model import User
from app.models.audit_log import AuditLog
from app.models.user_preferences_model import UserPreferences
from flask import sqlalchemy
# from app.schemas.register_schema import RegisterSchema


class UserService:

    @staticmethod
    def get_user_profile(user_id: int) -> dict:
        """
        Lấy thông tin profile của user theo user_id.
        Trả về dict chứa thông tin user hoặc None nếu không tìm thấy.

        Ví dụ:
            {
                "id": 123,
                "username": "john_doe",
                "email": "john.doe@example.com",
                "phone": "0123456789",
                "role": "user",
                "is_active": True,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-10T15:30:00Z"
            }
        """
        # 1. Tìm user trong database bằng user_id
        user = User.find_by_id(user_id)
        if not user:
            return None  # Không tìm thấy user
        # 2. Trả về user.to_dict() 
        return user.to_dict()

    @staticmethod
    def update_user_profile(user_id: int, email: str = None, phone: str = None) -> dict:
        """
        Cập nhật thông tin profile của user.
        Chỉ cho phép cập nhật email, phone, và role 

        Đối tượng:
        - user: Cập nhật chính mình
        - admin: Cập nhật bất kỳ user nào

        Validate:
        - email phải có định dạng hợp lệ
        - phone phải có định dạng hợp lệ

         Trả về dict chứa thông tin user đã được cập nhật hoặc lỗi nếu có.

         Ví dụ:
            Input data:
            {
                "email": "john.doe@example.com",
                "phone": "0123456789",
            }
            Output data:
            {
                "id": 123,
                "username": "john_doe",
                "email": "john.doe@example.com",
                "phone": "0123456789",
                "role": "user", 
                "is_active": True,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-10T15:30:00Z"
            }
        """
        # 1. Tìm user
        user = User.find_by_id(user_id)
        if not user:
            return {"success": False, "error": "User không tồn tại."}
            
        # 2. Kiểm tra email, phone không trùng
        if email and email != user.email:
            if User.find_by_email(email):
                return {"success": False, "error": "Email đã được sử dụng."}
            user.email = email
        if phone and phone != user.phone:
            if User.find_by_phone(phone):
                return {"success": False, "error": "Số điện thoại đã được sử dụng."}
            user.phone = phone

        # 3. Cập nhật fields
        user.updated_at = datetime.now(timezone.utc) + timedelta(hours=7)

        # 4. Ghi audit log
        audit_log = AuditLog(
            user_id=user.id,
            action="update_profile",
            ip_address="",  # Lấy IP từ request context nếu cần
            user_agent="",  # Lấy user agent từ request context nếu cần
            # Có thể thêm details về những gì đã thay đổi nếu cần, ví dụ:
            # email đã thay đổi từ old_email sang new_email, phone đã thay đổi từ old_phone sang new_phone
            details={
                "email": {"old": user.email, "new": email} if email else None,
                "phone": {"old": user.phone, "new": phone} if phone else None,
            }
        )
        db.session.add(audit_log)
        
        # 5. Commit DB
        db.session.commit()

        # 6. Trả về user đã được cập nhật
        return user.to_dict()

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> dict:
        # 1. Validation nhanh (Nên làm trước khi đụng vào DB)
        if old_password == new_password:
            return {"success": False, "error": "Mật khẩu mới phải khác mật khẩu cũ."}
        
        # Giả sử RegisterSchema() là một class có phương thức static hoặc cần khởi tạo
        if not RegisterSchema().validate_password_strength(new_password):
            return {"success": False, "error": "Mật khẩu mới không đủ mạnh."}

        try:
            # 2. Kiểm tra User
            user = User.query.get(user_id) # Hoặc find_by_id tùy bạn define
            if not user:
                return {"success": False, "error": "User không tồn tại."}

            # 3. Xác thực mật khẩu cũ
            if not user.check_password(old_password):
                return {"success": False, "error": "Mật khẩu cũ không đúng."}

            # 4. Thực hiện thay đổi
            user.set_password(new_password)
            
            # 5. Ghi log (Tốt nhất nên lấy IP/User-Agent từ Request context của Flask/FastAPI)
            audit_log = AuditLog(
                user_id=user.id,
                action="change_password",
                details={"message": "Người dùng đã thay đổi mật khẩu thành công."}
            )
            db.session.add(audit_log)
            
            # 6. Commit một lần duy nhất cho tất cả thay đổi
            db.session.commit()

            # 7. Blacklist tất cả tokens hiện tại → bắt login lại
            

            return {"success": True, "message": "Đổi mật khẩu thành công."}

        except Exception as e:
            db.session.rollback() # Quan trọng: Trả lại trạng thái cũ nếu lỗi
            return {"success": False, "error": f"Lỗi hệ thống: {str(e)}"}

    @staticmethod
    def list_users(page: int = 1, per_page: int = 20, search: str = None) -> dict:
        """
        Danh sách users với phân trang và filter (ADMIN ONLY).
        
        Args:
            page: Trang hiện tại (1, 2, 3...)
            per_page: Số users mỗi trang
            search: Tìm theo username hoặc email
        
        Returns:
            {
                "success": True,
                "data": {
                    "users": [...],
                    "pagination": {
                        "page": 1,
                        "per_page": 20,
                        "total": 150,
                        "pages": 8
                    }
                }
            }
        """
        # 1. Khởi tạo query cơ bản, sắp xếp theo created_at giảm dần
        query = User.query.order_by(User.created_at.desc())

        # 2. Áp dụng filter nếu có tham số search (Case-insensitive)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_filter),
                    User.email.ilike(search_filter)
                )
            )

        # 3. Thực hiện phân trang (Sử dụng hàm paginate của Flask-SQLAlchemy)
        # error_out=False giúp trả về list rỗng thay vì lỗi 404 nếu page vượt quá giới hạn
        pagination_obj = query.paginate(page=page, per_page=per_page, error_out=False)

        # 4. Serialize dữ liệu (Giả sử bạn đã có UserSchema hoặc phương thức to_dict)
        users_data = [user.to_dict() for user in pagination_obj.items]

        # 5. Trả về cấu trúc theo yêu cầu
        return {
            "success": True,
            "data": {
                "users": users_data,
                "pagination": {
                    "page": pagination_obj.page,
                    "per_page": pagination_obj.per_page,
                    "total": pagination_obj.total,
                    "pages": pagination_obj.pages
                }
            }
        }