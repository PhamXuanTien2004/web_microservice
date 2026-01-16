# app/models/user_model.py
from app import db

class Users(db.Model):
    __tablename__ = "users_profile"

    id = db.Column(db.Integer, primary_key=True, autoincrement=False) 
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telphone = db.Column(db.String(20), unique=True, nullable=True)
    role = db.Column(db.String(5), default="User", nullable=False)
    sensors = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "telphone": self.telphone,
            "role": self.role,
            "sensors": self.sensors,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }