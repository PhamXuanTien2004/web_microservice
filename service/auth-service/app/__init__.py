from flask import Flask
from flask_cors import CORS
from config import config
from app.extensions import db, jwt, migrate
from app.scripts.create_admin import create_admin_if_not_exists

def create_app(config_name: str = "default") -> Flask:
    """
    Tạo và cấu hình Flask application.

    Args:
        config_name: "development" | "testing" | "production" | "default"

    Returns:
        Flask application instance đã được cấu hình đầy đủ.
    """
    app = Flask(__name__)

    # ── 1. Load config ────────────────────────────────────────
    app.config.from_object(config[config_name])

    # ── 2. Init extensions ────────────────────────────────────
    # Thứ tự quan trọng: db trước migrate (migrate cần db)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # ── 3. Setup CORS ─────────────────────────────────────────
    CORS(
        app,
        origins=app.config.get("CORS_ORIGINS", ["http://localhost:3000"]),
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )

    # ── 4. Đăng ký JWT callbacks (middleware) ─────────────────
    # Phải làm SAU jwt.init_app(app) để jwt đã có app context
    from app.middleware.jwt_middleware import register_jwt_callbacks
    register_jwt_callbacks(jwt)

    # ── 5. Đăng ký Blueprints (routes) ───────────────────────
    from app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)

    # ── 6. Import models để Flask-Migrate nhận diện ───────────
    # Nếu không import, flask db migrate sẽ không tạo migration
    with app.app_context():
        from app.models import User, TokenBlacklist  # noqa: F401
        db.create_all()
        create_admin_if_not_exists()

    # ── 7. Register error handlers ────────────────────────────
    _register_error_handlers(app)

    return app


def _register_error_handlers(app: Flask):
    """Đăng ký global error handlers cho các HTTP errors thường gặp."""

    @app.errorhandler(400)
    def bad_request(error):
        return {
            "success": False,
            "error": {"code": "BAD_REQUEST", "message": "Request không hợp lệ."},
        }, 400

    @app.errorhandler(404)
    def not_found(error):
        return {
            "success": False,
            "error": {"code": "NOT_FOUND", "message": "Endpoint không tồn tại."},
        }, 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return {
            "success": False,
            "error": {
                "code": "METHOD_NOT_ALLOWED",
                "message": "HTTP method không được phép.",
            },
        }, 405

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal Server Error: {error}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "Lỗi server. Thử lại sau."},
        }, 500
