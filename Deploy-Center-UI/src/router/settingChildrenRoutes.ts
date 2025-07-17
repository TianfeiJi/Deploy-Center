import { RouteRecordRaw } from 'vue-router';


const settingChildrenRoutes: RouteRecordRaw[] = [
  {
    path: '/setting/systemConfig',
    component: () => import('pages/SettingPage.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/settings/SystemConfigSettingsPage.vue'),
        meta: {
          title: '系统配置',
          icon: 'fa-solid fa-gear',
        },
      },
    ],
  },
  {
    path: '/setting/security',
    component: () => import('pages/SettingPage.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/settings/SecuritySettingsPage.vue'),
        meta: {
          title: '安全设置',
          icon: 'fa-solid fa-shield-halved',
        },
      },
    ],
  },
  {
    path: '/setting/user',
    component: () => import('pages/SettingPage.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/settings/UserSettingsPage.vue'),
        meta: {
          title: '用户管理',
          icon: 'fa-solid fa-users',
        },
      },
    ],
  },
  {
    path: '/setting/agent',
    component: () => import('pages/SettingPage.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/settings/AgentSettingsPage.vue'),
        meta: {
          title: 'Agent管理',
          icon: 'fa-solid fa-server',
        },
      },
    ],
  },
  // {
  //   path: '/setting/selfDeploy',
  //   component: () => import('pages/SettingPage.vue'),
  //   children: [
  //     {
  //       path: '',
  //       component: () => import('src/pages/todo/SelfDeploySettingsPage.vue'),
  //       meta: {
  //         title: '自我部署',
  //         icon: 'fa-solid fa-cloud-arrow-up',
  //       },
  //     },
  //   ],
  // },

];


export default settingChildrenRoutes;