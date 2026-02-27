# ROADMAP USER SERVICE - DANH SÁCH CÔNG VIỆC

## 🎯 TỔNG QUAN USER SERVICE

**User Service** quản lý thông tin người dùng SAU KHI đã đăng nhập thành công (Auth Service xử lý login/register).

**Phân biệt với Auth Service:**
- **Auth Service**: Đăng nhập, đăng ký, JWT tokens, xác thực
- **User Service**: Quản lý profile, cài đặt cá nhân, danh sách users, cập nhật thông tin

---

## 📋 DANH SÁCH CHỨC NĂNG CHÍNH

### 1. QUẢN LÝ PROFILE CÁ NHÂN (User thường)
- ✅ Xem thông tin của chính mình
- ✅ Cập nhật email, phone
- ✅ Đổi mật khẩu
- ✅ Quản lý cài đặt cá nhân (preferences):
  - Bật/tắt email alerts
  - Bật/tắt SMS alerts
  - Chọn theme (light/dark)
  - Chọn ngôn ngữ (vi/en)
  - Chọn timezone

### 2. QUẢN LÝ USERS (Admin)
- ✅ Xem danh sách tất cả users (có phân trang)
- ✅ Tìm kiếm user theo username/email
- ✅ Xem chi tiết 1 user bất kỳ
- ✅ Cập nhật thông tin user khác
- ✅ Kích hoạt/vô hiệu hóa tài khoản (is_active)
- ✅ Xóa user (soft delete)

### 3. AUDIT LOGS (Admin)
- ✅ Xem lịch sử thay đổi của user
- ✅ Lọc logs theo thời gian, user, hành động

---

## 🗂️ CẤU TRÚC THƯ MỤC USER SERVICE

```
services/user-service/
├── run.py                          # Entry point
├── config.py                       # Cấu hình (giống Auth)
├── requirements.txt                # Dependencies
├── Dockerfile                      # Docker build
└── app/
    ├── __init__.py                 # create_app() factory
    ├── extensions.py               # db instance
    ├── models/
    │   ├── __init__.py
    │   ├── user.py                 # User model (shared với Auth)
    │   ├── user_preferences.py     # UserPreferences model
    │   └── audit_log.py            # AuditLog model
    ├── schemas/
    │   ├── __init__.py
    │   ├── user_schema.py          # UpdateProfileSchema, UpdatePasswordSchema
    │   └── preferences_schema.py   # PreferencesSchema
    ├── services/
    │   ├── __init__.py
    │   ├── user_service.py         # Business logic cho user management
    │   ├── preferences_service.py  # Business logic cho preferences
    │   └── audit_service.py        # Ghi logs
    ├── middleware/
    │   ├── __init__.py
    │   ├── auth_middleware.py      # Gọi Auth Service để validate token
    │   └── role_middleware.py      # @require_role (copy từ Auth)
    └── controllers/
        ├── __init__.py
        ├── user_controller.py      # Endpoints cho users
        └── preferences_controller.py  # Endpoints cho preferences
```

---

## 🔧 CÔNG VIỆC CẦN LÀM - CHI TIẾT

### ══════════════════════════════════════════════════
### GIAI ĐOẠN 1: SETUP CƠ BẢN (1-2 ngày)
### ══════════════════════════════════════════════════

#### Task 1.1: Tạo cấu trúc project ⏱️ 30 phút

```bash
# Tạo thư mục
mkdir -p services/user-service/app/{models,schemas,services,middleware,controllers}

# Tạo các files cơ bản
touch services/user-service/run.py
touch services/user-service/config.py
touch services/user-service/requirements.txt
touch services/user-service/Dockerfile
touch services/user-service/app/__init__.py
touch services/user-service/app/extensions.py
```

**Giải thích:**
- Tạo cấu trúc thư mục giống Auth Service để dễ maintain
- Mỗi layer (models, services, controllers) có nhiệm vụ riêng

---

#### Task 1.2: Copy và chỉnh sửa config files ⏱️ 30 phút

