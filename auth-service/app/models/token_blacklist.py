# app/models/token_blacklist.py
from app import db
from datetime import datetime

class TokenBlacklist(db.Model):
    __tablename__ = "token_blacklist"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), unique=True, nullable=False)
    expired_at = db.Column(db.DateTime, nullable=False)
