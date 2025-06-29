// src/stores/useLoginUserStore.ts
import { defineStore } from 'pinia';
import { User } from 'src/types/User';
import { getUser } from 'src/api/userApi';

export const useLoginUserStore = defineStore('loginUserStore', {
  state: () => ({
    // 初始化 loginUser 状态从 sessionStorage 读取
    loginUser: JSON.parse(sessionStorage.getItem('loginUser') || 'null') as User | null,
  }),
  actions: {
    // 设置当前登录用户
    async setLoginUserByUserId(userId: number) {
      try {
        const response = await getUser(userId);
        if (response.code === 200 && response.data) {
          this.loginUser = response.data;
          // 将用户信息存储到 sessionStorage
          sessionStorage.setItem('loginUser', JSON.stringify(response.data));
        } else {
          throw new Error(response.msg || 'User not found');
        }
      } catch (error) {
        console.error('Error fetching user details:', error);
        this.loginUser = null; // 确保在出错时清除 loginUser
        sessionStorage.removeItem('loginUser'); // 同时清除 sessionStorage 中的用户信息
      }
    },

    // 清除当前登录用户
    clearLoginUser() {
      this.loginUser = null;
      sessionStorage.removeItem('loginUser'); // 清除 sessionStorage 中的用户信息
    },
  }
});