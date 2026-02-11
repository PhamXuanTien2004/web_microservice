# backend\user-service\app\__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    from app.controllers.user_controller import user_bp
    app.register_blueprint(user_bp, url_prefix="/api/user")

    return app

