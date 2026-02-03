import { authApi } from '../App';

export const userService = {
  getMyProfile: () => authApi.get('/user/profile')
};
