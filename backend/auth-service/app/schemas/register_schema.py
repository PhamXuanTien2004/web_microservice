# backend\auth-service\app\schemas\register_schema.py
from marshmallow import Schema, fields, validate, validates_schema, ValidationError
import re

# 1. Định nghĩa Schema con cho Profile (để validate kỹ cả bên trong)
class ProfileInputSchema(Schema):
    # Khai báo các trường bạn mong muốn nhận
    name = fields.Str(
        required=True, 
        error_messages={"required": "Name không được để trống"}
    )

    email = fields.Email(
        required=True, 
        error_messages={
            "required": "Email không được để trống", 
            "invalid": "Email không đúng định dạng"
        }
    )

    telphone = fields.Str(
        required=True, 
        validate=validate.Regexp(
            r"(84|0[3|5|7|8|9])+([0-9]{8})\b", 
            error="Số điện thoại không hợp lệ"
        ),
        error_messages={"required": "Telephone không được để trống"}
    )

    role = fields.Str(
        load_default="user",  
        validate=validate.OneOf(
            choices=["user", "admin"], 
            error="Role chỉ được phép là 'user' hoặc 'admin'"
        )
    )

    sensors = fields.Integer(load_default=1, allow_none=True)
    
    topic = fields.String(allow_none=True)


    
    # Cho phép nhận thêm các trường khác nếu cần (tùy chọn)
    class Meta:
        unknown = 'EXCLUDE'

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
    created_at = fields.DateTime(required=False)

    profile = fields.Nested(ProfileInputSchema, required=True, error_messages={"required": "Thông tin profile là bắt buộc"})
    
    @validates_schema
    def validate_register_data(self, data, **kwargs):
        errors = {}
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