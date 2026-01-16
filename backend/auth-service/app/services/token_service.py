# app/services/token_service.py
import jwt
from datetime import datetime, timedelta
from flask import current_app
from jwt import ExpiredSignatureError, InvalidTokenError

def generate_access_token(user):
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(
            minutes=current_app.config["JWT_ACCESS_EXPIRES"]
        )
    }

    return jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    
def generate_refresh_token(user):
    payload = {
        "sub": str(user.id),  
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(
            days=current_app.config["JWT_REFRESH_EXPIRES"]
        )
    }

    return jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

def decode_token(token, token_type=None):
    try:
        # Lấy key từ config (Sửa từ SECRET_KEY thành JWT_SECRET_KEY nếu bạn dùng Flask-JWT)
        secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("SECRET_KEY")
        
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"]
        )

        if token_type and payload.get("type") != token_type:
            raise Exception("Invalid token type")

        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token đã hết hạn")
    except jwt.InvalidTokenError:
        raise Exception("Chữ ký Token không hợp lệ")
        