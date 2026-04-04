<template>
  <q-page class="project-deploy-console-page">
    <div v-if="projectLoaded" class="page-shell">
      <section class="console-card">
        <div class="console-header">
          <div class="console-main">
            <div class="console-title-row">
              <h1 class="console-title">
                {{ projectDetail.project_name || '-' }}
              </h1>

              <div class="title-runtime">
                <template v-if="runtimeStatus === 'Checking'">
                  <q-spinner color="grey-5" size="16px" />
                  <span class="runtime-checking-text">检测中</span>
                </template>

                <template v-else>
                  <span class="status-pill" :class="statusPillClass">
                    {{ runtimeStatusText || 'Unknown' }}
                  </span>
                </template>
              </div>
            </div>

            <div class="console-submeta">
              <span class="type-text">{{ projectTypeLabel }}</span>

              <span class="submeta-divider">·</span>

              <span class="code-text">
                {{ projectDetail.project_code || 'NO_CODE' }}
              </span>

              <template v-if="projectDetail.project_group">
                <span class="submeta-divider">·</span>
                <span class="submeta-item">
                  {{ projectDetail.project_group }}
                </span>
              </template>

              <template v-if="deployText">
                <span class="submeta-divider">·</span>
                <span class="submeta-item">
                  最近部署：{{ deployText }}
                </span>
              </template>
            </div>
          </div>

          <div class="console-right">
            <button
              class="header-btn header-btn-secondary"
              @click="openProjectDetailDialog"
            >
              详情
            </button>
          </div>
        </div>

        <div class="tab-bar">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-btn"
            :class="{ active: activeTab === tab.key }"
            @click="handleActiveTabChange(tab.key)"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="console-body">
          <template v-if="activeTab === 'deploy'">
            <component
              :is="currentProjectDeployPanel"
              v-if="projectDetail.id && currentProjectDeployPanel"
              :project-id="projectDetail.id"
            />

            <div v-else class="unsupported-panel">
              <div class="unsupported-title">暂不支持的项目类型</div>
              <div class="unsupported-desc">
                当前项目类型：{{ projectType || '-' }}
              </div>
            </div>
          </template>

          <template v-else-if="activeTab === 'tasks'">
            <DeployTaskPanel
              v-if="projectDetail.id"
              :project-id="projectDetail.id"
            />
          </template>

          <template v-else-if="activeTab === 'container_info'">
            <ContainerInfoPanel :project="projectDetail" />
          </template>

          <template v-else-if="activeTab === 'container_inspect'">
            <ContainerInspectPanel :project="projectDetail" />
          </template>

          <template v-else-if="activeTab === 'container_log'">
            <ContainerLogPanel :project="projectDetail"/>
          </template>

          <template v-else-if="activeTab === 'container_action'">
            <ContainerActionPanel
              :project="projectDetail"
              :runtime-status="runtimeStatus"
              @action-success="handleContainerActionSuccess"
            />
        </template>
        </div>
      </section>
    </div>

    <div v-else class="loading-wrap">
      <q-spinner color="primary" size="40px" />
      <div class="loading-text">加载项目信息中...</div>
    </div>

    <component
      v-if="currentDialogComponent"
      :is="currentDialogComponent"
      v-model="detailDialogVisible"
      :project="projectDetail"
      @saved="refreshAll"
      @deleted="handleDeleted"
    />
  </q-page>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Notify } from 'quasar'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import { useAgentStore } from 'stores/useAgentStore'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'

import type { PythonProject, JavaProject, WebProject } from 'src/types/Project.types'

import DeployTaskPanel from 'src/components/deploy/panels/DeployTaskPanel.vue'
import WebProjectDeployPanel from 'components/deploy/panels/WebProjectDeployPanel.vue'
import JavaProjectDeployPanel from 'components/deploy/panels/JavaProjectDeployPanel.vue'
import PythonProjectDeployPanel from 'src/components/deploy/panels/PythonProjectDeployPanel.vue'
import ContainerInfoPanel from 'src/components/deploy/panels/ContainerInfoPanel.vue'
import ContainerInspectPanel from 'src/components/deploy/panels/ContainerInspectPanel.vue'
import ContainerLogPanel from 'src/components/deploy/panels/ContainerLogPanel.vue'
import ContainerActionPanel from 'src/components/deploy/panels/ContainerActionPanel.vue'

import { projectDetailDialogMap } from 'src/registry/projectDetailDialogRegistry'

type TabKey = 'deploy' | 'tasks' | 'container_info' | 'container_inspect' | 'container_log' | 'container_action'
type ProjectDetail = PythonProject | JavaProject | WebProject
type ProjectType = keyof typeof projectDetailDialogMap

