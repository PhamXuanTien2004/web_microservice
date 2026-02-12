from marshmallow import Schema, fields, validate, ValidationError


class RefreshSchema(Schema):
    """
    Validate dữ liệu đầu vào cho endpoint POST /api/auth/refresh.
    Thực ra JWT refresh token nằm trong header Authorization,
    schema này chỉ cần thiết nếu truyền qua body.
    """

    # Nếu truyền refresh_token qua body thay vì header:
    # refresh_token = fields.String(required=True)
    pass  # Token được đọc từ Authorization header bởi Flask-JWT-Extended
