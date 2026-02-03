import axios from 'axios';

// 1. Cấu hình instance duy nhất trỏ tới Gateway Service
// Export tên `authApi` để các component hiện có import `{ authApi }`
export const authApi = axios.create({
    // Giả sử Gateway của bạn chạy ở port 5000
    baseURL: 'http://localhost:5000/api',
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: true // Quan trọng: Cho phép tự động gửi kèm HttpOnly Cookie
});

// Giữ alias `api` cho tương thích ngược
export const api = authApi;

// 2. Thiết lập Interceptor cho instance chung
api.interceptors.request.use(
    (config) => {
        // Vì bạn dùng Cookie HttpOnly, JavaScript không cần can thiệp vào token
        console.log(`[Gateway Request]: ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 3. Xử lý lỗi tập trung (Optional nhưng nên có)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            console.warn("Phiên đăng nhập hết hạn hoặc không hợp lệ.");
            // Bạn có thể xử lý redirect về /login ở đây nếu cần
        }
        return Promise.reject(error);
    }
);