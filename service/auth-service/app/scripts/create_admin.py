import os
from app.extensions import db
from app.models.auth_model import User
from flask import current_app


def create_admin_if_not_exists():
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    phone = os.getenv("ADMIN_PHONE", "")
    
    if not username or not password:
        current_app.logger.warning(
            "ADMIN_USERNAME or ADMIN_PASSWORD not set. Skip admin creation."
        )
        return

    existing_user = User.find_by_username(username)
    if existing_user:
        current_app.logger.info("Admin user already exists. Skip creation.")
        return

    admin = User(
        username=username,
        email=email,
        phone=phone,
        role="admin",
        is_active=True,
    )
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    current_app.logger.info(
        f"Admin user '{username}' created successfully."
    )