# backend\user-service\app\schemas\ProfileShema.py
from marshmallow import Schema, fields, validate, pre_load, EXCLUDE, ValidationError

class ProfileSchema(Schema):
    username = fields.Str(required=True)
    name = fields.Str(required=True, error_messages={"required": "Name không được để trống"})
    email = fields.Email(required=True, error_messages={"required": "Email không được để trống", "invalid": "Email không đúng định dạng"})
    
    telphone = fields.Str(
        required=True, 
        validate=validate.Regexp(
            r"^(0|84)(3|5|7|8|9|9)[0-9]{8}$", 
            error="Số điện thoại không hợp lệ"
        ),
        error_messages={"required": "Telephone không được để trống"}
    )

    role = fields.Str(
        load_default="user",  
        validate=validate.OneOf(choices=["user", "admin"], error="Role chỉ được phép là 'user' hoặc 'admin'")
    )

    sensors = fields.Integer(load_default=1, allow_none=True) 
    topic = fields.String(allow_none=True)

    class Meta:
        unknown = EXCLUDE 

    @pre_load
    def process_data(self, data, **kwargs):
        # 1. Chuẩn hóa chuỗi (giữ nguyên logic của bạn)
        for key in ['role', 'email', 'username']:
            if key in data and isinstance(data[key], str):
                data[key] = data[key].strip().lower()

        role = data.get('role') or 'user'
        data['role'] = role

        # 3. Logic điều kiện đã sửa:
        if role == 'admin':
            data['sensors'] = None
            data['topic'] = None
        else:
            # Nếu là user mà thiếu sensors thì mới gán mặc định
            if data.get('sensors') is None:
                data['sensors'] = 1
            # Bạn có thể thêm yêu cầu topic bắt buộc cho user tại đây
        return data