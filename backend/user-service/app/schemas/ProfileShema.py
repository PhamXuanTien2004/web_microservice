from marshmallow import Schema, fields, validate, validates_schema, ValidationError, pre_load
from app.models.user_model import Users
import re

class ProfileSchema(Schema):
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

    sensors = fields.Integer(
        load_default=1,  
        error_messages={"invalid": "Sensors lỗi type (phải là số nguyên)"}
    )

    @pre_load
    def process_null_values(self, data, **kwargs):
        """
        Chạy trước khi validation.
        Nếu client gửi {"role": null} -> đổi thành {"role": "user"}
        """
        # Xử lý Role
        if 'role' in data and data['role'] is None:
            data['role'] = 'user'
        
        # Xử lý Sensors
        if 'sensors' in data and data['sensors'] is None:
            data['sensors'] = 1
            
        return data