**Files cần copy từ Auth Service:**
1. `config.py` → giữ nguyên
2. `requirements.txt` → giữ nguyên (cùng dependencies)
3. `Dockerfile` → đổi port 5001 → 5002
4. `app/extensions.py` → giữ nguyên

**Giải thích:**
- Config giống nhau vì cùng kết nối DB, JWT
- Chỉ khác port để phân biệt 2 services

---

#### Task 1.3: Tạo Models ⏱️ 2-3 giờ

##### 📄 `app/models/user.py`
**Copy từ Auth Service, BỎ các method liên quan auth:**

```python
# GIỮ LẠI:
- class User với các fields
- find_by_id()
- find_by_username()
- find_by_email()
- to_dict()

# BỎ ĐI (đã có trong Auth Service):
- set_password()
- check_password()
```

**Giải thích:**
- User Service KHÔNG xử lý password (Auth Service lo)
- Chỉ cần đọc/cập nhật thông tin user (email, phone, is_active)

---

##### 📄 `app/models/user_preferences.py` (MỚI)

```python
class UserPreferences(db.Model):
    """
    Lưu cài đặt cá nhân của user.
    
    Mỗi user có 1 record duy nhất trong bảng này.
    """
    __tablename__ = "user_preferences"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
    # Alert settings
    email_alerts = db.Column(db.Boolean, default=True)
    sms_alerts = db.Column(db.Boolean, default=False)
    
    # UI settings
    theme = db.Column(db.String(20), default='light')  # 'light' / 'dark'
    language = db.Column(db.String(10), default='vi')  # 'vi' / 'en'
    timezone = db.Column(db.String(50), default='Asia/Ho_Chi_Minh')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

**Giải thích:**
- **email_alerts**: Có gửi email khi sensor vượt ngưỡng không?
- **sms_alerts**: Có gửi SMS không? (tốn tiền hơn)
- **theme**: Giao diện sáng/tối
- **language**: Ngôn ngữ hiển thị
- **timezone**: Múi giờ để hiển thị đúng thời gian

---

##### 📄 `app/models/audit_log.py` (MỚI)

```python
class AuditLog(db.Model):
    """
    Ghi lại mọi thay đổi do user thực hiện.
    
    Dùng để:
    - Admin xem ai đã làm gì
    - Debug khi có vấn đề
    - Compliance (tuân thủ quy định)
    """
    __tablename__ = "audit_logs"
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100))  # "UPDATE_PROFILE", "UPDATE_PREFERENCES"
    resource_type = db.Column(db.String(50))  # "user", "sensor", "alert"
    resource_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    details = db.Column(db.JSON)  # Chi tiết thay đổi
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Giải thích:**
- Ví dụ audit log: "User admin (IP 192.168.1.10) đã cập nhật email của user john_doe từ old@example.com → new@example.com lúc 10:30 AM"
- **details**: JSON chứa before/after values

---

### ══════════════════════════════════════════════════
### GIAI ĐOẠN 2: MIDDLEWARE VÀ AUTH (1 ngày)
### ══════════════════════════════════════════════════

#### Task 2.1: Tạo Auth Middleware ⏱️ 2-3 giờ

##### 📄 `app/middleware/auth_middleware.py`

**Vấn đề cần giải quyết:**
- User Service KHÔNG có JWT secret key
- User Service KHÔNG tự verify token được
- Phải gọi Auth Service để verify

**Giải pháp:**

```python
import requests

def validate_token_with_auth_service(token: str) -> dict:
    """
    Gọi Auth Service endpoint POST /api/auth/validate-token
    để kiểm tra token có hợp lệ không.
    
    Returns:
        {
            "valid": True,
            "user_id": 1,
            "username": "admin",
            "role": "admin"
        }
    """
    try:
        response = requests.post(
            "http://auth-service:5001/api/auth/validate-token",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["data"]
        else:
            return None
    except Exception as e:
        print(f"Auth validation error: {e}")
        return None


def require_auth(fn):
    """
    Decorator thay thế @jwt_required() của Auth Service.
    
    User Service không có JWT secret, nên phải gọi Auth Service.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Đọc token từ header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": {"code": "MISSING_TOKEN", "message": "Thiếu token."}
            }), 401
        
        token = auth_header.split(" ")[1]
        
        # Validate với Auth Service
        user_info = validate_token_with_auth_service(token)
        if not user_info:
            return jsonify({
                "success": False,
                "error": {"code": "INVALID_TOKEN", "message": "Token không hợp lệ."}
            }), 401
        
        # Lưu user_info vào Flask g để controller dùng
        g.current_user_id = user_info["user_id"]
        g.current_user_role = user_info["role"]
        g.current_username = user_info["username"]
        
        return fn(*args, **kwargs)
    return wrapper
```

