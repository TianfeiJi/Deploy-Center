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

function redirectToLogin(delay = 2000) {
  setTimeout(() => {
    const isHashMode = window.location.href.includes('#/');
    if (isHashMode) {
      window.location.href = '#/login';
    } else {
      window.location.href = '/login';
    }
  }, delay);
}

// 响应拦截器
request.interceptors.response.use(
  response => {
    const ajaxResult = response.data;
    
    // 业务错误
    if (ajaxResult.code !== 200) {
      Notify.create({ type: 'negative', message: ajaxResult.msg || '请求失败' });
    }

    return ajaxResult;
  },
  error => {
    // 真正的网络异常 或 HTTP 401、500等
    console.log('捕获到错误：', error);

    if(error.status == 401){    // 如果后端报错401，则AxiosError 的code是401，则需要重新登录
      Notify.create({type: 'negative', message: '登录过期，请重新登录'});

      // 重定向到login页
      redirectToLogin();
    } else {
      // 从后端响应中提取业务错误消息进行提示
      Notify.create({type: 'negative', message: error?.response?.data?.msg || error?.message || '请求失败，请检查网络或稍后重试' });
    }

    // 如果请求失败，直接返回 Promise.reject，其中包含 Axios 的错误对象
    return Promise.reject(error); // 只有 HTTP 错误才抛
  }
);

export default request;