const route = useRoute()
const router = useRouter()
const agentStore = useAgentStore()
const { currentAgent } = storeToRefs(agentStore)

const projectLoaded = ref(false)
const activeTab = ref<TabKey>('deploy')
const detailDialogVisible = ref(false)

const projectDetail = ref<ProjectDetail>({} as ProjectDetail)
const runtimeStatus = ref<string>('Checking')

const tabs = ref<{ key: TabKey; label: string }[]>([
  { key: 'deploy', label: '部署' },
  { key: 'tasks', label: '部署任务' },
  { key: 'container_info', label: '容器信息' },
  { key: 'container_inspect', label: '容器 Inspect' },
  { key: 'container_log', label: '容器日志' },
  { key: 'container_action', label: '容器操作' },
])

function getAgentApi() {
  return provideCurrentAgentProxyApi()
}

function getRouteProjectId(): string {
  return String(route.params.id || route.query.id || '').trim()
}

function isWebProject(project: ProjectDetail): project is WebProject {
  return String(project.project_type || '').toLowerCase() === 'web'
}

function isContainerProject(project: ProjectDetail): project is PythonProject | JavaProject {
  const type = String(project.project_type || '').toLowerCase()
  return type === 'python' || type === 'java'
}

const projectType = computed<ProjectType | ''>(() => {
  const type = String(projectDetail.value.project_type || '').toLowerCase().trim()
  return type in projectDetailDialogMap ? (type as ProjectType) : ''
})

const projectTypeLabel = computed(() => {
  if (projectType.value === 'java') return 'Java'
  if (projectType.value === 'web') return 'Web'
  if (projectType.value === 'python') return 'Python'
  return '项目'
})

const runtimeStatusText = computed(() => {
  if (runtimeStatus.value === 'Checking') return '检测中'
  if (runtimeStatus.value === 'Unknown') return ''
  if (runtimeStatus.value === 'Awaiting Deployment') return '未部署'
  return runtimeStatus.value
})

const deployText = computed(() => {
  const lastDeployedAt = projectDetail.value.last_deployed_at
  if (!lastDeployedAt) return '未部署'

  try {
    const now = Date.now()
    const time = new Date(lastDeployedAt).getTime()
    if (Number.isNaN(time)) return '未部署'

    const diff = Math.floor((now - time) / 1000)

    if (diff < 60) return '刚刚'
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
    return `${Math.floor(diff / 86400)}天前`
  } catch {
    return '未部署'
  }
})

const statusPillClass = computed(() => {
  const value = String(runtimeStatus.value || '').toLowerCase()

  if (value === 'unknown') return 'status-pill-warning'
  if (value === 'awaiting deployment') return 'status-pill-info'
  if (value === 'deployed') return 'status-pill-success'
  if (value.startsWith('up')) return 'status-pill-success'
  if (value.startsWith('exited (0)')) return 'status-pill-info'
  if (value.startsWith('exited')) return 'status-pill-danger'
  if (value.startsWith('restarting') || value.startsWith('paused')) return 'status-pill-warning'
  if (value.startsWith('created')) return 'status-pill-info'
  if (value.startsWith('dead')) return 'status-pill-danger'
  return 'status-pill-info'
})

const currentProjectDeployPanel = computed(() => {
  if (projectType.value === 'java') return JavaProjectDeployPanel
  if (projectType.value === 'web') return WebProjectDeployPanel
  if (projectType.value === 'python') return PythonProjectDeployPanel
  return null
})

const currentDialogComponent = computed(() => {
  return projectType.value ? projectDetailDialogMap[projectType.value] : null
})

async function fetchProjectDetail() {
  const id = getRouteProjectId()

  if (!id || !currentAgent.value?.id) {
    projectLoaded.value = false
    return
  }

  try {
    const data = await getAgentApi().fetchProjectDetail(id)
    projectDetail.value = { ...data }
    projectLoaded.value = true
  } catch (error) {
    console.error('fetchProjectDetail error:', error)
    projectLoaded.value = false
    Notify.create({
      type: 'negative',
      message: '加载项目信息失败',
      position: 'top',
    })
  }
}

async function fetchRuntimeStatus() {
  runtimeStatus.value = 'Checking'

  try {
    const currentProject = projectDetail.value

    if (isWebProject(currentProject)) {
      if (!currentProject.id) {
        runtimeStatus.value = 'Unknown'
        return
      }

      const res = await getAgentApi().checkWebProjectDeploymentStatus(currentProject.id)
      runtimeStatus.value = res?.deployment_status || 'Unknown'
      return
    }

    if (isContainerProject(currentProject)) {
      const containerName = currentProject.container_name

      if (!containerName) {
        runtimeStatus.value = 'Unknown'
        return
      }

      const statusRes = await getAgentApi().fetchDockerContainerStatus(containerName)
      runtimeStatus.value = statusRes?.container_status || 'Unknown'
      return
    }

    runtimeStatus.value = 'Unknown'
  } catch (error) {
    console.error('fetchRuntimeStatus error:', error)
    runtimeStatus.value = 'Unknown'
  }
}