**Giải thích:**
- **Tại sao không dùng @jwt_required()?** Vì User Service không có JWT_SECRET_KEY. Nếu copy key sang thì vi phạm nguyên tắc bảo mật (chỉ Auth Service nên có key).
- **Flow**: Request → User Service → Gọi Auth Service validate → Auth Service trả user_id, role → User Service tiếp tục xử lý
- **Performance**: Mỗi request tốn thêm 1 HTTP call (~5-20ms). Có thể cache token 1-2 phút để giảm calls.

---

#### Task 2.2: Copy Role Middleware ⏱️ 15 phút

Copy `app/middleware/role_middleware.py` từ Auth Service, chỉnh sửa nhẹ:

```python
def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Đọc role từ Flask g (đã set bởi require_auth)
            user_role = g.get("current_user_role")
            
            if user_role not in roles:
                return jsonify({
                    "success": False,
                    "error": {"code": "FORBIDDEN", "message": "Không có quyền."}
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

**Sử dụng:**
```python
@user_bp.get("/users")
@require_auth              # Bước 1: Kiểm tra token
@require_role("admin")     # Bước 2: Kiểm tra role
def list_users():
    ...
```

---

### ══════════════════════════════════════════════════
### GIAI ĐOẠN 3: BUSINESS LOGIC - SERVICES (2-3 ngày)
### ══════════════════════════════════════════════════

#### Task 3.1: User Service ⏱️ 1 ngày

##### 📄 `app/services/user_service.py`

**Các method cần implement:**

```python
class UserService:
    
    @staticmethod
    def get_user_profile(user_id: int) -> tuple:
        """
        Lấy thông tin user (dùng bởi chính user hoặc admin).
        
        Returns:
            ({"success": True, "data": {"user": {...}}}, 200)
        """
        # 1. Tìm user
        # 2. Trả về user.to_dict()
    
    @staticmethod
    def update_profile(user_id: int, email: str = None, phone: str = None) -> tuple:
        """
        Cập nhật email/phone của user.
        
        Chỉ cho phép:
        - User cập nhật chính mình
        - Admin cập nhật bất kỳ ai
        
        Validation:
        - Email phải unique
        - Email đúng format
        """
        # 1. Tìm user
        # 2. Kiểm tra email không trùng
        # 3. Cập nhật fields
        # 4. Ghi audit log
        # 5. Commit DB
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> tuple:
        """
        Đổi mật khẩu.
        
        Validation:
        - old_password phải đúng
        - new_password đủ mạnh
        - new_password khác old_password
        """
        # 1. Verify old password
        # 2. Hash new password
        # 3. Cập nhật password_hash
        # 4. Ghi audit log
        # 5. (Optional) Blacklist tất cả tokens hiện tại → bắt login lại
    
    @staticmethod
    def list_users(page: int = 1, per_page: int = 20, 
                   search: str = None, role: str = None) -> tuple:
        """
        Danh sách users với phân trang và filter (ADMIN ONLY).
        
        Args:
            page: Trang hiện tại (1, 2, 3...)
            per_page: Số users mỗi trang
            search: Tìm theo username hoặc email
            role: Lọc theo role ("user" / "admin")
        
        Returns:
            {
                "success": True,
                "data": {
                    "users": [...],
                    "pagination": {
                        "page": 1,
                        "per_page": 20,
                        "total": 150,
                        "pages": 8
                    }
                }
            }
        """
        # 1. Build query với filter
        # 2. Paginate
        # 3. Trả về danh sách
    
    @staticmethod
    def toggle_user_status(user_id: int, is_active: bool) -> tuple:
        """
        Kích hoạt/vô hiệu hóa user (ADMIN ONLY).
        
        Dùng khi:
        - Khóa tài khoản vi phạm
        - Tạm ngưng tài khoản
        """
        # 1. Cập nhật is_active
        # 2. Ghi audit log
        # 3. Blacklist tất cả tokens nếu is_active = False
    
    @staticmethod
    def delete_user(user_id: int) -> tuple:
        """
        Xóa user (ADMIN ONLY).
        
        Soft delete: đánh dấu is_active = False, không xóa hẳn.
        """
        # Gọi toggle_user_status(user_id, False)
