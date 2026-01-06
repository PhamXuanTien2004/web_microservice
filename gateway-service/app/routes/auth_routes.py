from flask import Blueprint, request
from ..services.proxy_service import forward_request

bp = Blueprint("auth_routes", __name__)

@bp.route("/login", methods=["POST"])
def login():
    return forward_request(
        service="AUTH",
        path="/login",
        method="POST",
        data=request.json
    )

@bp.route("/register", methods=["POST"])
def register():
    return forward_request(
        service="AUTH",
        path="/register",
        method="POST",
        data=request.json
    )
