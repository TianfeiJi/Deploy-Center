<template>
  <q-page class="settings-page q-pa-md">
    <div class="row no-wrap" style="height: 100%">
      <!-- 自定义侧边栏 -->
      <div class="sidebar column q-pa-md">
        <div class="menu-list">
          <div
            v-for="item in menuItems"
            :key="item.value"
            class="menu-item"
            :class="{ active: activeTab === item.value }"
            @click="goToPage(item.value)"
          >
            <q-icon :name="item.icon" size="1.1rem" class="q-mr-sm" />
            <span>{{ item.label }}</span>
          </div>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="content-area col">
        <router-view />
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const activeTab = ref<string>('')
const router = useRouter()
const route = useRoute()

const menuItems = [
  { label: '关于', icon: 'fa-solid fa-info-circle', value: '/document/about' },
  { label: '系统设计', icon: 'fa-solid fa-diagram-project', value: '/document/systemDesign' },
  { label: 'FAQ', icon: 'fa-solid fa-question-circle', value: '/document/faq' },
  { label: '意见反馈', icon: 'fa-solid fa-comment-dots', value: '/document/feedback' },
  { label: '更新计划', icon: 'fa-solid fa-calendar-check', value: '/document/updatePlan' },
  { label: '版本历史', icon: 'fa-solid fa-history', value: '/document/versionHistory' },
];

// 获取第一个菜单项的路径
const defaultTab = menuItems[0].value;

// 监听路由变化，更新activeTab
watch(() => route.path, (newPath) => {
  // 如果当前路由在菜单项中，更新activeTab
  if (menuItems.some(item => item.value === newPath)) {
    activeTab.value = newPath;
  } else {
    // 如果当前路由不在菜单项中，恢复到默认的第一个菜单项
    activeTab.value = defaultTab;
    router.push(defaultTab);
  }
});

// 在组件加载时，根据当前路由设置activeTab
onMounted(() => {
  // 如果当前路由在菜单项中，设置activeTab
  if (menuItems.some(item => item.value === route.path)) {
    activeTab.value = route.path;
  } else {
    // 如果当前路由不在菜单项中，设置为默认的第一个菜单项
    activeTab.value = defaultTab;
    router.push(defaultTab);
  }
});

const goToPage = (page: string) => {
  activeTab.value = page;
  router.push(page);
};
</script>

<style scoped>
.sidebar {
  width: 240px;
  background-color: #fafafa;
  border-right: 1px solid #e0e0e0;
  border-radius: 8px 0 0 8px;
  box-shadow: inset -1px 0 0 rgba(0, 0, 0, 0.03);
}

.menu-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.menu-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  font-size: 0.95rem;
  border-radius: 6px;
  color: #444;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu-item:hover {
  background-color: #f0f0f0;
}

.menu-item.active {
  background-color: #e3f2fd;
  color: #1976d2;
  font-weight: 600;
}

.content-area {
  flex: 1;
  padding: 32px;
  background-color: #fff;
  border-radius: 0 8px 8px 0;
  box-shadow: 0 0 0 rgba(0, 0, 0, 0.03);
}
</style>