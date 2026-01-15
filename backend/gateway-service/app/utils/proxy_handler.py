# backend\gateway-service\app\utils\proxy_handler.py
import requests
from flask import request, Response, jsonify

def forward_request(service_url, path):
    try:
        # Xử lý double slash: Xóa dấu / ở cuối service_url và ở đầu path
        clean_url = service_url.rstrip('/')
        clean_path = path.lstrip('/')
        target_url = f"{clean_url}/{clean_path}"

        # Debug log (Nên có để biết gateway đang gọi đi đâu)
        print(f"Forwarding to: {target_url}")

        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            params=request.args,
            allow_redirects=False
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, headers)

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Service Unavailable", "message": f"Không thể kết nối tới {service_url}"}), 503