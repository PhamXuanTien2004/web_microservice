from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes import auth_routes, device_routes, data_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    app.register_blueprint(auth_routes.bp, url_prefix="/api/auth")
    app.register_blueprint(device_routes.bp, url_prefix="/api/devices")
    app.register_blueprint(data_routes.bp, url_prefix="/api/data")

    return app