```

**Giải thích từng method:**

**get_user_profile:**
- User thường gọi để xem thông tin mình
- Admin gọi để xem thông tin user khác

**update_profile:**
- Chỉ cho phép đổi email, phone (KHÔNG đổi username, role)
- Email mới phải unique (không trùng user khác)
- Ghi audit log: "User X đã đổi email từ A → B"

**change_password:**
- Phải nhập đúng password cũ trước khi đổi
- Password mới validate (8+ ký tự, có chữ hoa, số...)
- Sau khi đổi password, nên blacklist tất cả tokens để bắt đăng nhập lại ở tất cả thiết bị (bảo mật)

**list_users:**
- PHÂN TRANG: page=1, per_page=20 → lấy users 1-20
- SEARCH: search="john" → tìm username hoặc email có chứa "john"
- FILTER: role="admin" → chỉ lấy admins

**toggle_user_status:**
- Admin khóa tài khoản vi phạm: `is_active = False`
- User bị khóa không thể login (Auth Service kiểm tra `is_active`)

---

#### Task 3.2: Preferences Service ⏱️ 4-5 giờ

##### 📄 `app/services/preferences_service.py`

```python
class PreferencesService:
    
    @staticmethod
    def get_preferences(user_id: int) -> tuple:
        """
        Lấy preferences của user.
        
        Nếu chưa có record → tự động tạo với default values.
        """
        # 1. Tìm user_preferences theo user_id
        # 2. Nếu không có → tạo mới với defaults
        # 3. Trả về
    
    @staticmethod
    def update_preferences(user_id: int, **kwargs) -> tuple:
        """
        Cập nhật preferences.
        
        Kwargs có thể gồm:
        - email_alerts: bool
        - sms_alerts: bool
        - theme: "light" / "dark"
        - language: "vi" / "en"
        - timezone: "Asia/Ho_Chi_Minh"
        """
        # 1. Lấy preferences hiện tại (hoặc tạo mới)
        # 2. Update từng field được truyền vào
        # 3. Validate (theme chỉ là light/dark, language chỉ vi/en)
        # 4. Commit
```

**Giải thích:**
- Preferences được tạo tự động khi user đăng ký (hoặc lazy create khi lần đầu truy cập)
- Frontend gọi API này khi user đổi settings trong UI

---

#### Task 3.3: Audit Service ⏱️ 2-3 giờ

##### 📄 `app/services/audit_service.py`

```python
class AuditService:
    
    @staticmethod
    def log(user_id: int, action: str, resource_type: str = None,
            resource_id: int = None, details: dict = None):
        """
        Ghi audit log.
        
        Ví dụ:
            AuditService.log(
                user_id=1,
                action="UPDATE_PROFILE",
                resource_type="user",
                resource_id=5,
                details={"field": "email", "old": "old@x.com", "new": "new@x.com"}
            )
        """
        # 1. Lấy IP và User-Agent từ request
        # 2. Tạo AuditLog record
        # 3. Commit
    
    @staticmethod
    def get_logs(user_id: int = None, action: str = None, 
                 start_date=None, end_date=None, 
                 page: int = 1, per_page: int = 50) -> tuple:
        """
        Lấy audit logs với filter (ADMIN ONLY).
        
        Dùng để:
        - Admin xem lịch sử thay đổi của 1 user
        - Debug vấn đề ("Ai đã xóa sensor X?")
        """
        # 1. Build query với filters
        # 2. Paginate
        # 3. Trả về
