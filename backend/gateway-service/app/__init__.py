from flask import Flask
from flask_cors import CORS # Cài thêm: pip install flask-cors

def create_app():
    app = Flask(__name__)
    
    # Cấu hình CORS cho phép Frontend gọi vào Gateway
    CORS(app, resources={r"/api/*": {"origins": "*"}}) 

    # Đăng ký các Blueprint (Routes)
    from app.routes.auth_routes import auth_bp
    # from app.routes.user_routes import user_routes_bp # (Tự tạo file tương tự auth)
    
    # Prefix giúp URL đẹp hơn: localhost:5000/api/auth/...
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(user_routes_bp, url_prefix='/api/users')

    return app