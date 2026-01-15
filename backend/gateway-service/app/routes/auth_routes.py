from flask import Blueprint, jsonify, request
from app.config import Config
from app.middleware.check_user import check_user
from app.utils.proxy_handler import forward_request

auth_bp = Blueprint('auth_bp', __name__)

# --- AUTH ROUTES ---

@auth_bp.route('register', methods=['POST'])
def register():
    return forward_request(Config.AUTH_SERVICE_URL, '/register')

@auth_bp.route('login', methods=['POST'])
def login():
    return forward_request(Config.AUTH_SERVICE_URL, '/login')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # QUAN TRỌNG: Không gọi check_user() ở đây!
    # Hãy để request đi thẳng sang Auth Service.
    # Auth Service sẽ lo việc xóa cookie dù token có sống hay chết.
    return forward_request(Config.AUTH_SERVICE_URL, '/logout')
