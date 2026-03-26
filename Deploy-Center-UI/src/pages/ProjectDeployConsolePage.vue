<template>
  <q-page class="project-deploy-console-page">
    <div v-if="projectLoaded" class="page-shell">
      <ProjectSidebar :project="projectDetail" :editing="isSidebarEditing" :form="detailForm"
        @start-edit="startSidebarEdit" @cancel-edit="cancelSidebarEdit" @save-edit="saveSidebarDetail" />

      <ProjectWorkspaceLayout :project-name="projectDetail.project_name"
        :project-group="projectDetail.project_group || '-'" :tabs="tabs" :active-tab="activeTab"
        @update:active="handleActiveTabChange" @refresh="refreshAll">
        <template v-if="activeTab === 'deploy'">
          <component :is="currentProjectDeployPanel" v-if="projectDetail.id && currentProjectDeployPanel"
            :project-id="projectDetail.id" @deploy-success="refreshAll" />

          <div v-else class="unsupported-panel">
            不支持的项目类型：{{ projectDetail.project_type || '-' }}
          </div>
        </template>

        <template v-else-if="activeTab === 'history'">
          <ProjectDeployHistoryPanel v-if="projectDetail.id" :project-id="projectDetail.id" />
        </template>
      </ProjectWorkspaceLayout>
    </div>

    <div v-else class="loading">
      <q-spinner color="primary" size="40px" />
      <div class="loading-text">加载项目信息中...</div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { Notify } from 'quasar'
import { storeToRefs } from 'pinia'
import { useAgentStore } from 'stores/useAgentStore'
import { useRoute } from 'vue-router'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'

import ProjectSidebar from 'components/deploy/ProjectSidebar.vue'
import ProjectWorkspaceLayout from 'components/deploy/ProjectWorkspaceLayout.vue'
import WebProjectDeployPanel from 'components/deploy/panels/WebProjectDeployPanel.vue'
import JavaProjectDeployPanel from 'components/deploy/panels/JavaProjectDeployPanel.vue'
import PythonProjectDeployPanel from 'src/components/deploy/panels/PythonProjectDeployPanel.vue'
import ProjectDeployHistoryPanel from 'components/deploy/panels/ProjectDeployHistoryPanel.vue'

type TabKey = 'deploy' | 'history'

const route = useRoute()
const agentStore = useAgentStore()
const { currentAgent } = storeToRefs(agentStore)

const projectLoaded = ref(false)
const activeTab = ref<TabKey>('deploy')
const isSidebarEditing = ref(false)

type ProjectDetail = {
  id: string
  project_type: 'java' | 'python' | 'web'
  project_name: string
  project_code: string
  project_group?: string
  [key: string]: any
}

const projectDetail = ref<ProjectDetail>({} as ProjectDetail)
const detailForm = ref<ProjectDetail>({} as ProjectDetail)

const tabs = ref([
  { key: 'deploy', label: '部署' },
  { key: 'history', label: '部署历史' }
])

function getAgentApi() {
  return provideCurrentAgentProxyApi()
}

function handleActiveTabChange(v: TabKey) {
  activeTab.value = v
}

function getRouteProjectId(): string {
  return String(route.params.id || route.query.id || '').trim()
}

/**
 * 根据项目类型动态选择部署面板
 */
const currentProjectDeployPanel = computed(() => {
  const rawType =
    projectDetail.value.project_type ||
    projectDetail.value.type ||
    projectDetail.value.projectType ||
    ''

  const projectType = String(rawType).toLowerCase().trim()

  if (projectType.includes('java')) {
    return JavaProjectDeployPanel
  }

  if (projectType.includes('web')) {
    return WebProjectDeployPanel
  }

  if (projectType.includes('python')) {
    return PythonProjectDeployPanel
  }

  return null
})

async function fetchProjectDetail() {
  const id = getRouteProjectId()

  if (!id) {
    projectLoaded.value = false
    Notify.create({
      type: 'negative',
      message: '缺少项目ID',
      position: 'top'
    })
    return
  }

  if (!currentAgent.value?.id) {
    projectLoaded.value = false
    return
  }

  try {
    const data = await getAgentApi().fetchProjectDetail(id)
    projectDetail.value = { ...data }
    detailForm.value = { ...data }
    projectLoaded.value = true
  } catch (e) {
    console.error('获取项目详情失败', e)
    projectLoaded.value = false
    Notify.create({
      type: 'negative',
      message: '加载项目信息失败',
      position: 'top'
    })
  }
}

function startSidebarEdit() {
  detailForm.value = { ...projectDetail.value }
  isSidebarEditing.value = true
}

function cancelSidebarEdit() {
  detailForm.value = { ...projectDetail.value }
  isSidebarEditing.value = false
}

async function saveSidebarDetail() {
  try {
    projectDetail.value = { ...detailForm.value }
    isSidebarEditing.value = false

    Notify.create({
      type: 'positive',
      message: '保存成功',
      position: 'top'
    })
  } catch (e) {
    console.error('保存失败', e)
    Notify.create({
      type: 'negative',
      message: '保存失败',
      position: 'top'
    })
  }
}

async function refreshAll() {
  await fetchProjectDetail()
  Notify.create({
    type: 'positive',
    message: '已刷新',
    position: 'top'
  })
}

watch(
  [() => route.fullPath, () => currentAgent.value?.id],
  async ([, agentId]) => {
    const id = getRouteProjectId()
    if (!id || !agentId) {
      projectLoaded.value = false
      return
    }
    await fetchProjectDetail()
  },
  { immediate: true }
)
</script>

<style scoped>
.project-deploy-console-page {
  min-height: 100vh;
  padding: 18px;
  background:
    radial-gradient(circle at top left, rgba(14, 165, 233, 0.06), transparent 24%),
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.05), transparent 22%),
    linear-gradient(180deg, #f8fbff 0%, #f1f5f9 100%);
}

.page-shell {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 18px;
  min-height: calc(100vh - 36px);
}

.loading {
  min-height: calc(100vh - 36px);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 12px;
  color: #64748b;
}

.loading-text {
  font-size: 14px;
}
</style>