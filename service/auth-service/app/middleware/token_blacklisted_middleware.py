from functools import wraps
from flask_jwt_extended import get_jwt

def check_if_token_is_blacklisted(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jti = get_jwt()["jti"] # Lấy ID định danh của token hiện tại
        
        # Kiểm tra trong Redis hoặc DB
        token_in_blacklist = TokenBlacklist.query.filter_by(token_jti=jti).first()
        
        if token_in_blacklist:
            return jsonify({"message": "Token đã bị vô hiệu hóa (logged out)"}), 401
            
        return f(*args, **kwargs)
    return decorated_function