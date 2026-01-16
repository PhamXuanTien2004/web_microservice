import requests
from datetime import datetime
from flask import current_app
from flask_jwt_extended import decode_token
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from app import db
# Import chính xác từ file model của bạn
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
        
        # 2. Tạo User bên Auth Service
        new_auth = Auths(username=data["username"])
        new_auth.set_password(data["password"])

        try:
            db.session.add(new_auth)
            db.session.commit()
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
            # --- Rollback: Xóa user bên Auth nếu bên User Service lỗi ---
            print(f"User Service failed: {e}. Rolling back Auth...") 
            
            db.session.delete(new_auth)
            db.session.commit()
            
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

        return new_auth

    @staticmethod
    def login_user(username: str, password: str) -> Auths:
        auth = Auths.query.filter_by(username=username).first()

        if not auth or not auth.check_password(password):
            raise ValidationError({
                "error": ["Sai username hoặc password"]
            })

        return auth

    @staticmethod
    def logout_user(access_token: str, refresh_token: str):
        """
        Chỉ chịu trách nhiệm đưa Token vào Blacklist (Database).
        Không xử lý Cookie hay Response ở đây.
        """
        try:
            # 1. Xử lý Access Token
            if access_token:
                try:
                    decoded_acc = decode_token(access_token)
                    exp_acc = datetime.fromtimestamp(decoded_acc["exp"])
                    acc_blacklist = TokenBlacklist(
                        token=access_token, 
                        expired_at=exp_acc
                    )
                    db.session.add(acc_blacklist)
                except Exception as e:
                    print(f"⚠️ Access Token invalid/expired, skip blacklist: {e}")

            # 2. Xử lý Refresh Token
            if refresh_token:
                try:
                    decoded_ref = decode_token(refresh_token, token_type="refresh") # Nhớ check type nếu cần
                    exp_ref = datetime.fromtimestamp(decoded_ref["exp"])
                    ref_blacklist = TokenBlacklist(
                        token=refresh_token,
                        expired_at=exp_ref
                    )
                    db.session.add(ref_blacklist)
                except Exception as e:
                     print(f"⚠️ Refresh Token invalid/expired, skip blacklist: {e}")

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"🔴 LỖI CRITICAL KHI BLACKLIST: {str(e)}")
            # Không raise lỗi ra ngoài để quy trình logout ở Controller vẫn tiếp tục xóa cookie
            return False