import axios from 'axios';
import { Notify } from 'quasar';
import { useAuthStore } from 'src/stores/useAuthStore';

axios.defaults.headers['Content-Type'] = 'application/json;charset=utf-8'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  // 为了方便后端调试 暂时不设置请求超时时间
  // timeout: 5000, // 请求超时时间
});

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 在请求发送之前做一些处理，比如添加 token
    const authStore = useAuthStore()
    const token = authStore.token
    
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // 如果请求参数是 FormData 的话，设置 Content-Type 为 'multipart/form-data'
    if (config.data instanceof FormData) {
      config.headers['Content-Type'] = 'multipart/form-data';
    }

    // 一些自定义请求头
    // config.headers["X-App-Id"] = import.meta.env.VITE_APP_ID;

    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  response => {
    const ajaxResult = response.data;
    
    if (ajaxResult.code == 401) { //01 Unauthorized 需要登录
      setTimeout(() => {
        // 重定向到登录页面
        window.location.href = '#/login';   // 注：在history模式下，不需要携带#
      }, 2000); // 等待2秒
    }
    if (ajaxResult.code !== 200) {
      console.log('请求失败：', ajaxResult.msg)
      // 直接返回响应，不抛出错误，由调用者进行处理(Notify.create()弹出错误信息）
    }
    return ajaxResult;
  },
  error => {
    console.log('错误信息：', error)
    if(error.status == 401){    // 如果后端报错401，则AxiosError 的code是401，则需要重新登录
      Notify.create({
        position: 'top',
        type: 'negative',
        message: '登录过期，请重新登录',
      });
      setTimeout(() => {
        // 重定向到登录页面
        window.location.href = '#/login';   // 注：在history模式下，不需要携带#
      }, 2000); // 等待2秒
    }
    // 如果请求失败，直接返回 Promise.reject，其中包含 Axios 的错误对象
    return Promise.reject(error);
  }
);

export default request;
