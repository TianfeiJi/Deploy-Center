<template>
  <!-- Header + View 布局 -->
  <q-layout view="hHh lpR fFf" class="bg-grey-2">
    <!-- Header区域 -->
    <q-header elevated class="bg-white text-grey-8 q-py-xs" height-hint="58">
      <q-toolbar>
        <div class="row items-center" style="margin-right: 0.5rem;">
          <q-btn flat no-caps no-wrap style="padding: 0; margin-right: 0.5rem;" to="/topology">
            <q-toolbar-title shrink class="text-weight-bold">
              Deploy Center UI
            </q-toolbar-title>
          </q-btn>

          <div class="text-caption text-grey-7">
            <a :href="`https://github.com/TianfeiJi/Deploy-Center/tags`" target="_blank" class="text-grey-7"
              style="text-decoration: none; cursor: pointer">
              {{ version }}
            </a>
          </div>
        </div>

        <!-- Agent 筛选 -->
        <q-btn flat dense no-caps no-wrap class="agent-switcher" :ripple="false">
          <q-avatar size="26px" :color="currentHealth === 'healthy' ? 'green-5' : 'grey-5'" text-color="white">
            <q-icon name="dns" size="18px" />
          </q-avatar>

          <div class="q-ml-sm column">
            <span class="text-body2 text-weight-medium">
              {{
                currentAgent
                  ? `${currentAgent.name} (${currentAgent.ip})`
                  : '未选择 Agent'
              }}
            </span>
          </div>

          <q-icon name="expand_more" size="18px" class="q-ml-xs" />

          <q-menu transition-show="jump-down">
            <q-list>
              <q-item v-for="agent in agentList" :key="agent.id" clickable v-close-popup
                @click="selectAgent(agent.id)">
                <q-item-section avatar style="min-width: 16px; padding-right: 8px">
                  <q-avatar size="24px"
                    :color="agentRuntimeInfoMap[agent.id]?.health === 'healthy' ? 'green-5' : 'grey-5'"
                    text-color="white">
                    <q-icon name="dns" size="16px" />
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-body2">{{ agent.name }} ({{ agent.ip }})</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>

        <q-space />

        <!-- 导航区域 -->
        <div class="nav-btns">
          <q-btn flat no-caps no-wrap :ripple="false" to="/dashboard" class="nav-btn"
            :class="{ 'active-nav': route.path === '/dashboard' }">
            <q-icon name="dashboard" size="20px" />
            <span class="q-ml-sm">仪表盘</span>
          </q-btn>
          <q-btn flat no-caps no-wrap :ripple="false" to="/project" class="nav-btn"
            :class="{ 'active-nav': route.path === '/project' }">
            <q-icon name="build" size="20px" />
            <span class="q-ml-sm">项目部署</span>
          </q-btn>
          <q-btn flat no-caps no-wrap :ripple="false" to="/deployHistory" class="nav-btn"
            :class="{ 'active-nav': route.path === '/deployHistory' }">
            <q-icon name="history" size="20px" />
            <span class="q-ml-sm">部署历史</span>
          </q-btn>
          <q-btn flat no-caps no-wrap :ripple="false" to="/deployLog" class="nav-btn"
            :class="{ 'active-nav': route.path === '/deployLog' }">
            <q-icon name="description" size="20px" />
            <span class="q-ml-sm">部署日志</span>
          </q-btn>
          <!-- 
            <q-btn flat no-caps no-wrap :ripple=false to="/apiLog" class="nav-btn" :class="{ 'active-nav': route.path === '/apiLog'} ">
              <q-icon name="description" size="20px" />
              <span class="q-ml-sm">Api日志</span>
            </q-btn>
          -->
        </div>

        <q-space />

        <!-- Greeting -->
        <div style="margin-right: 1rem">
          {{ greetingText }}
        </div>

        <!-- 头像 -->
        <q-btn round dense flat>
          <q-avatar size="35px" class="avatar-shadow">
            <img src="https://cdn.quasar.dev/img/boy-avatar.png" />
          </q-avatar>
          <q-tooltip>用户</q-tooltip>
          <q-menu>
            <q-list style="min-width: 100px">
              <q-item clickable v-close-popup @click="openProfileDialog">
                <q-item-section>个人信息</q-item-section>
              </q-item>
              <q-item clickable v-close-popup @click="goToNotificationPage">
                <q-item-section>消息通知</q-item-section>
              </q-item>
              <q-item clickable v-close-popup @click="handleConfirmLogout">
                <q-item-section>退出登录</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>

        <div class="q-gutter-sm row items-center no-wrap" style="margin-left: 0.2rem">
          <q-btn round dense flat color="grey-8" icon="article" to="/document">
            <q-tooltip>文档</q-tooltip>
          </q-btn>
        </div>

        <div v-if="isAdminUser" class="q-gutter-sm row items-center no-wrap">
          <q-btn round dense flat color="grey-8" icon="settings" to="/setting/systemConfig">
            <q-tooltip>设置</q-tooltip>
          </q-btn>
        </div>
      </q-toolbar>
    </q-header>

    <!-- 用户个人信息对话框  -->
    <UserProfileDialog v-model="showProfileDialog" />

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { ref, watch, onMounted, computed } from 'vue';
import { Notify, Dialog } from 'quasar';
import { useRoute, useRouter } from 'vue-router';
import { logout } from 'src/api/authApi';
import { getUser } from 'src/api/userApi';
import UserProfileDialog from 'src/components/UserProfileDialog.vue';
import { useLoginUserStore } from 'src/stores/useLoginUserStore';
import { useAgentStore } from 'src/stores/useAgentStore';
import { useSystemConfigStore } from 'stores/useSystemConfigStore';
import { observeWatermark } from 'src/utils/watermark';
import { version } from '../../package.json'
import { resetAllStores } from 'src/utils/resetAllStores';

