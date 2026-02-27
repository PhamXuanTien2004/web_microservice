"""
User Service Application Factory

Khởi tạo Flask app, extensions, và đăng ký blueprints.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from app.extensions import db
import logging
import os


def create_app(config_name=None):
    """
    Application Factory Pattern.
    
    Args:
        config_name: "development", "production", hoặc "testing"
    
    Returns:
        Flask app instance
    """
    # 1. Create Flask app
    app = Flask(__name__)
    
    # 2. Load configuration
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
    
    from config import config
    app.config.from_object(config.get(config_name, config["development"]))
    
    # 3. Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    # 4. Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    
    # 5. Setup CORS
    # Cho phép requests từ frontend và Auth Service
    CORS(app, 
         origins=app.config.get("CORS_ORIGINS", ["http://localhost:3000", "http://localhost:5001"]),
         supports_credentials=True)
    
    # ═══════════════════════════════════════════════════════════════
    # REGISTER BLUEPRINTS
    # ═══════════════════════════════════════════════════════════════
    
    # Import blueprints
    from app.controllers.user_controller import user_bp
    from app.controllers.preferences_controller import pref_bp
    
    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(pref_bp)
    
    logging.info("Blueprints registered:")
    logging.info(f"  - {user_bp.name}: {user_bp.url_prefix}")
    logging.info(f"  - {pref_bp.name}: {pref_bp.url_prefix}")
    
    # ═══════════════════════════════════════════════════════════════
    # IMPORT MODELS
    # ═══════════════════════════════════════════════════════════════
    
    # Import models để Flask-Migrate nhận diện
    with app.app_context():
        from app.models.user_model import User
        from app.models.user_preferences_model import UserPreferences
        from app.models.audit_log import AuditLog
    
    # ═══════════════════════════════════════════════════════════════
    # HEALTH CHECK & INFO ENDPOINTS
    # ═══════════════════════════════════════════════════════════════
    
    @app.route("/")
    def index():
        """Root endpoint - Service info."""
        return jsonify({
            "service": "User Service",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "health": "/health",
                "users": "/api/users",
                "preferences": "/api/users/me/preferences"
            }
        }), 200
    
    @app.route("/health")
    def health_check():
        """Health check endpoint for monitoring."""
        try:
            # Check database connection
            db.session.execute("SELECT 1")
            db_status = "ok"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return jsonify({
            "status": "ok" if db_status == "ok" else "degraded",
            "service": "user-service",
            "database": db_status
        }), 200 if db_status == "ok" else 503
    
    # ═══════════════════════════════════════════════════════════════
    # GLOBAL ERROR HANDLERS
    # ═══════════════════════════════════════════════════════════════
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "Endpoint không tồn tại."
            }
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({
            "success": False,
            "error": {
                "code": "METHOD_NOT_ALLOWED",
                "message": "HTTP method không được hỗ trợ cho endpoint này."
            }
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logging.error(f"Internal error: {str(error)}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Lỗi server. Vui lòng thử lại sau."
            }
        }), 500
    
    # ═══════════════════════════════════════════════════════════════
    # REQUEST/RESPONSE LOGGING (Optional - for debugging)
    # ═══════════════════════════════════════════════════════════════
    
    @app.before_request
    def log_request():
        """Log incoming requests."""
        from flask import request
        if app.config.get("DEBUG"):
            logging.info(f"{request.method} {request.path}")
    
    @app.after_request
    def log_response(response):
        """Log outgoing responses."""
        from flask import request
        if app.config.get("DEBUG"):
            logging.info(f"{request.method} {request.path} -> {response.status_code}")
        return response
    
    # Log startup info
    logging.info("=" * 60)
    logging.info("User Service initialized successfully")
    logging.info(f"Environment: {config_name}")
    logging.info(f"Debug mode: {app.config.get('DEBUG')}")
    logging.info(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    logging.info("=" * 60)
    
    return app