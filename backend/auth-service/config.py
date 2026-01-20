# backend\auth-service\config.py

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "SECRET_KEY"  # Nên đổi thành chuỗi ngẫu nhiên dài hơn

    JWT_ACCESS_EXPIRES = 15      # phút
    JWT_REFRESH_EXPIRES = 7      # ngày

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://auth_user:root%40root@localhost:3306/auth_service_db"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    USER_SERVICE_URL = "http://localhost:5002/api/user"