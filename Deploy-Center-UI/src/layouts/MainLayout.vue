<template>
  <q-layout view="hHh lpR fFf" class="bg-grey-2">
    <q-header elevated class="bg-white text-grey-8 q-py-xs app-header" height-hint="58">
      <q-toolbar class="header-toolbar no-wrap">
        <!-- 左侧：Logo + 版本 -->
        <div class="header-left row items-center no-wrap">
          <q-btn flat no-caps no-wrap class="logo-btn" to="/topology">
            <q-toolbar-title shrink class="text-weight-bold header-title">
              Deploy Center UI
            </q-toolbar-title>
          </q-btn>

          <div class="text-caption text-grey-7 version-text">
            <a
              :href="`https://github.com/TianfeiJi/Deploy-Center/tags`"
              target="_blank"
              class="text-grey-7 version-link"
            >
              {{ version }}
            </a>
          </div>
        </div>

        <!-- Agent 筛选 -->
        <q-btn flat dense no-caps no-wrap class="agent-switcher" :ripple="false">
          <q-avatar
            size="26px"
            :color="currentHealth === 'healthy' ? 'green-5' : 'grey-5'"
            text-color="white"
          >
            <q-icon name="dns" size="18px" />
          </q-avatar>

          <div class="q-ml-sm column agent-text-wrap">
            <span class="text-body2 text-weight-medium agent-text">
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
              <q-item
                v-for="agent in agentList"
                :key="agent.id"
                clickable
                v-close-popup
                @click="selectAgent(agent.id)"
              >
                <q-item-section avatar style="min-width: 16px; padding-right: 8px">
                  <q-avatar
                    size="24px"
                    :color="agentRuntimeInfoMap[agent.id]?.health === 'healthy' ? 'green-5' : 'grey-5'"
                    text-color="white"
                  >
                    <q-icon name="dns" size="16px" />
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-body2">
                    {{ agent.name }} ({{ agent.ip }})
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>

        <q-space class="toolbar-space" />

        <!-- 导航区域 -->
        <div class="nav-btns row no-wrap items-center">
          <q-btn
            flat
            no-caps
            no-wrap
            :ripple="false"
            to="/dashboard"
            class="nav-btn"
            :class="{ 'active-nav': route.path === '/dashboard' }"
          >
            <q-icon name="dashboard" size="20px" />
            <span class="q-ml-sm nav-text">仪表盘</span>
          </q-btn>

          <q-btn
            flat
            no-caps
            no-wrap
            :ripple="false"
            to="/projects"
            class="nav-btn"
            :class="{ 'active-nav': route.path === '/projects' }"
          >
            <q-icon name="apps" size="20px" />
            <span class="q-ml-sm nav-text">项目中心</span>
          </q-btn>

          <q-btn
            flat
            no-caps
            no-wrap
            :ripple="false"
            to="/tasks"
            class="nav-btn"
            :class="{ 'active-nav': route.path === '/tasks' }"
          >
            <q-icon name="task_alt" size="20px" />
            <span class="q-ml-sm nav-text">部署任务</span>
          </q-btn>

          <q-btn
            flat
            no-caps
            no-wrap
            :ripple="false"
            to="/deployLog"
            class="nav-btn"
            :class="{ 'active-nav': route.path === '/deployLog' }"
          >
            <q-icon name="description" size="20px" />
            <span class="q-ml-sm nav-text">部署日志</span>
          </q-btn>
        </div>

        <q-space class="toolbar-space" />

        <!-- 右侧 -->
        <div class="header-right row items-center no-wrap">
          <div class="greeting-text">
            {{ greetingText }}
          </div>

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

          <div class="header-icon-group row items-center no-wrap">
            <q-btn round dense flat color="grey-8" icon="article" to="/document">
              <q-tooltip>文档</q-tooltip>
            </q-btn>
          </div>

          <div v-if="isAdminUser" class="header-icon-group row items-center no-wrap">
            <q-btn round dense flat color="grey-8" icon="settings" to="/setting/systemConfig">
              <q-tooltip>设置</q-tooltip>
            </q-btn>
          </div>
        </div>
      </q-toolbar>
    </q-header>

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
import { version } from '../../package.json';
import { resetAllStores } from 'src/utils/resetAllStores';

const route = useRoute();
const router = useRouter();

const agentStore = useAgentStore();
const { agentList, currentAgent, agentRuntimeInfoMap } = storeToRefs(agentStore);

const selectAgent = async (agentId: number) => {
  const oldAgentId = currentAgent.value?.id;

  if (!agentId || agentId === oldAgentId) return;

  // 如果当前在项目部署控制台页，切换 Agent 后直接返回项目列表
  const isDeployPage = route.path.startsWith('/project/deploy/')
  if (isDeployPage) {
    Notify.create({
      type: 'info',
      message: '已切换 Agent，请重新选择项目',
      position: 'top',
      timeout: 1200,
    })

    await router.replace('/project')
  }

  agentStore.setCurrentAgentById(agentId);
  sessionStorage.setItem('selectedAgentId', String(agentId));
};

const currentHealth = computed(() =>
  currentAgent.value?.id !== undefined
    ? agentRuntimeInfoMap.value[currentAgent.value.id]?.health
    : undefined
);

const greetingText = ref('');
const setGreeting = (nickname: string) => {
  const hour = new Date().getHours();
  if (hour > 6 && hour < 12) greetingText.value = '☀️上午好，' + nickname;
  else if (hour >= 12 && hour < 18) greetingText.value = '🌤️下午好，' + nickname;
  else greetingText.value = '🌙晚上好，' + nickname;
};

