import requests
from app.config import Config

def create_user_profile(data):
    response = requests.post(
        Config.USER_SERVICE_URL,
        json=data,
        timeout=Config.TIMEOUT
    )
    return response
