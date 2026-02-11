import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "SECRET_KEY"
    JWT_SECRET_KEY = "SECRET_KEY"

    # Thời hạn token dưới dạng số nguyên (phút cho access, ngày cho refresh)
    JWT_ACCESS_EXPIRES = 15      # phút
    JWT_REFRESH_EXPIRES = 7      # ngày

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://auth_user:root%40root@localhost:3306/auth_service_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    USER_SERVICE_URL = "http://localhost:5002/api/user"

    # --- [THÊM MỚI] CẤU HÌNH COOKIE ĐỂ FIX LỖI ---
    # False = Chạy localhost (HTTP). True = Chạy Production (HTTPS)
    COOKIE_SECURE = False

    # 'Lax' giúp cookie dễ được chấp nhận hơn khi dev
    COOKIE_SAMESITE = 'Lax'

    # --- [THÊM MỚI] ĐỂ JWT MIDDLEWARE HIỂU COOKIE ---
    # Bắt buộc có dòng này thì hàm logout (@jwt_required) mới tìm thấy token trong cookie
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
    JWT_COOKIE_CSRF_PROTECT = False # Tắt CSRF khi dev để tránh lỗi 401/422 khó hiểu