const loginUserStore = useLoginUserStore();
const { loginUser } = storeToRefs(loginUserStore);

watch(
  loginUser,
  (newLoginUser) => {
    if (newLoginUser?.nickname) setGreeting(newLoginUser.nickname);
  },
  { immediate: true }
);

const systemConfigStore = useSystemConfigStore();
watch(
  () => systemConfigStore.configMap,
  () => {
    const enableGlobalWatermark = systemConfigStore.get('enable_global_watermark') === true;
    const nickname = loginUser.value?.nickname;
    if (enableGlobalWatermark && nickname) {
      observeWatermark({ text: nickname, opacity: 0.1, fontSize: 18, rotate: -30 });
    }
  },
  { immediate: true, deep: true }
);

const isAdminUser = ref(false);
onMounted(async () => {
  const agentStore = useAgentStore();
  await agentStore.getAllAgentList();
  await agentStore.getAllAgentRuntimeInfo();

  const storedAgentId = Number(sessionStorage.getItem('selectedAgentId'));
  const selectedAgentFromStorage = agentList.value.find((a) => a.id === storedAgentId);
  if (selectedAgentFromStorage) agentStore.setCurrentAgentById(selectedAgentFromStorage.id);
  else if (agentList.value.length > 0) {
    agentStore.setCurrentAgentById(agentList.value[0].id);
    sessionStorage.setItem('selectedAgentId', String(agentList.value[0].id));
  }

  if (!loginUser.value) {
    router.replace('/login');
    return;
  }

  try {
    if (!Object.keys(systemConfigStore.configMap).length) await systemConfigStore.loadConfig();
    const response = await getUser(loginUser.value.id);
    isAdminUser.value = response.data.role === 'admin';
  } catch (error) {
    console.error(error);
    router.replace('/login');
  }
});

const showProfileDialog = ref(false);
const openProfileDialog = () => (showProfileDialog.value = true);

const goToNotificationPage = () => {
  Notify.create({ message: '尚未实现，敬请期待', type: 'warning', position: 'top' });
};

const handleConfirmLogout = () => {
  Dialog.create({
    title: '确认退出',
    message: '确定要退出当前账号吗?',
    cancel: { label: '取消', flat: true, textColor: 'negative' },
    ok: { label: '确定', flat: true, textColor: 'positive' },
    persistent: true
  }).onOk(() => {
    logout().then(() => {
      Notify.create({ message: '已退出登录', type: 'positive', position: 'top' });
      router.push('/login');
      resetAllStores();
      sessionStorage.clear();
    });
  });
};
</script>

<style scoped>
.app-header {
  backdrop-filter: blur(10px);
}

.header-toolbar {
  min-height: 58px;
  flex-wrap: nowrap;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.header-toolbar::-webkit-scrollbar {
  display: none;
}

.header-left,
.agent-switcher,
.nav-btns,
.header-right,
.header-icon-group {
  flex-shrink: 0;
}

.header-left {
  margin-right: 0.5rem;
}

.logo-btn {
  padding: 0 8px;
  margin-right: 0.5rem;
  min-height: 36px;
  display: flex;
  align-items: center;
}

.header-title {
  font-size: 1.05rem;
  line-height: 1.2;
}

.version-text {
  white-space: nowrap;
}

.version-link {
  text-decoration: none;
  cursor: pointer;
}

.agent-switcher {
  max-width: 320px;
}

.agent-text-wrap {
  min-width: 0;
  max-width: 220px;
}

.agent-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-btns {
  gap: 2px;
}

.nav-btn {
  transition: background-color 0.3s ease;
  border-radius: 10px;
  padding: 0 10px;
  min-height: 38px;
}

.nav-btn:hover,
.nav-btn.active-nav {
  background-color: rgba(0, 150, 136, 0.1);
  color: #009688;
}

.nav-text {
  white-space: nowrap;
}

.toolbar-space {
  min-width: 10px;
}

.header-right {
  gap: 2px;
}

.greeting-text {
  margin-right: 1rem;
  white-space: nowrap;
}

.header-icon-group {
  margin-left: 0.2rem;
}

.avatar-shadow {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

/* <= 1200px */
@media (max-width: 1199px) {
  .greeting-text {
    display: none;
  }

  .agent-text-wrap {
    max-width: 170px;
  }

  .nav-btn {
    padding: 0 8px;
  }
}

/* <= 900px */
@media (max-width: 900px) {
  .version-text {
    display: none;
  }

  .agent-text-wrap {
    display: none;
  }

  .nav-text {
    display: none;
  }

  .nav-btn {
    min-width: 38px;
    padding: 0 8px;
  }

  .header-title {
    font-size: 0.98rem;
  }
}

/* <= 600px */
@media (max-width: 600px) {
  .header-toolbar {
    padding-left: 8px;
    padding-right: 8px;
  }

  .header-left {
    margin-right: 0.25rem;
  }

  .logo-btn {
    margin-right: 0.25rem;
  }

  .header-title {
    font-size: 0.92rem;
  }

  .agent-switcher {
    padding-left: 6px;
    padding-right: 6px;
  }

  .nav-btn {
    min-width: 34px;
    min-height: 34px;
    padding: 0 6px;
  }

  .nav-btn .q-icon {
    font-size: 18px;
  }
}
</style>