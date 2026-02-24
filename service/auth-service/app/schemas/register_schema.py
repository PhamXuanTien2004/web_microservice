from marshmallow import Schema, fields, validate, ValidationError


class RegisterSchema(Schema):
    """
    Validate dữ liệu đầu vào cho endpoint POST /api/auth/register.

    Marshmallow tự động:
        - Kiểm tra field bắt buộc (required)
        - Kiểm tra kiểu dữ liệu (String)
        - Kiểm tra độ dài (Length)
        - Trả về lỗi rõ ràng nếu invalid

    Cách dùng trong controller:
        schema = RegisterSchema()
        errors = schema.validate(request.get_json())
        if errors:
            return {'success': False, 'errors': errors}, 400

        data = schema.load(request.get_json())
        username = data['username']
        password = data['password']
    """

    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=50, error="Username phải từ 3 đến 50 ký tự."),
            validate.Regexp(
                r"^[a-zA-Z0-9_.-]+$",
                error="Username chỉ được chứa chữ cái, số và các ký tự _ . -",
            ),
        ],
    )

    email = fields.Email(
        required=True, # bắt buộc phải có email
        validate=validate.Length(max=100),
        error_messages={
            "required": "Email là bắt buộc.",
            "invalid": "Email không đúng định dạng.",
        },
    )

    password = fields.String(
        required=True,
        validate=validate.Length(min=8, error="Password phải có ít nhất 8 ký tự."),
        load_only=True,  # không trả về password trong response
    )

    phone = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Regexp(
            r"^(?:\+84|0)(3|5|7|8|9)\d{8}$",
            error="Số điện thoại không hợp lệ.",
        ),
        load_default=None,
    )
    
    def validate_password_strength(self, password: str) -> None:
        """Kiểm tra độ mạnh của password."""
        errors = []
        if not any(c.islower() for c in password):
            errors.append("Phải có ít nhất một chữ cái thường.")
        if not any(c.isupper() for c in password):
            errors.append("Phải có ít nhất một chữ cái hoa.")
        if not any(c.isdigit() for c in password):
            errors.append("Phải có ít nhất một chữ số.")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for c in password):
            errors.append("Phải có ít nhất một ký tự đặc biệt.")
        if errors:
            raise ValidationError(" ".join(errors))