```

**Khi nào gọi `AuditService.log()`?**
- Sau mỗi hành động quan trọng: update profile, change password, delete user...
- Ví dụ trong `UserService.update_profile()`:
```python
def update_profile(user_id, email, phone):
    user = User.find_by_id(user_id)
    old_email = user.email
    
    user.email = email
    user.phone = phone
    db.session.commit()
    
    # GHI LOG
    AuditService.log(
        user_id=g.current_user_id,
        action="UPDATE_PROFILE",
        resource_type="user",
        resource_id=user_id,
        details={"old_email": old_email, "new_email": email}
    )
```

---

### ══════════════════════════════════════════════════
### GIAI ĐOẠN 4: SCHEMAS (1 ngày)
### ══════════════════════════════════════════════════

#### Task 4.1: User Schemas ⏱️ 2-3 giờ

##### 📄 `app/schemas/user_schema.py`

```python
class UpdateProfileSchema(Schema):
    """Validate dữ liệu khi update profile."""
    email = fields.Email(required=False, validate=validate.Length(max=100))
    phone = fields.String(required=False, validate=validate.Length(max=20))


class ChangePasswordSchema(Schema):
    """Validate khi đổi password."""
    old_password = fields.String(required=True, validate=validate.Length(min=1))
    new_password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    
    def validate_password_strength(self, value):
        # Giống RegisterSchema
        if not any(c.isupper() for c in value):
            raise ValidationError("Password phải có chữ hoa.")
        ...


class UserQuerySchema(Schema):
    """Validate query params khi list users."""
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))
    search = fields.String(required=False)
    role = fields.String(required=False, validate=validate.OneOf(["user", "admin"]))
```

---

#### Task 4.2: Preferences Schema ⏱️ 1 giờ

##### 📄 `app/schemas/preferences_schema.py`

```python
class PreferencesSchema(Schema):
    """Validate khi update preferences."""
    email_alerts = fields.Boolean(required=False)
    sms_alerts = fields.Boolean(required=False)
    theme = fields.String(required=False, validate=validate.OneOf(["light", "dark"]))
    language = fields.String(required=False, validate=validate.OneOf(["vi", "en"]))
    timezone = fields.String(required=False)  # Có thể thêm list timezones hợp lệ
```

---

### ══════════════════════════════════════════════════
### GIAI ĐOẠN 5: CONTROLLERS - API ENDPOINTS (2 ngày)
### ══════════════════════════════════════════════════

#### Task 5.1: User Controller ⏱️ 1 ngày

##### 📄 `app/controllers/user_controller.py`

**Các endpoints cần implement:**

```
┌─────────────────────────────────────────────────────────────────┐
│ PROFILE CÁ NHÂN (User thường và Admin)                         │
└─────────────────────────────────────────────────────────────────┘
GET    /api/users/me                  Xem profile của chính mình
PUT    /api/users/me                  Cập nhật profile (email, phone)
POST   /api/users/me/change-password  Đổi password

┌─────────────────────────────────────────────────────────────────┐
│ QUẢN LÝ USERS (Admin only)                                      │
└─────────────────────────────────────────────────────────────────┘
GET    /api/users                     Danh sách users (phân trang)
GET    /api/users/:id                 Chi tiết 1 user
PUT    /api/users/:id                 Cập nhật user khác
PATCH  /api/users/:id/status          Kích hoạt/khóa user
DELETE /api/users/:id                 Xóa user

┌─────────────────────────────────────────────────────────────────┐
│ AUDIT LOGS (Admin only)                                         │
└─────────────────────────────────────────────────────────────────┘
GET    /api/users/audit-logs          Xem logs
```

**Code mẫu:**

```python
from flask import Blueprint, request, jsonify, g
from app.middleware.auth_middleware import require_auth
from app.middleware.role_middleware import require_role

user_bp = Blueprint("users", __name__, url_prefix="/api/users")

# ─────────────────────────────────────────────────────────────
# PROFILE CÁ NHÂN
# ─────────────────────────────────────────────────────────────

