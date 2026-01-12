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
