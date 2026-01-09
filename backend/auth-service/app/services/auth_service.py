from app.models import Users
from app.models.user_model import UserRole
from app import db
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash


class AuthService:

    @staticmethod
    def register_user(data: dict) -> Users:
        """
        data: dict đã được validate bởi RegisterSchema
        """

        # Kiểm tra trùng username
        if Users.query.filter_by(username=data["username"]).first():
            raise ValidationError({
                "username": ["Username đã tồn tại"]
            })

        # Kiểm tra trùng email
        if Users.query.filter_by(email=data["email"]).first():
            raise ValidationError({
                "email": ["Email đã tồn tại"]
            })

        # Kiểm tra trùng telphone (nếu có)
        telphone = data.get("telphone")
        if telphone and Users.query.filter_by(telphone=telphone).first():
            raise ValidationError({
                "telphone": ["Telphone đã tồn tại"]
            })


        try:
            role_enum = UserRole(data["role"]) 
        except ValueError:
            # Phòng trường hợp data["role"] không map được vào Enum (dù Schema đã chặn)
            role_enum = UserRole.USER

        # Tạo user mới
        user = Users(
            name=data["name"],
            username=data["username"],
            email=data["email"],
            telphone=data.get("telphone"),
            role=role_enum,
            sensors=data.get("sensors", 1)
        )


        new_user = Users(
            name=data["name"],
            username=data["username"],
            email=data["email"],
            telphone=data.get("telphone"),
            role=role_enum,
            sensors=data.get("sensors", 1)
        )
        
        new_user.set_password(data["password"])

        # 3. Lưu vào DB với Try/Catch IntegrityError
        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except IntegrityError:
            db.session.rollback()
            # Lỗi này xảy ra khi có 2 request cùng lúc, hoặc check ở bước 1 bị sót
            raise ValidationError({"error": ["Dữ liệu (Username/Email/Phone) đã tồn tại trong hệ thống."]})
        except Exception as e:
            db.session.rollback()
            raise e

        return user

    @staticmethod
    def login_user(username: str, password: str) -> Users:
        user = Users.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            raise ValidationError({
                "error": ["Sai username hoặc password"]
            })

        return user