@user_bp.get("/me")
@require_auth
def get_my_profile():
    """User xem profile của chính mình."""
    user_id = g.current_user_id
    result, status = UserService.get_user_profile(user_id)
    return jsonify(result), status


@user_bp.put("/me")
@require_auth
def update_my_profile():
    """User cập nhật email/phone của mình."""
    data = request.get_json()
    errors = UpdateProfileSchema().validate(data)
    if errors:
        return jsonify({"success": False, "error": {"details": errors}}), 400
    
    user_id = g.current_user_id
    result, status = UserService.update_profile(
        user_id=user_id,
        email=data.get("email"),
        phone=data.get("phone")
    )
    return jsonify(result), status


@user_bp.post("/me/change-password")
@require_auth
def change_my_password():
    """User đổi password của mình."""
    data = request.get_json()
    errors = ChangePasswordSchema().validate(data)
    if errors:
        return jsonify({"success": False, "error": {"details": errors}}), 400
    
    user_id = g.current_user_id
    result, status = UserService.change_password(
        user_id=user_id,
        old_password=data["old_password"],
        new_password=data["new_password"]
    )
    return jsonify(result), status


# ─────────────────────────────────────────────────────────────
# QUẢN LÝ USERS (ADMIN ONLY)
# ─────────────────────────────────────────────────────────────

@user_bp.get("")
@require_auth
@require_role("admin")
def list_users():
    """Admin xem danh sách users."""
    # Đọc query params
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search")
    role = request.args.get("role")
    
    result, status = UserService.list_users(
        page=page,
        per_page=per_page,
        search=search,
        role=role
    )
    return jsonify(result), status


@user_bp.get("/<int:user_id>")
@require_auth
def get_user_detail(user_id):
    """
    Xem chi tiết 1 user.
    
    Cho phép:
    - User xem chính mình (user_id == g.current_user_id)
    - Admin xem bất kỳ ai
    """
    current_user_id = g.current_user_id
    current_role = g.current_user_role
    
    # Check quyền
    if current_role != "admin" and user_id != current_user_id:
        return jsonify({
            "success": False,
            "error": {"code": "FORBIDDEN", "message": "Không có quyền xem user khác."}
        }), 403
    
    result, status = UserService.get_user_profile(user_id)
    return jsonify(result), status


@user_bp.put("/<int:user_id>")
@require_auth
@require_role("admin")
def update_user(user_id):
    """Admin cập nhật thông tin user khác."""
    data = request.get_json()
    # ... tương tự update_my_profile


@user_bp.patch("/<int:user_id>/status")
@require_auth
@require_role("admin")
def toggle_user_status(user_id):
    """Admin kích hoạt/khóa user."""
    data = request.get_json()
    is_active = data.get("is_active")
    
    if not isinstance(is_active, bool):
        return jsonify({"success": False, "error": {"message": "is_active phải là boolean."}}), 400
    
    result, status = UserService.toggle_user_status(user_id, is_active)
    return jsonify(result), status


@user_bp.delete("/<int:user_id>")
@require_auth
@require_role("admin")
def delete_user(user_id):
    """Admin xóa user."""
    result, status = UserService.delete_user(user_id)
    return jsonify(result), status
```

---

#### Task 5.2: Preferences Controller ⏱️ 3-4 giờ

##### 📄 `app/controllers/preferences_controller.py`

```python
pref_bp = Blueprint("preferences", __name__, url_prefix="/api/users/me/preferences")

@pref_bp.get("")
@require_auth
def get_preferences():
    """User xem cài đặt của mình."""
    user_id = g.current_user_id
    result, status = PreferencesService.get_preferences(user_id)
    return jsonify(result), status


@pref_bp.put("")
@require_auth
def update_preferences():
    """User cập nhật cài đặt."""
    data = request.get_json()
    errors = PreferencesSchema().validate(data)
    if errors:
        return jsonify({"success": False, "error": {"details": errors}}), 400
    
    user_id = g.current_user_id
    result, status = PreferencesService.update_preferences(user_id, **data)
    return jsonify(result), status
