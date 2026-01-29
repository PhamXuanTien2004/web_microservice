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

userApi.interceptors.request.use(
    (config) => {
        // KIỂM TRA: Key này phải giống hệt key lúc bạn thực hiện localStorage.setItem() khi Login
        const token = localStorage.getItem('access_token'); 
        
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log("Đã đính kèm Token vào Header");
        } else {
            console.warn("Không tìm thấy Token trong LocalStorage");
        }
        return config;
    },
    (error) => Promise.reject(error)
);