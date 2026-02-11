from flask import Blueprint, jsonify, request
from app.config import Config
from app.middleware.check_user import check_user
from app.utils.proxy_handler import forward_request

user_bp = Blueprint('user_bp', __name__)

# --- USER ROUTES (Cần bảo vệ) ---

# Public ROUTES
@user_bp.route('/createUser', methods=['POST'])
def creatUser():
    # Forward registration from Auth Service to User Service internal endpoint
    return forward_request(Config.USER_SERVICE_URL, '/internal/users')

# Protected ROUTES
@user_bp.route('/profile', methods=['GET'])
def get_profile():
    # Gọi middleware
    is_valid, payload_or_error, status = check_user()

    if not is_valid:
        return jsonify(payload_or_error), status

    # Nếu valid, 'payload_or_error' chứa payload user info.
    # Thêm header X-User-ID để User Service biết ai đang gọi
    extra_headers = {'X-User-ID': str(payload_or_error.get('sub'))}

    return forward_request(Config.USER_SERVICE_URL, '/profile', extra_headers=extra_headers)