# backend\user-service\app\services\TokenService.py

import jwt
from datetime import datetime, timedelta
from flask import current_app
from jwt import ExpiredSignatureError, InvalidTokenError

def decode_token(token, token_type=None):
    # Không dùng try-except ở đây để decorator tự xử lý các loại lỗi cụ thể
    secret = current_app.config.get("SECRET_KEY")
    print(f"USER_SERVICE_KEY: {secret}")
    payload = jwt.decode(
        token,
        secret,
        algorithms=["HS256"]
    )

    if token_type and payload.get("type") != token_type:
        raise jwt.InvalidTokenError("Token type mismatch")

    return payload