import requests
from datetime import datetime
from flask import current_app
from app.services.token_service import decode_token
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from app import db

from app.models.auth_model import Auths 
from app.models.token_blacklist import TokenBlacklist

class AuthService:

    @staticmethod
    def register_user(data: dict) -> Auths:
        """
        data: dict đã được validate bởi RegisterSchema
        """
        # 1. Kiểm tra trùng username
        if Auths.query.filter_by(username=data["username"]).first():
            raise ValidationError({
                "username": ["Username đã tồn tại"]
            })

        # Lấy phần profile tách riêng
        profile_data = data.get('profile', {})

        # Mapping thủ công các trường quan trọng từ cấp ngoài cùng vào profile_data
        # Lưu ý: frontend dùng 'telphone' nên map đúng tên trường
        fields_to_map = ['email', 'name', 'telphone', 'role']
        for field in fields_to_map:
            if field in data and field not in profile_data:
                profile_data[field] = data[field]
        
        # 2. Tạo User bên Auth Service
        new_auth = Auths(username=data["username"])
        new_auth.set_password(data["password"])

        try:
            # Thêm vào session và flush để lấy id mà chưa commit
            db.session.add(new_auth)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            raise ValidationError({"error": ["Dữ liệu Username đã tồn tại trong hệ thống."]})
        except Exception as e:
            db.session.rollback()
            raise e

        # 3. Gọi Service User để lưu thông tin Profile
        # --- QUAN TRỌNG: Bung toàn bộ dữ liệu profile vào payload ---
        profile_payload = {
            'user_id': new_auth.id,
            'username': new_auth.username,
            **profile_data 
        }
        # ---------------------------------------------------------------

        try:
            # Lấy URL từ config (đã sửa thành http://localhost:5002/api/user)
            user_service_url = current_app.config.get('USER_SERVICE_URL')
            
            # Ghép chuỗi URL: /api/user + /internal/users
            target_url = f"{user_service_url}/internal/users"
            
            # Gửi request POST
            response = requests.post(target_url, json=profile_payload, timeout=5)
            # Raise lỗi nếu User Service trả về 4xx hoặc 5xx
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            # --- Rollback: Undo session nếu User Service lỗi ---
            print(f"User Service failed: {e}. Rolling back Auth...") 
            db.session.rollback()
            
            # Cố gắng đọc lỗi chi tiết từ User Service gửi về
            error_msg = "Hệ thống đang bận, không thể tạo hồ sơ người dùng lúc này."
            if e.response is not None:
                try:
                    error_json = e.response.json()
                    if "errors" in error_json:
                        error_msg = error_json["errors"]
                    elif "error" in error_json:
                        error_msg = error_json["error"]
                except:
                    pass
            
            # Ném lỗi ra để Controller bắt
            raise Exception(error_msg)

        # Nếu tới đây không có exception nghĩa là User Service OK -> commit toàn bộ
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return new_auth

    @staticmethod
    def login_user(username: str, password: str) -> Auths:
        auth = Auths.query.filter_by(username=username).first()

        if not auth or not auth.check_password(password):
            raise ValidationError({
                "error": ["Sai username hoặc password"]
            })

        try:
            auth.is_active = True
            db.session.commit()   
        except Exception as e:
            db.session.rollback()
            raise e

        return auth

    @staticmethod
    def logout_user(access_token: str, refresh_token: str):
        try:
            if not access_token and not refresh_token:
                return False

            # Ensure tokens are str
            if isinstance(access_token, bytes):
                access_token = access_token.decode()
            if isinstance(refresh_token, bytes):
                refresh_token = refresh_token.decode()

            # 1. Xử lý Access Token
            if access_token:
                # Thêm allow_expired=True để vẫn lấy được data từ token cũ
                decoded_acc = decode_token(access_token, token_type=None, allow_expired=True)
                exp_acc = datetime.fromtimestamp(decoded_acc["exp"])
                
                # Kiểm tra xem token này đã có trong blacklist chưa để tránh lỗi IntegrityError
                if not TokenBlacklist.query.filter_by(token=access_token).first():
                    db.session.add(TokenBlacklist(token=access_token, expired_at=exp_acc))

                # Cập nhật trạng thái is_active = False
                user_id = decoded_acc.get("sub")
                auth = Auths.query.get(user_id)
                if auth:
                    auth.is_active = False

            # 2. Xử lý Refresh Token
            if refresh_token:
                decoded_ref = decode_token(refresh_token, token_type="refresh", allow_expired=True)
                exp_ref = datetime.fromtimestamp(decoded_ref["exp"])
                
                if not TokenBlacklist.query.filter_by(token=refresh_token).first():
                    db.session.add(TokenBlacklist(token=refresh_token, expired_at=exp_ref))

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            # Log lỗi chi tiết để debug
            print(f"🔴 Lỗi Logout: {str(e)}")
            return False