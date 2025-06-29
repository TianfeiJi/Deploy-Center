import {defineStore} from 'pinia';

export const useAuthStore = defineStore('authStore', {
  state: () => ({
    innerToken: sessionStorage.getItem('token'), // 初始化token状态从sessionStorage读取
  }),
  actions: {
    setToken(newToken: string) {
      console.log(this)
      this.innerToken = newToken;
      sessionStorage.setItem('token', newToken);
    },
    clearToken() {
      this.innerToken = null;
      sessionStorage.removeItem('token');
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.innerToken,
    token: (state) => state.innerToken
  },
});
