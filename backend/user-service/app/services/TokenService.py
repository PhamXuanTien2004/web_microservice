import jwt
from datetime import datetime, timedelta
from flask import current_app
from jwt import ExpiredSignatureError, InvalidTokenError

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