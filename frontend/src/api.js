import axios from 'axios';

// Kết nối tới Auth Service (Đăng ký/Đăng nhập)
export const authApi = axios.create({
    baseURL: 'http://localhost:5001/api/auth',
    headers: {
        'Content-Type': 'application/json'
    }
});

// Kết nối tới User Service (Quản lý Profile/Sensor)
export const userApi = axios.create({
    baseURL: 'http://localhost:5002/api/user',
    headers: {
        'Content-Type': 'application/json'
    }
});

userApi.interceptors.request.use((config) => {
    const token = localStorage.getItem('user_token');
    if (token) {
        // Gửi theo chuẩn Bearer Token
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});