import os

class Config:
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
    DEVICE_SERVICE_URL = os.getenv('DEVICE_SERVICE_URL', 'http://localhost:5002')
    DATA_SERVICE_URL = os.getenv('DATA_SERVICE_URL', 'http://localhost:5003')

    SECRET_KEY = os.getenv('SECRET_KEY', 'secret-key')