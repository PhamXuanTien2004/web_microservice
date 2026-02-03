# E2E Test Guide — Frontend ↔ Backend Integration

## Kiến trúc
- **Frontend**: React + Mantine UI (Vite dev server on port 5173)
- **Gateway**: Flask (port 5000) — routes requests to microservices
- **Auth Service**: Flask (port 5001) — login/register, sets HttpOnly cookies
- **User Service**: Flask (port 5002) — user profiles
- **Database**: MySQL (localhost, must be running)

## Bước 1: Kiểm tra MySQL
Đảm bảo MySQL đang chạy:
```bash
mysql -u auth_user -p -e "SHOW DATABASES;"
# Password: root@root
# Nếu không kết nối được, khởi động MySQL service
```

## Bước 2: Khởi chạy Backend Services (mở 3 terminal riêng)

### Terminal 1 — Auth Service
```powershell
cd backend\auth-service
python run.py
# Expect: Running on http://localhost:5001/
```

### Terminal 2 — User Service
```powershell
cd backend\user-service
python run.py
# Expect: Running on http://localhost:5002/
```

### Terminal 3 — Gateway
```powershell
cd backend\gateway-service
python run.py
# Expect: Running on http://localhost:5000/
```

## Bước 3: Khởi chạy Frontend (một terminal khác)
```powershell
cd frontend
npm run dev
# Expect: Local: http://localhost:5173/
```

## Bước 4: Test luồng (từ trình duyệt)

### Test 4a — Kiểm tra trang login load được
- Mở http://localhost:5173
- Nên thấy form "Chào mừng trở lại!" với input Username/Password
- Console (DevTools) không nên có lỗi

### Test 4b — Đăng ký (Register)
- Nếu có trang `/register`, thử tạo account mới:
  - Username: `testuser_01` (3-50 ký tự)
  - Password: `TestPass123!` (phải có: hoa, thường, số, đặc biệt, >=8 ký tự)
  - Name: `Test User`
  - Email: `test@example.com`
  - Phone: `0123456789` (format SĐT Việt Nam)
  - Role: `user` hoặc `admin`
- **Kỳ vọng**: 
  - Alert "Đăng ký thành công!"
  - Redirect tới `/login`
  - Kiểm tra DB: `SELECT * FROM auth_service_db.users;` (auth service)

### Test 4c — Đăng nhập (Login)
- Username: `testuser_01`
- Password: `TestPass123!`
- **Kỳ vọng**:
  - Không có lỗi 401 hay 404
  - Alert "Chào mừng testuser_01 đã quay trở lại!"
  - Redirect tới profile page
  - Hiển thị: Name, Email, Role, Sensors (nếu user), Topic (nếu user)

### Test 4d — Profile Page
- URL: http://localhost:5173/user/profile
- **Kỳ vọng**:
  - Hiển thị thông tin user (name, email, role, sensors, topic)
  - Nút "Đăng xuất" hoạt động
  - Header hiển thị tên user + Logout button

### Test 4e — Logout
- Click "Đăng xuất" button
- **Kỳ vọng**:
  - Cookie bị xóa (DevTools → Application → Cookies → localhost → refresh)
  - Redirect về trang login
  - Khi F5 trang login, không hiển thị profile (vì cookie hết hạn)

## Bước 5: Kiểm tra Backend Logs

### Check Auth Service Console
Nên thấy:
```
[Gateway] Forwarding to http://localhost:5001/api/auth/login with cookies: ...
127.0.0.1 - - [03/Feb/2026 ...] "POST /api/auth/login HTTP/1.1" 200 -
```

### Check Gateway Console
Nên thấy:
```
[Gateway Request]: POST /auth/login
[Gateway] Forwarding to http://localhost:5001/api/auth/login with cookies: ...
```

### Check User Service Console
Nên thấy:
```
[Gateway] Forwarding to http://localhost:5002/api/user/internal/users with cookies: ...
127.0.0.1 - - [03/Feb/2026 ...] "POST /api/user/internal/users HTTP/1.1" 201 -
```

## Bước 6: Kiểm tra Network & Cookies (DevTools)

### Test Login Cookie Flow
1. Mở DevTools (F12) → Network tab
2. Thực hiện login
3. Xem request POST /api/auth/login:
   - Response Headers nên có `Set-Cookie: access_token_cookie=...`
   - Response Headers nên có `Set-Cookie: refresh_token_cookie=...`
4. Sau login, kiểm tra Application → Cookies:
   - Nên thấy 2 cookies: `access_token_cookie` và `refresh_token_cookie`
   - HttpOnly = true (JavaScript không thể truy cập)
   - SameSite = Lax (có thể gửi khi same-site request)
   - Secure = false (dev mode)

### Test Profile Cookie Forward
1. Trên trang profile, xem request GET /api/user/profile:
   - Request Headers nên có `Cookie: access_token_cookie=...; refresh_token_cookie=...`
   - Response Status = 200 (not 401)

## Bước 7: Xử lý Lỗi Thường Gặp

### Lỗi 401 trên /api/user/profile
- **Nguyên nhân**: Browser không gửi cookie hoặc token expired
- **Kiểm tra**:
  - Có Set-Cookie trong response login không? (Nếu không, auth service chưa set)
  - Có Cookie header trong request profile không? (Nếu không, browser block do SameSite)
  - Token còn hạn không? (15 phút, check `exp` trong token)

### Lỗi 404 trên /api/auth/login
- **Nguyên nhên**: Frontend gọi `/login` thay vì `/auth/login`
- **Fix**: Kiểm tra `frontend/src/services/authService.js` dùng `.post('/auth/login')`

### Lỗi CORS
- **Nguyên nhân**: Gateway CORS settings sai
- **Fix**: Kiểm tra `backend/gateway-service/app/__init__.py` — `origins` nên có `http://localhost:5173`

### Lỗi MySQL Connection Refused
- **Nguyên nhân**: MySQL không chạy hoặc credentials sai
- **Fix**: 
  - Kiểm tra `backend/auth-service/config.py` — `SQLALCHEMY_DATABASE_URI`
  - Khởi động MySQL: `mysql.server start` (macOS) hoặc `services.msc` (Windows)

## Bước 8: Summary Checklist

- [ ] Auth service chạy (port 5001)
- [ ] User service chạy (port 5002)
- [ ] Gateway chạy (port 5000)
- [ ] Frontend chạy (port 5173)
- [ ] MySQL kết nối thành công
- [ ] Đăng ký tạo user thành công
- [ ] Đăng nhập nhận Set-Cookie
- [ ] Browser lưu cookies (DevTools check)
- [ ] Profile page load mà không có 401
- [ ] Logout xóa cookies
- [ ] Refresh trang sau logout → back to login form

## Nếu tất cả pass
🎉 **E2E test passed!** Frontend ↔ Backend integration hoạt động. Bước tiếp theo: polish UI, thêm notification, refactor RegisterForm.

## Nếu có lỗi
Paste lại:
- Exact error message từ console
- Network request/response headers
- Backend terminal logs (Auth/User/Gateway)
