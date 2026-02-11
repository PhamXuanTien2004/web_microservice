# backend\gateway-service\app\__init__.py
from flask import Flask
from flask_cors import CORS 
from app.config import Config

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:5000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": "*", # Cho phép tất cả headers để tránh lỗi header không khớp
            "supports_credentials": True 
        }
    })
    

    # Đăng ký các Blueprint (Routes)
    from app.routes.user_routes import user_bp
    from app.routes.auth_routes import auth_bp
    # from app.routes.user_routes import user_routes_bp # (Tự tạo file tương tự auth)

    # Prefix giúp URL đẹp hơn: localhost:5000/api/auth/...
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')

    return app