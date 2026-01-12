import requests
from flask import request, Response, jsonify

def forward_request(service_url, path):
    """
    Hàm chung để chuyển tiếp request từ Gateway sang Microservice đích
    """
    try:
        target_url = f"{service_url}/{path}"
        
        # Forward request với method, headers, params, và body
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            params=request.args,
            allow_redirects=False
        )

        # Lọc headers trả về (bỏ các header hop-by-hop)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, headers)

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Service unavailable", "service": service_url}), 503