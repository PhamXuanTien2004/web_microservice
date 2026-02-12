# service\auth-service\run.py
import os
from app import create_app

# Đọc môi trường từ biến ENV (default: development)
config_name = os.getenv("FLASK_ENV", "development")

# Tạo app instance
app = create_app(config_name)

if __name__ == "__main__":
    port = int(os.getenv("AUTH_SERVICE_PORT", 5001))
    debug = config_name == "development"

    print(f"🚀 Auth Service running on port {port} [{config_name}]")
    app.run(host="0.0.0.0", port=port, debug=debug)