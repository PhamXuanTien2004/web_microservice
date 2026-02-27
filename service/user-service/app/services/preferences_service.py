from app.models.user_model import User
from app.models.user_preferences_model import UserPreferences
from app.extensions import db

class PreferencesService:
    @staticmethod
    def get_perferences(user_id: int) -> tuple:
        """
        Đưa ra những setting của user theo user_id

        Returns:
            tuple (result_dict, status_code)
        """

        # Tìm user_id trong db
        pref = UserPreferences.find_by_id(user_id)

        # Đưa ra thông báo nếu không có user_id
        if not pref:
            pref = UserPreferences(
                user_id = user_id,
                email_alerts = True,
                sms_alerts = False
            )
            db.session.add(pref)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return {
                    "success": False,
                    "error": {
                        "code": "DATABASE_ERROR",
                        "message": "Lỗi khi tạo preferences"
                    }
                }, 500
        
        # Trả về thông tin user
        return {
            "success": True,
            "data": {"pref": pref.to_dict()}
        }, 200  

    @staticmethod
    def update_perferences (user_id: int, **kwargs) -> tuple:
        """
        Cập nhật preferences của user.

        Chỉ update các fields được truyền vào,
        giữ nguyên các fields không được truyền.

        Args:
            user_id: ID của user
            **kwargs: Các fields cần update
                - email_alerts: bool
                - sms_alerts: bool

        Returns:
            tuple (result_dict, http_status_code)
        """
        # Tìm user_id trong db
        prefs = UserPreferences.find_by_user_id(user_id)

        if not prefs:
            UserPreferences(
                user_id = user_id,
                email_alerts = True,
                sms_alerts = False
            )
            db.session.add(prefs)
        
        changes = {}

        # List cacs field cos theer update
        allowed_fields = ['email_alerts', 'sms_alerts']

        for field, value in kwargs.items():
            # Chỉ update nếu fields đó hợp lệ và tồn tại trong model
            if field in allowed_fields and hasattr(prefs, field):
                is_valid, error_msg = PreferencesService.validate_preference_value(field, value)
                if not is_valid:
                    return {
                        "success": False,
                        "error": {"code": "INVALID_INPUT", "message": error_msg}
                    }, 400

                old_value = getattr(prefs, field)

                if old_value != value:
                    setattr(prefs, field, value)
                    changes[field] = {"old": old_value, "new": value}
        
        if not changes:
            return {
                "success": True,
                "message": "Không có gì thay đổi",
                "data": {
                    "preferences": prefs.to_dict()
                }
            }, 200

        # Commit changes vào db 
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return {
                    "success": False,
                    "error": {
                        "code": "DATABASE_ERROR",
                        "message": "Lỗi khi tạo preferences"
                    }
                }, 500
        # Ghi audit log
        AuditService.log(
                    user_id=user_id,
                    action="UPDATE_PREFERENCES",
                    resource_type="user_preferences",
                    resource_id=prefs.id,
                    details=changes
                )
        
        # Trả về kết quả
        return {
            "success": True,
            "message": "Cập nhật preferences thành công.",
            "data": {
                "preferences": prefs.to_dict()
            }
        }, 200
    
    def validate_preference_value(field: str, value) -> tuple:
        """
        Validate giá trị của preference field.
        
        Args:
            field: Tên field
            value: Giá trị cần validate
        
        Returns:
            (is_valid: bool, error_message: str)
        
        Ví dụ:
            valid, error = validate_preference_value("theme", "dark")
            # → (True, None)
            
            valid, error = validate_preference_value("theme", "red")
            # → (False, "theme chỉ được là 'light' hoặc 'dark'")
        """
        validations = {
            "email_alerts": lambda v: isinstance(v, bool),
            "sms_alerts": lambda v: isinstance(v, bool),
        }
        
        error_messages = {
            "email_alerts": "email_alerts phải là boolean (True/False)",
            "sms_alerts": "sms_alerts phải là boolean (True/False)",
        }
        
        if field not in validations:
            return False, f"Field '{field}' không hợp lệ"
        
        if validations[field](value):
            return True, None
        else:
            return False, error_messages[field]
            
            



        

