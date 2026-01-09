import jwt
from flask import current_app
from datetime import datetime
from jwt import ExpiredSignatureError, InvalidTokenError

def decode_token(token):
    """
    Giải mã và xác thực JWT
    Trả về payload nếu hợp lệ
    Ném exception nếu token không hợp lệ
    """

    try:
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        # Có thể kiểm tra thêm nếu muốn
        if payload.get("exp") < datetime.utcnow().timestamp():
            raise ExpiredSignatureError("Token expired")

        return payload

    except ExpiredSignatureError:
        raise Exception("Token has expired")

    except InvalidTokenError:
        raise Exception("Invalid token")
