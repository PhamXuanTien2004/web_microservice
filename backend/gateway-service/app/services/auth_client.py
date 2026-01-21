import requests
from app.config import Config

def register_auth(data):
    response = requests.post(
        Config.AUTH_SERVICE_URL,
        json=data,
        timeout=Config.TIMEOUT
    )
    return response
