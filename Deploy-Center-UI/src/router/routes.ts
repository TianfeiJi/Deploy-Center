import { RouteRecordRaw } from 'vue-router';
import settingChildrenRoutes from './settingChildrenRoutes'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/DashboardPage.vue') }],
  },
  {
    path: '/login',
    component: () => import('layouts/EmptyLayout.vue'),
    children: [{ path: '', component: () => import('pages/LoginPage.vue') }],
  },
  {
    path: '/dashboard',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/DashboardPage.vue') }],
  },
  {
    path: '/topology',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/TopologyPage.vue') }],
  },
  {
    path: '/projects',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/ProjectCenterPage.vue') }],
  },
  {
    path: '/project/deploy/:id',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/ProjectDeployConsolePage.vue') }],
  },
  {
    path: '/tasks',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/DeployTaskPage.vue') }],
  },
  {
    path: '/deployLog',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/DeployLogPage.vue') }],
  },
  {
    path: '/document',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/DocumentPage.vue'), children: [{ path: '', component: () => import('pages/documents/AboutPage.vue') }] },  // 默认选择
      { path: 'systemDesign', component: () => import('pages/DocumentPage.vue'), children: [{ path: '', component: () => import('pages/documents/SystemDesignPage.vue') }]},
      { path: 'faq', component: () => import('pages/DocumentPage.vue'), children: [{ path: '', component: () => import('pages/documents/FAQPage.vue') }]},
      { path: 'feedback', component: () => import('pages/DocumentPage.vue'), children: [{ path: '', component: () => import('pages/documents/FeedbackPage.vue') }]},
      { path: 'versionHistory', component: () => import('pages/DocumentPage.vue'), children: [{ path: '', component: () => import('pages/documents/VersionHistoryPage.vue') }]},
      { path: 'updatePlan', component: () => import('pages/DocumentPage.vue'), children: [{ path: '', component: () => import('pages/documents/UpdatePlanPage.vue') }]},
      { path: 'about', component: () => import('pages/DocumentPage.vue'), children: [{ path: '', component: () => import('pages/documents/AboutPage.vue') }]},
    ]
  },
  {
    path: '/setting',
    meta: {
      requiresRoles: ["admin"],
    },
    component: () => import('layouts/MainLayout.vue'),
    children: settingChildrenRoutes
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