function handleActiveTabChange(value: TabKey) {
  if (activeTab.value === value) return
  activeTab.value = value
}

function openProjectDetailDialog() {
  if (!currentDialogComponent.value) {
    Notify.create({
      type: 'warning',
      message: '暂不支持该类型详情',
      position: 'top',
    })
    return
  }

  detailDialogVisible.value = true
}

async function handleContainerActionSuccess() {
  await fetchRuntimeStatus()
}

async function refreshAll() {
  await fetchProjectDetail()
  await fetchRuntimeStatus()
}

async function handleDeleted() {
  Notify.create({
    type: 'positive',
    message: '项目已删除',
    position: 'top',
  })

  await router.replace('/project')
}

watch(
  [() => route.fullPath, () => currentAgent.value?.id],
  async () => {
    await fetchProjectDetail()
    await fetchRuntimeStatus()
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
  min-height: calc(100vh - 36px);
}

.console-card {
  min-height: calc(100vh - 36px);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.console-header {
  padding: 22px 22px 18px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  background:
    radial-gradient(circle at top right, rgba(14, 165, 233, 0.06), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.92) 100%);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.console-main {
  flex: 1;
  min-width: 0;
}

.console-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  flex-wrap: wrap;
}

.console-title {
  margin: 0;
  font-size: 30px;
  line-height: 1.15;
  font-weight: 800;
  color: #0f172a;
  word-break: break-word;
  letter-spacing: -0.01em;
}

.title-runtime {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 28px;
}

.console-submeta {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}

.type-text {
  color: #0f172a;
  font-weight: 700;
}

.code-text {
  color: #475569;
  font-weight: 700;
}

.submeta-item {
  color: #64748b;
}

.submeta-divider {
  color: #cbd5e1;
  font-size: 18px;
  line-height: 1;
}

.console-right {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  min-height: 40px;
}

.runtime-checking-text {
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.header-btn {
  border: none;
  border-radius: 12px;
  height: 38px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s ease;
}

.header-btn-secondary {
  background: #fff;
  color: #334155;
  border: 1px solid #dbe4ee;
}

.header-btn-secondary:hover {
  border-color: #bfd2ff;
  color: #2563eb;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.08);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}

.status-pill-success {
  background: rgba(34, 197, 94, 0.1);
  color: #15803d;
}

.status-pill-info {
  background: rgba(59, 130, 246, 0.1);
  color: #1d4ed8;
}

.status-pill-warning {
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
}

.status-pill-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #b91c1c;
}

.tab-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.72);
  overflow-x: auto;
  background: rgba(255, 255, 255, 0.72);
}

.tab-btn {
  position: relative;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 14px;
  font-weight: 700;
  padding: 10px 14px 12px;
  border-radius: 12px 12px 0 0;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.18s ease;
}

.tab-btn:hover {
  color: #0284c7;
  background: rgba(14, 165, 233, 0.05);
}

.tab-btn.active {
  color: #0284c7;
  background: rgba(14, 165, 233, 0.06);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 0;
  height: 2px;
  border-radius: 999px;
  background: #0ea5e9;
}

.console-body {
  flex: 1;
  min-height: 0;
  padding: 16px 18px 18px;
}

.loading-wrap {
  min-height: calc(100vh - 36px);
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  gap: 12px;
  color: #64748b;
}

.loading-text {
  font-size: 14px;
}

.unsupported-panel {
  min-height: 320px;
  border-radius: 20px;
  border: 1px dashed #cbd5e1;
  background: rgba(255, 255, 255, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #64748b;
  gap: 8px;
}

.unsupported-title {
  font-size: 18px;
  font-weight: 700;
  color: #334155;
}

.unsupported-desc {
  font-size: 14px;
  color: #64748b;
}

@media (max-width: 768px) {
  .project-deploy-console-page {
    padding: 14px;
  }

  .page-shell,
  .console-card,
  .loading-wrap {
    min-height: calc(100vh - 28px);
  }

  .console-header {
    padding: 18px 18px 14px;
    flex-direction: column;
    align-items: stretch;
  }

  .console-title {
    font-size: 22px;
  }

  .console-title-row {
    align-items: flex-start;
  }

  .console-right {
    justify-content: flex-start;
  }

  .tab-bar {
    padding-left: 14px;
    padding-right: 14px;
  }

  .console-body {
    padding: 14px;
  }
}
</style>