const route = useRoute();
const router = useRouter();

const agentStore = useAgentStore();

// 解构出 agentStore 中的 agentList、currentAgent、agentRuntimeInfoMap
// 使用 storeToRefs 保证它们在组合式 API 中依然保持响应式引用
const { agentList, currentAgent, agentRuntimeInfoMap } = storeToRefs(agentStore);

// 选择agent
const selectAgent = (agentId: number) => {
  // 设置当前选中的agent
  agentStore.setCurrentAgentById(agentId);
  // 保存当前选中的agentId
  sessionStorage.setItem('selectedAgentId', String(agentId));
};

const currentHealth = computed(() =>
  currentAgent.value?.id !== undefined
    ? agentRuntimeInfoMap.value[currentAgent.value.id]?.health
    : undefined
);

// 初始化问候语
const greetingText = ref('');

const setGreeting = (nickname: string) => {
  const hour = new Date().getHours();
  if (hour > 6 && hour < 12) {
    greetingText.value = '☀️上午好，' + nickname;
  } else if (hour >= 12 && hour < 18) {
    greetingText.value = '🌤️下午好，' + nickname;
  } else {
    greetingText.value = '🌙晚上好，' + nickname;
  }
};

// 获取 loginUserStore
const loginUserStore = useLoginUserStore();
const { loginUser } = storeToRefs(loginUserStore);

// 监听用户变化，设置问候语
watch(
  loginUser,
  (newLoginUser) => {
    if (newLoginUser && newLoginUser.nickname) {
      setGreeting(newLoginUser.nickname);
    }
  },
  { immediate: true } // 立即执行一次，以处理页面加载时的情况
);

// 监听系统配置变化 → 判断是否开启水印
const systemConfigStore = useSystemConfigStore();
watch(
  () => systemConfigStore.configMap,
  () => {
    const enableGlobalWatermark =
      systemConfigStore.get('enable_global_watermark') === true;
    const nickname = loginUser.value?.nickname;
    if (enableGlobalWatermark && nickname) {
      observeWatermark({
        text: nickname,
        opacity: 0.1,
        fontSize: 18,
        rotate: -30,
      });
    }
  },
  { immediate: true, deep: true }
);

const isAdminUser = ref(false);
onMounted(async () => {
  const agentStore = useAgentStore();
  // 1. 获取所有Agent列表
  await agentStore.getAllAgentList();
  // 2. 获取所有Agent运行时信息
  await agentStore.getAllAgentRuntimeInfo();
  // 3. 设置当前选中的 Agent
  // 3.1 尝试从 sessionStorage 中读取上次选中的 Agent ID
  const storedAgentId = Number(sessionStorage.getItem('selectedAgentId'));
  // 3.2 在当前 agentList 中查找匹配的 Agent
  const selectedAgentFromStorage = agentList.value.find((a) => a.id === storedAgentId);
  if (selectedAgentFromStorage) {
    // 3.3 若存在匹配项，则设为当前 Agent
    agentStore.setCurrentAgentById(selectedAgentFromStorage.id);
  } else if (agentList.value.length > 0) {
    // 3.4 否则默认选择第一个 Agent，并将selectedAgentId写入 sessionStorage
    agentStore.setCurrentAgentById(agentList.value[0].id);
    sessionStorage.setItem('selectedAgentId', String(agentList.value[0].id));
  }

  // ✅ 判断登录用户是否存在
  if (!loginUser.value) {
    console.warn('未获取到登录用户，跳转登录页');
    router.replace('/login');
    return;
  }

  try {
    // ✅ 加载系统配置（如果未加载过）
    if (!Object.keys(systemConfigStore.configMap).length) {
      await systemConfigStore.loadConfig();
    }

    console.log('MainLayout - 当前登录的用户：', loginUser.value);

    // ✅ 请求后端确认角色
    const response = await getUser(loginUser.value.id);
    const user = response.data;

    if (user.role === 'admin') {
      isAdminUser.value = true;
    }
  } catch (error) {
    console.error('获取用户信息或系统配置失败', error);

    // 如果是 401 或 token 无效，也跳转登录（防止中间 token 失效）
    router.replace('/login');
  }
});

const showProfileDialog = ref(false);
const openProfileDialog = () => (showProfileDialog.value = true);

const goToNotificationPage = () => {
  Notify.create({
    message: '尚未实现，敬请期待',
    type: 'warning',
    position: 'top',
  });
};

const handleConfirmLogout = () => {
  Dialog.create({
    title: '确认退出',
    message: '确定要退出当前账号吗?',
    cancel: {
      label: '取消', // 自定义取消按钮的文本
      flat: true, // 设置为扁平按钮
      textColor: 'negative', // 设置按钮文字颜色
    },
    ok: {
      label: '确定',
      flat: true,
      textColor: 'positive',
    },
    persistent: true, // 点击对话框外部不关闭对话框
  }).onOk(() => {
    logout().then(() => {
      Notify.create({
        message: '已退出登录',
        type: 'positive',
        position: 'top',
      });

      // ## 退出登录后执行的操纵：
      // 1. 重定向到登录页面
      router.push('/login');

      // 2.清除所有store
      resetAllStores();

      // 3. 清除所有sessionStorage存储的数据
      sessionStorage.clear();
    });
  });
};
</script>

<style scoped>
.nav-btn {
  transition: background-color 0.3s ease;
}

/* 设置选择的导航的样式 文字色和背景色 浅绿*/
.nav-btn:hover,
.nav-btn.active-nav {
  background-color: rgba(0, 150, 136, 0.1);
  color: #009688;
}
</style>
