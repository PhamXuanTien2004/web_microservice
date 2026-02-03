import { authApi } from '../App';

export const authService = {
  login: (username, password) => authApi.post('/auth/login', { username, password }),
  logout: () => authApi.post('/auth/logout')
};
