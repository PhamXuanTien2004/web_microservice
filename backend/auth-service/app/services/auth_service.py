from app.models import Auths
from app import db
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash


class AuthService:

    @staticmethod
    def register_user(data: dict) -> Auths:
        """
        data: dict đã được validate bởi RegisterSchema
        """

        # Kiểm tra trùng username
        if Auths.query.filter_by(username=data["username"]).first():
            raise ValidationError({
                "username": ["Username đã tồn tại"]
            })

        # Tạo user mới
        auth = Auths(
            username=data["username"],
        )

        new_auth = Auths(
            username=data["username"]
        )
        
        new_auth.set_password(data["password"])

        # 3. Lưu vào DB với Try/Catch IntegrityError
        try:
            db.session.add(new_auth)
            db.session.commit()
            return new_auth
        except IntegrityError:
            db.session.rollback()
            # Lỗi này xảy ra khi có 2 request cùng lúc, hoặc check ở bước 1 bị sót
            raise ValidationError({"error": ["Dữ liệu Username đã tồn tại trong hệ thống."]})
        except Exception as e:
            db.session.rollback()
            raise e

        return auth

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
                    # Lưu ý: Token quá dài có thể gây lỗi DB nếu cột ngắn, nên dùng jti nếu có
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

            # 3. Commit một lần
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"🔴 LỖI CRITICAL KHI BLACKLIST: {str(e)}")
            # Không raise lỗi ra ngoài để quy trình logout ở Controller vẫn tiếp tục xóa cookie
            return False