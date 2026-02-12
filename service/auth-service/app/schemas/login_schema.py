from marshmallow import Schema, fields, validate, ValidationError


class LoginSchema(Schema):
    """
    Validate dữ liệu đầu vào cho endpoint POST /api/auth/login.

    Marshmallow tự động:
        - Kiểm tra field bắt buộc (required)
        - Kiểm tra kiểu dữ liệu (String)
        - Kiểm tra độ dài (Length)
        - Trả về lỗi rõ ràng nếu invalid

    Cách dùng trong controller:
        schema = LoginSchema()
        errors = schema.validate(request.get_json())
        if errors:
            return {'success': False, 'errors': errors}, 400

        data = schema.load(request.get_json())
        username = data['username']
        password = data['password']
    """

    username = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={
            "required": "Username là bắt buộc.",
            "null": "Username không được để trống.",
            "validator_failed": "Username không hợp lệ.",
        },
    )

    password = fields.String(
        required=True,
        validate=validate.Length(min=1, max=128),
        error_messages={
            "required": "Password là bắt buộc.",
            "null": "Password không được để trống.",
        },
    )