import requests
from flask import request, jsonify, make_response

def forward_request(service_url, endpoint, extra_headers: dict = None):
    """
    Hàm trung gian để chuyển tiếp request từ Gateway sang Microservice.
    Đảm bảo giữ nguyên JSON data và Cookies (cả 2 chiều).
    """
    
    # 1. Xây dựng URL đích
    # service_url: http://localhost:5001/api/auth
    # endpoint: /login
    # -> url: http://localhost:5001/api/auth/login
    url = f"{service_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    method = request.method
    
    # 2. Lấy dữ liệu từ Frontend gửi lên
    # json_data: Dùng cho POST/PUT (body)
    # incoming_cookies: Dùng cho Logout hoặc các request cần xác thực (Gateway -> Service)
    json_data = request.get_json(silent=True)
    incoming_cookies = request.cookies

    # Build headers to forward (exclude hop-by-hop headers)
    incoming_headers = {}
    for k, v in request.headers.items():
        if k.lower() in ('host', 'content-length', 'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade'):
            continue
        incoming_headers[k] = v

    if extra_headers:
        incoming_headers.update(extra_headers)

    try:
        # 3. Gửi request sang Service đích
        # Debug: log incoming cookies forwarded from browser to gateway
        print(f"[Gateway] Forwarding to {url} with cookies: {incoming_cookies}")

        resp = requests.request(
            method=method,
            url=url,
            json=json_data,
            cookies=incoming_cookies, # [QUAN TRỌNG 1]: Chuyển tiếp Cookie từ FE -> Service
            headers=incoming_headers,
            timeout=10 # Set timeout để tránh treo Gateway nếu Service chết
        )

        # 4. Nhận phản hồi từ Service
        # Xử lý trường hợp Service trả về nội dung rỗng (ví dụ 204 No Content)
        response_data = resp.json() if resp.content else {}

        flask_response = make_response(
            jsonify(response_data),
            resp.status_code
        )

        # 5. Forward Set-Cookie headers from upstream response to client unchanged (if any)
        # Prefer copying raw Set-Cookie header(s) instead of reconstructing cookies
        set_cookie = resp.headers.get('Set-Cookie')
        if set_cookie:
            # If multiple Set-Cookie headers are present, requests may combine them; still forward what we have
            flask_response.headers.add('Set-Cookie', set_cookie)

        return flask_response

    except requests.exceptions.RequestException as e:
        # Xử lý khi Service đích bị sập hoặc timeout
        print(f"Error forwarding request to {url}: {e}")
        return jsonify({
            "error": "Service Unavailable", 
            "details": "Không thể kết nối tới Service đích"
        }), 503