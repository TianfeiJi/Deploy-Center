import {defineStore} from 'pinia';

export const useAuthStore = defineStore('authStore', {
  state: () => ({
    innerToken: localStorage.getItem('token'), // 初始化token状态从localStorage读取
  }),
  actions: {
    setToken(newToken: string) {
      console.log(this)
      this.innerToken = newToken;
      localStorage.setItem('token', newToken);
    },
    clearToken() {
      this.innerToken = null;
      localStorage.removeItem('token');
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.innerToken,
    token: (state) => state.innerToken
  },
});
