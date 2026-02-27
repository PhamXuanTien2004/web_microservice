from datetime import datetime, timezone, timedelta
from sqlalchemy import or_
from flask import g  
from app.extensions import db
from app.models.user_model import User
from app.models.audit_log import AuditLog
from app.models.user_preferences_model import UserPreferences
from app.services.audit_service import AuditService 


class UserService:

    @staticmethod
    def get_user_profile(user_id: int) -> tuple:  
        """
        Lấy thông tin profile của user theo user_id.
        Trả về tuple (dict, status_code).

        Returns:
            tuple (result_dict, http_status_code)
            
        Ví dụ:
            result, status = UserService.get_user_profile(1)
            # result = {"success": True, "data": {"user": {...}}}
            # status = 200
        """
        # 1. Tìm user trong database bằng user_id
        user = User.find_by_id(user_id)
        
        if not user:
            return {
                "success": False,
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": "User không tồn tại."
                }
            }, 404  
        
        # 2. Trả về thông tin user
        return {
            "success": True,
            "data": {"user": user.to_dict()}
        }, 200  

    @staticmethod
    def update_user_profile(user_id: int, email: str = None, phone: str = None) -> tuple:
        """
        Cập nhật email và/hoặc phone của user.
        
        Validation:
            - Email mới phải unique (không trùng user khác)
            - Nếu không truyền email/phone thì giữ nguyên giá trị cũ
        
        Args:
            user_id: ID của user cần cập nhật
            email:   Email mới (optional)
            phone:   Phone mới (optional)
        
        Returns:
            tuple (result_dict, http_status_code)
        
        Ghi audit log:
            Ghi lại old values và new values để truy vết thay đổi
        """
        # Tìm user
        user = User.find_by_id(user_id)
        if not user:
            return {
                "success": False,
                "error": {
                    "code": "USER_NOT_FOUND", 
                    "message": "User không tồn tại."
                }
            }, 404
            
        # Lưu giá trị cũ để ghi vào audit log
        old_email = user.email
        old_phone = user.phone
        changes = {}  # Lưu sự thay đổi nếu có 

        # Kiểm tra email nếu được truyền vào
        if email is not None and email != old_email:
            findEmail = User.find_by_email(email)

            if findEmail and findEmail.id != user_id:
                return {
                    "success": False,
                    "error": {
                        "code": "DUPLICATE_EMAIL", 
                        "message": f"Email '{email}' đã tồn tại."
                    }
                }, 409

            # Cập nhật email
            user.email = email
            changes["email"] = {"old": old_email, "new": email}

        # Kiểm tra phone nếu được truyền vào
        if phone is not None and phone != old_phone: 
            user.phone = phone
            changes["phone"] = {"old": old_phone, "new": phone}
        
        # Nếu không có gì thay đổi
        if not changes:
            return {
                "success": True,
                "message": "Không có gì thay đổi",
                "data": {"user": user.to_dict()}
            }, 200
        
        # Lưu vào db
        try: 
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "Lỗi truy cập database"
                }
            }, 500
       
        # Ghi audit log
        AuditService.log(
            user_id=user_id,  # Người thực hiện thay đổi
            action="UPDATE_PROFILE",
            resource_type="user",
            resource_id=user_id,
            details=changes  # {"email": {"old": "...", "new": "..."}}
        )
        
        # Trả về kết quả
        return {
            "success": True,
            "message": "Cập nhật profile thành công.",
            "data": {"user": user.to_dict()}
        }, 200

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> tuple: 
        """
        Đổi password của user.
        
        Security flow:
            1. Verify old password đúng
            2. Validate new password đủ mạnh (đã check ở Schema)
            3. Đảm bảo new != old
            4. Hash new password
            5. Cập nhật password_hash
            6. (Optional) Blacklist tất cả tokens → buộc login lại
        
        Args:
            user_id:      ID của user
            old_password: Password hiện tại (để verify)
            new_password: Password mới
        
        Returns:
            tuple (result_dict, http_status_code)
        """
        # Tìm user
        user = User.find_by_id(user_id)
        if not user:
            return {
                "success": False,
                "error": {
                    "code": "USER_NOT_FOUND", 
                    "message": "User không tồn tại."
                }
            }, 404

        # Verify old password
        if not user.check_password(old_password):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_OLD_PASSWORD",
                    "message": "Password hiện tại không đúng"
                }
            }, 401  

        # Kiểm tra new password khác old password
        if old_password == new_password:
            return {
                "success": False,
                "error": {
                    "code": "PASSWORD_UNCHANGED",
                    "message": "Password mới phải khác Password cũ"
                }
            }, 400  

        # Hash và cập nhật password mới
        user.set_password(new_password)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR", 
                    "message": "Lỗi khi đổi password."
                }
            }, 500
            
        # Ghi audit log
        AuditService.log(
            user_id=user_id,
            action="CHANGE_PASSWORD",
            resource_type="user",
            resource_id=user_id,
            details={"note": "Password changed successfully"}
            # KHÔNG lưu password vào log (bảo mật!)
        )
        
        # (OPTIONAL - SECURITY) Blacklist tất cả tokens của user này
        # Buộc user phải đăng nhập lại ở tất cả thiết bị
        # Cần gọi API của Auth Service để blacklist tokens
        # hoặc set flag trong DB để Auth Service check
        
        # TODO: Implement token revocation
        # _revoke_all_user_tokens(user_id)

        # Trả về success
        return {
            "success": True,
            "message": "Đổi password thành công. Vui lòng đăng nhập lại."
        }, 200

    @staticmethod
    def list_users(page: int = 1, per_page: int = 20,
                   search: str = None, role: str = None) -> tuple:
        """
        Lấy danh sách users với phân trang và filter.
        
        ADMIN ONLY - Controller phải kiểm tra role trước khi gọi.
        
        Args:
            page:     Trang hiện tại (bắt đầu từ 1)
            per_page: Số users mỗi trang (max 100)
            search:   Tìm kiếm theo username hoặc email (optional)
            role:     Lọc theo role "user" hoặc "admin" (optional)
        
        Returns:
            tuple (result_dict, http_status_code)
        
        Ví dụ:
            # Trang 1, 20 users, tìm "john"
            list_users(page=1, per_page=20, search="john")
            
            # Trang 2, chỉ lấy admins
            list_users(page=2, role="admin")
        """
        # 1. Build query cơ bản
        query = User.query
        
        # 2. Apply search filter (nếu có)
        if search:
            # Tìm trong cả username VÀ email
            # %search% = contains (LIKE)
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            )
        
        # 3. Apply role filter (nếu có)
        if role:
            query = query.filter(User.role == role)
        
        # 4. Order by ID (mới nhất trước)
        query = query.order_by(User.id.desc())
        
        # 5. Paginate
        # Flask-SQLAlchemy có method .paginate() rất tiện
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False  # Không raise error nếu page > total_pages
        )
        
        # 6. Convert users sang dict
        users = [user.to_dict() for user in pagination.items]
        
        # 7. Trả về kết quả
        return {
            "success": True,
            "data": {
                "users": users,
                "pagination": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,      # Tổng số records
                    "pages": pagination.pages       # Tổng số trang
                }
            }
        }, 200

    @staticmethod
    def toggle_user_status(user_id: int, is_active: bool, 
                           current_user_id: int = None) -> tuple: 
        """
        Kích hoạt hoặc vô hiệu hóa user.
        
        ADMIN ONLY.
        
        Args:
            user_id:         ID của user cần thay đổi
            is_active:       True = kích hoạt, False = vô hiệu hóa
            current_user_id: ID của admin đang thực hiện (optional)
        
        Returns:
            tuple (result_dict, http_status_code)
        
        Side effects:
            Nếu is_active = False → nên blacklist tất cả tokens
            để user bị logout ngay lập tức.
        """
        # 1. Tìm user
        user = User.find_by_id(user_id)
        if not user:
            return {
                "success": False,
                "error": {"code": "USER_NOT_FOUND", "message": "User không tồn tại."}
            }, 404
        
        # 2. Kiểm tra trạng thái hiện tại
        if user.is_active == is_active:
            # Không có gì thay đổi
            return {
                "success": True,
                "message": f"User đã ở trạng thái {'active' if is_active else 'inactive'}.",
                "data": {"user": user.to_dict()}
            }, 200
        
        # 3. Cập nhật trạng thái
        old_status = user.is_active
        user.is_active = is_active
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "error": {"code": "DATABASE_ERROR", "message": "Lỗi khi cập nhật."}
            }, 500
        
        # 4. Ghi audit log
        action = "ACTIVATE_USER" if is_active else "DEACTIVATE_USER"
        
        log_user_id = current_user_id if current_user_id else user_id
        
        AuditService.log(
            user_id=log_user_id,  # Changed: use parameter
            action=action,
            resource_type="user",
            resource_id=user_id,
            details={
                "old_status": old_status,
                "new_status": is_active
            }
        )
        
        # 5. (OPTIONAL) Nếu vô hiệu hóa → blacklist tất cả tokens
        if not is_active:
            # TODO: Gọi Auth Service để revoke tokens
            # _revoke_all_user_tokens(user_id)
            pass
        
        # 6. Trả về
        status_text = "kích hoạt" if is_active else "vô hiệu hóa"
        return {
            "success": True,
            "message": f"Đã {status_text} user thành công.",
            "data": {"user": user.to_dict()}
        }, 200

    @staticmethod
    def delete_user(user_id: int, current_user_id: int = None) -> tuple:
        """
        Xóa user (soft delete).
        
        ADMIN ONLY.
        
        Thực chất chỉ set is_active = False,
        không xóa hẳn khỏi database.
        
        Args:
            user_id:         ID của user cần xóa
            current_user_id: ID của admin đang thực hiện
        
        Returns:
            tuple (result_dict, http_status_code)
        """
        # Gọi lại toggle_user_status với is_active = False
        return UserService.toggle_user_status(
            user_id=user_id, 
            is_active=False,
            current_user_id=current_user_id
        )