import { route } from 'quasar/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';
import {Notify} from 'quasar';
import routes from './routes';
import { useLoginUserStore } from 'src/stores/useLoginUserStore';
import { getUser } from 'src/api/userApi';


/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory);

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  // 添加全局前置守卫
  Router.beforeEach(async (to, from, next) => {
    const requiredRoles = to.meta.requiresRoles as string[] | undefined;

    const loginUserStore = useLoginUserStore();

    let userRole = '';

    // 有用户缓存才发请求（避免未登录用户多请求一次）
    if (loginUserStore.loginUser?.id) {
      try {
        const response = await getUser(loginUserStore.loginUser.id);
        userRole = response.data?.role ?? '';
      } catch (e) {
        console.error('获取用户信息失败', e);
        Notify.create({ message: '身份校验失败，请重新登录', color: 'negative' });
        // 清除用户信息
        loginUserStore.clearLoginUser();

        return next('/login');
      }
    }

    // 若有角色要求，且当前用户不在要求角色中
    if (requiredRoles?.length && !requiredRoles.includes(userRole)) {
      Notify.create({ message: '您没有权限访问该页面', color: 'warning' });
      return next('/');
    }

    next();
  });

  return Router;
});
