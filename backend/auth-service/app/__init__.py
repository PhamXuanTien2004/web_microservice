from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS  # <--- 1. Import thư viện

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    # ---------------------------------------------------------
    # 2. Cấu hình CORS tại đây
    
    # Cách 2: (KHUYÊN DÙNG) Chỉ cho phép Frontend Vue gọi vào
    # Giả sử Vue chạy ở http://localhost:5173
    CORS(app, resources={
        r"/api/*": {  # Chỉ áp dụng cho các route bắt đầu bằng /api
            "origins": ["http://localhost:5173", "http://localhost:5001"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True # Quan trọng nếu bạn dùng Cookie/Session sau này
        }
    })
    # ---------------------------------------------------------

    from app.controllers.auth_controller import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    
    return app