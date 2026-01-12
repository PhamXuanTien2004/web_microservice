from marshmallow import Schema, fields, validate, validates_schema, ValidationError
import re

class RegisterSchema(Schema):

    username = fields.Str(
        required=True, 
        validate=validate.Length(min=3, max=50),
        error_messages={"required": "Username không được để trống"}
    )
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8),
        error_messages={"required": "Password không được để trống"}
    )
    created_at = fields.DateTime(
        required=False
    )

    @validates_schema
    def validate_register_data(self, data, **kwargs):
        errors = {}
        # Validate password
        password = data.get("password")
        if password:
            pwd_errors = []

            if not re.search(r"[A-Z]", password):
                pwd_errors.append("Password phải có ít nhất 1 chữ hoa")
            if not re.search(r"[a-z]", password):
                pwd_errors.append("Password phải có ít nhất 1 chữ thường")
            if not re.search(r"\d", password):
                pwd_errors.append("Password phải có ít nhất 1 số")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;/']", password):
                pwd_errors.append("Password phải có ít nhất 1 ký tự đặc biệt")

            if pwd_errors:
                errors["password"] = pwd_errors

        if errors:
            raise ValidationError(errors)
