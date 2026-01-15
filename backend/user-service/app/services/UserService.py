from app.models.user_model import Users
from app import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

class UserService:

    @staticmethod
    def create_user(data: dict) -> Users:
        if Users.query.filter_by(email=data["email"]).first():
            raise ValidationError({
                "message": ["Email đã tồn tại"]
            })

        telphone = data.get("telphone")
        if telphone and Users.query.filter_by(telphone = telphone).first():
            raise ValidationError({
                "message": ["Telphone đã tồn tại"]
            })

        try: 
            user = Users(**data)

            db.session.add(user)
            db.session.commit()
            return user
        
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def findUserById(user_id):
        user = Users.query.get(user_id)
    
        if user:
            return user.to_json() # Trả về dữ liệu sạch (không password)
        return None