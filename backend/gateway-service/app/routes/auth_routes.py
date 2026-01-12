from flask import Blueprint
from app.config import Config
from app.utils.proxy_handler import forward_request

# Tạo Blueprint
auth_bp = Blueprint('auth', __name__)

# Route bắt tất cả request sau /api/auth/
@auth_bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def auth_proxy(path):
    new_path = f"api/auth/{path}"
    return forward_request(Config.AUTH_SERVICE_URL, new_path)