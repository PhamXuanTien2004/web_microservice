# backend\user-service\app\services\UserService.py

from app.models.user_model import Users
from app import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

class UserService:

    @staticmethod
    def create_user(data: dict) -> Users:
        try:
            user = Users(**data)

            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError as ie:
            db.session.rollback()
            # Trả về ValidationError để controller map thành 400
            raise ValidationError({"error": ["Dữ liệu trùng lặp hoặc không hợp lệ"]})
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def findUserById(user_id):
        return Users.query.get(user_id)