# app/services/token_service.py
import jwt
from datetime import datetime, timedelta
from flask import current_app
from jwt import ExpiredSignatureError, InvalidTokenError

def generate_access_token(user):
    payload = {
        "sub": str(user.id),
        "name": user.name,
        "username": user.username,
        "role": user.role.value,
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
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        if token_type and payload.get("type") != token_type:
            raise InvalidTokenError("Invalid token type")

        return payload
    except ExpiredSignatureError:
        raise ValueError("Token đã hết hạn")