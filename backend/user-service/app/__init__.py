# backend\user-service\app\__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)


    CORS(app, resources={
        r"/api/*": {  # Chỉ áp dụng cho các route bắt đầu bằng /api
            "origins": ["http://localhost:5173", "http://localhost:5002"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True # Quan trọng nếu bạn dùng Cookie/Session sau này
        }
    })

    from app.controllers.user_controller import user_bp
    app.register_blueprint(user_bp, url_prefix="/api/user")

    return app

