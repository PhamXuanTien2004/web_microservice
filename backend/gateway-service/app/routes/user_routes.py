from flask import Blueprint, jsonify, request
from app.config import Config
from app.middleware.check_user import check_user
from app.utils.proxy_handler import forward_request

user_bp = Blueprint('user_bp', __name__)

# --- USER ROUTES (Cần bảo vệ) ---

# Public ROUTES
@user_bp.route('createUser', methods=['POST'])
def creatUser():
  
    return forward_request(Config.USER_SERVICE_URL, '/createUser')
    
# Proteced ROUTES
@user_bp.route('profile', methods=['GET']) # Profile thường là GET
def get_profile():
    # Gọi middleware
    is_valid, result = check_user()
    
    if not is_valid:
        # result lúc này là json error message
        return result, 401

    # Nếu valid, 'result' chứa payload user info.
    # Bạn có thể truyền user_id vào header để User Service biết ai đang gọi (Optional)
    # headers = {'X-User-ID': str(result.get('sub'))}
    
    return forward_request(Config.USER_SERVICE_URL, '/profile')