from marshmallow import Schema, fields, validate, validates_schema, ValidationError
import re

class RegisterSchema(Schema):
    name = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "Name không được để trống"}
    )
    username = fields.Str(
        required=True, 
        validate=validate.Length(min=3, max=50),
        error_messages={"required": "Username không được để trống"},
    )
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8),
        error_messages={"required": "Password không được để trống"}
    )
    email = fields.Email(
        required=True,
        error_messages={"required": "Email không được để trống"}
    )
    telphone = fields.Str(
        required=False, 
        validate=validate.Length(10),
        error_messages={"length": "Telphone phải có đúng 10 ký tự"}
    )
    sensors = fields.Int(
        required=False,
        load_default=1,
        validate=validate.Range(min=1),
        error_messages={"invalid": "Sensors phải là số nguyên lớn hơn hoặc bằng 1"}
    )
    role = fields.Str(
        required=False,
        load_default="user",
        validate=validate.OneOf(["user", "admin"]),
        error_messages={"invalid": "Role phải là 'user' hoặc 'admin'"}
    )
    
    created_at = fields.DateTime(
        required=False
    )

    @validates_schema
    def validate_register_data(self, data, **kwargs):
        errors = {}
        
        #Validate telphone
        telphone = data.get("telphone")
        if telphone:
            tel_errors = []
            if not re.fullmatch(r"0\d{9}", telphone):
                tel_errors.append("Telphone phải bắt đầu bằng số 0 và gồm 10 chữ số")

            if tel_errors:
                errors["telphone"] = tel_errors

        # Validate role
        role = data.get("role", "user")
        if role not in ["user", "admin"]:
            errors["role"] = ["Role không hợp lệ"]
        
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
