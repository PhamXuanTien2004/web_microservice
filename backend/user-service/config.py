import os 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "SECRET_KEY"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://auth_user:root%40root@localhost:3306/auth_service_db"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False