```

---

### ══════════════════════════════════════════════════
### GIAI ĐOẠN 6: HOÀN THIỆN VÀ TEST (1-2 ngày)
### ══════════════════════════════════════════════════

#### Task 6.1: Hoàn thiện create_app() ⏱️ 1 giờ

##### 📄 `app/__init__.py`

```python
def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Setup CORS
    CORS(app, origins=app.config.get("CORS_ORIGINS"))
    
    # Register blueprints
    from app.controllers.user_controller import user_bp
    from app.controllers.preferences_controller import pref_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(pref_bp)
    
    # Import models
    with app.app_context():
        from app.models import User, UserPreferences, AuditLog
    
    return app
```

---

#### Task 6.2: Migrations ⏱️ 30 phút

```bash
cd services/user-service

# Init migrations
flask --app run db init

# Tạo migration
flask --app run db migrate -m "create user_preferences and audit_logs tables"

# Apply migrations
flask --app run db upgrade
```

---

#### Task 6.3: Test với Postman ⏱️ 3-4 giờ

**Test cases cần cover:**

1. **User xem profile của mình** → 200
2. **User cập nhật email** → 200
3. **User đổi password sai password cũ** → 401
4. **User đổi password thành công** → 200
5. **User cố xem profile user khác** → 403
6. **Admin xem danh sách users (page 1)** → 200
7. **Admin search users** → 200
8. **Admin khóa user** → 200
9. **User bị khóa cố login** → 403 (test ở Auth Service)
10. **Admin xem audit logs** → 200
11. **User xem preferences** → 200
12. **User đổi theme light → dark** → 200

---

## 📊 TỔNG KẾT TIMELINE

```
Tuần 1:
  Ngày 1-2: Giai đoạn 1 + 2 (Setup + Middleware)
  Ngày 3-5: Giai đoạn 3 (Services)

Tuần 2:
  Ngày 1:   Giai đoạn 4 (Schemas)
  Ngày 2-3: Giai đoạn 5 (Controllers)
  Ngày 4-5: Giai đoạn 6 (Test + Fix bugs)
```

**Tổng thời gian ước tính: 7-10 ngày**

---

## ✅ CHECKLIST TỔNG

### Setup
- [ ] Tạo cấu trúc thư mục
- [ ] Copy config files từ Auth Service
- [ ] Cập nhật Dockerfile (port 5002)

### Models
- [ ] User model (copy từ Auth, bỏ auth methods)
- [ ] UserPreferences model
- [ ] AuditLog model

### Middleware
- [ ] auth_middleware.py (validate token với Auth Service)
- [ ] role_middleware.py (copy từ Auth)

### Services
- [ ] UserService: get_profile, update_profile, change_password
- [ ] UserService: list_users, toggle_status, delete_user
- [ ] PreferencesService: get_preferences, update_preferences
- [ ] AuditService: log, get_logs

### Schemas
- [ ] UpdateProfileSchema
- [ ] ChangePasswordSchema
- [ ] UserQuerySchema
- [ ] PreferencesSchema

### Controllers
- [ ] User endpoints: /me, /me/change-password
- [ ] Admin endpoints: /users, /users/:id, /users/:id/status
- [ ] Preferences endpoints: /me/preferences

### Testing
- [ ] Test với Postman (11 test cases)
- [ ] Verify audit logs được ghi đúng
- [ ] Verify phân quyền admin/user

### Deployment
- [ ] Migrations
- [ ] docker-compose.yml thêm user-service
- [ ] Test tích hợp với Auth Service

---

## 🎯 KẾT LUẬN

**User Service khác Auth Service ở chỗ:**
- Không xử lý login/JWT (Auth Service lo)
- Gọi Auth Service để validate token
- Focus vào quản lý profile, preferences, users
- Ghi audit logs cho mọi thay đổi

**Điểm chú ý:**
- Middleware `require_auth` phải gọi Auth Service
- Phân quyền rõ ràng: user chỉ chỉnh sửa mình, admin chỉnh sửa tất cả
- Ghi audit log sau mỗi hành động quan trọng
- Validate email unique khi update profile

Bạn có câu hỏi gì về bất kỳ task nào không?
