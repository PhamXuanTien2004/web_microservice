from flask import Blueprint, request
from ..middleware.auth_middleware import token_required
from ..services.proxy_service import forward_request

bp = Blueprint("device_routes", __name__)

@bp.route("/", methods=["GET"])
@token_required
def get_devices(user):
    return forward_request(
        service="DEVICE",
        path="/",
        method="GET",
        headers=request.headers
    )

@bp.route("/", methods=["POST"])
@token_required
def create_device(user):
    return forward_request(
        service="DEVICE",
        path="/",
        method="POST",
        data=request.json,
        headers=request.headers
    )
