from flask import Blueprint, request
from ..middleware.auth_middleware import token_required
from ..services.proxy_service import forward_request

bp = Blueprint("data_routes", __name__)

@bp.route("/realtime", methods=["GET"])
@token_required
def realtime_data(user):
    return forward_request(
        service="DATA",
        path="/realtime",
        method="GET",
        headers=request.headers
    )
