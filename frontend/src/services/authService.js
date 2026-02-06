import { authApi } from '../App';

export const authService = {
  login: (username, password) => authApi.post('/auth/login', { username, password }),
  register: (data) => authApi.post('/auth/register', data),
  logout: () => authApi.post('/auth/logout')
};
