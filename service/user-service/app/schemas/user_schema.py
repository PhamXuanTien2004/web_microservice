from marshmallow import Schema, fields, validate, ValidationError, validates

class UpdateProfileSchema(Schema):
    """Validate dữ liệu khi update profile."""
    email = fields.Email(required=False, validate=validate.Length(max=100))
    phone = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Regexp(
            r"^(?:\+84|0)(3|5|7|8|9)\d{8}$",
            error="Số điện thoại không hợp lệ.",
        ),
        load_default=None,
    )

class ChangePasswordSchema (Schema):
    """Vailidate khi đổi password"""

    old_password = fields.String(required=True, validate= validate.Length(min=8, max=128))
    new_password = fields.String(required = True, validate = validate.Length(min=8, max=128))
    @validate('new_password')
    def validate_new_password_strength(self, password: str) -> None:
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


class UserQuerySchema(Schema):
    """Validate query params khi list users."""
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))
    search = fields.String(required=False)
    role = fields.String(required=False, validate=validate.OneOf(["user", "admin"]))