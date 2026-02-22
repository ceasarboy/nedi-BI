import api from './api';

const AUTH_KEY = 'pb_bi_auth';

export const authService = {
  getStoredAuth() {
    try {
      const stored = localStorage.getItem(AUTH_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('读取认证信息失败:', error);
    }
    return null;
  },

  setStoredAuth(authData) {
    try {
      localStorage.setItem(AUTH_KEY, JSON.stringify(authData));
    } catch (error) {
      console.error('保存认证信息失败:', error);
    }
  },

  clearStoredAuth() {
    try {
      localStorage.removeItem(AUTH_KEY);
    } catch (error) {
      console.error('清除认证信息失败:', error);
    }
  },

  async login(username, password) {
    const response = await api.post('/auth/login', { username, password });
    if (response.data && response.data.success && response.data.user) {
      this.setStoredAuth(response.data.user);
      return response.data.user;
    }
    throw new Error(response.data?.message || '登录失败');
  },

  async register(username, password, confirmPassword) {
    const response = await api.post('/auth/register', { 
      username, 
      password, 
      confirm_password: confirmPassword 
    });
    if (response.data && response.data.success) {
      return response.data;
    }
    throw new Error(response.data?.message || '注册失败');
  },

  async logout() {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('登出API调用失败:', error);
    }
    this.clearStoredAuth();
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    if (response.data && response.data.success && response.data.user) {
      this.setStoredAuth(response.data.user);
      return response.data.user;
    }
    throw new Error('获取用户信息失败');
  },

  isAuthenticated() {
    return this.getStoredAuth() !== null;
  },

  getUser() {
    return this.getStoredAuth();
  },

  isAdmin() {
    const user = this.getStoredAuth();
    return user && user.role === 'admin';
  }
};

export default authService;
