# backend\gateway-service\app\config.py
import os

class Config:
    SECRET_KEY = "SECRET_KEY" 

    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001/api/auth')
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:5002/api/user')
    DATA_SERVICE_URL = os.getenv('DATA_SERVICE_URL', 'http://localhost:5003')

