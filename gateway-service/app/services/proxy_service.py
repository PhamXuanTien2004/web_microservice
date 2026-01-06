import requests
from flask import current_app, jsonify

SERVICE_MAP = {
    "AUTH": "AUTH_SERVICE_URL",
    "DEVICE": "DEVICE_SERVICE_URL",
    "DATA": "DATA_SERVICE_URL",
}

def forward_request(service, path, method, data=None, headers=None):
    service_url = current_app.config[SERVICE_MAP[service]]
    url = f"{service_url}{path}"

    try:
        response = requests.request(
            method=method,
            url=url,
            json=data,
            headers=headers,
            timeout=5
        )
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 503
