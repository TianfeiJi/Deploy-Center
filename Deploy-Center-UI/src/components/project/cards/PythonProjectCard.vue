<template>
  <q-card class="python-project-card">
    <q-card-section class="card-header">
      <div class="project-header">
        <div class="project-header-left">
          <div class="project-title" :title="pythonProject.project_name || '-'">
            {{ pythonProject.project_name || '-' }}
          </div>

          <div class="project-submeta">
            <span class="project-submeta-type">Python</span>
            <span v-if="pythonProject.project_group" class="project-submeta-divider">·</span>
            <span v-if="pythonProject.project_group" class="project-submeta-group">
              {{ pythonProject.project_group }}
            </span>
          </div>
        </div>

        <div class="project-header-right">
          <div class="runtime-status-inline">
            <template v-if="containerStatus === 'Checking'">
              <q-spinner color="grey-5" size="16px" />
            </template>

            <template v-else-if="containerStatus === 'Unknown'">
              <el-tag type="warning" effect="light" round>Status Unknown</el-tag>
            </template>

            <template v-else>
              <el-tag
                :closable="false"
                :type="getContainerStatusTagType(containerStatus)"
                effect="light"
                round
              >
                {{ formatContainerStatusLabel(containerStatus) }}
              </el-tag>
            </template>
          </div>

          <div class="project-deploy-text">
            最近部署：{{ getDeployText(pythonProject.last_deployed_at) }}
          </div>
        </div>
      </div>

      <div class="info-list q-mt-sm">
        <div class="info-row">
          <div class="info-key">容器名称</div>
          <div
            class="info-main-value hover-copy"
            :title="pythonProject.container_name || '-'"
            @click.stop="copyValue(pythonProject.container_name)"
          >
            {{ pythonProject.container_name || '-' }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">镜像名称</div>
          <div
            class="info-value hover-copy"
            :title="dockerImageText"
            @click.stop="copyValue(dockerImageText)"
          >
            {{ dockerImageText }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">端口映射</div>
          <div class="info-value" :title="portMappingText">
            {{ portMappingText }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">Docker 网络</div>
          <div
            class="info-value hover-copy"
            :title="pythonProject.network || '-'"
            @click.stop="copyValue(pythonProject.network)"
          >
            {{ pythonProject.network || '-' }}
          </div>
        </div>

        <div v-if="pythonProject.access_url" class="info-row">
          <div class="info-key">访问地址</div>
          <div
            class="info-value access-url-link"
            :title="pythonProject.access_url"
            @click.stop="openAccessUrl(pythonProject.access_url)"
          >
            {{ pythonProject.access_url }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">宿主机路径</div>
          <div
            class="info-value hover-copy multi-line-value"
            :title="pythonProject.host_project_path || '-'"
            @click.stop="copyValue(pythonProject.host_project_path)"
          >
            {{ pythonProject.host_project_path || '-' }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">容器内路径</div>
          <div
            class="info-value hover-copy multi-line-value"
            :title="pythonProject.container_project_path || '-'"
            @click.stop="copyValue(pythonProject.container_project_path)"
          >
            {{ pythonProject.container_project_path || '-' }}
          </div>
        </div>
      </div>
    </q-card-section>

    <q-card-actions class="card-actions split-actions">
      <div class="actions-left">
        <q-btn flat dense color="primary" label="详情" @click="viewPythonProjectDetail" />
      </div>

      <div class="actions-right">
        <q-btn flat dense color="positive" label="部署" @click="goToDeployConsole(pythonProject.id)" />
      </div>
    </q-card-actions>
  </q-card>

  <PythonProjectDetailDialog
    v-model="isViewDetailDialogOpen"
    :project="pythonProject"
    @saved="emit('refresh')"
    @deleted="emit('refresh')"
  />
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { Notify, copyToClipboard } from 'quasar'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'
import type { PythonProject } from 'src/types/Project.types'
import { useRouter } from 'vue-router'
import PythonProjectDetailDialog from 'src/components/project/dialogs/PythonProjectDetailDialog.vue'

const router = useRouter()

const props = defineProps<{
  pythonProject: PythonProject
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const agentProxyApi = provideCurrentAgentProxyApi()

const isViewDetailDialogOpen = ref(false)
const containerStatus = ref('Checking')

const goToDeployConsole = (id?: string | number) => {
  if (!id) return
  router.push({
    path: `/project/deploy/${id}`,
  })
}

const dockerImageText = computed(() => {
  return `${props.pythonProject.docker_image_name || '-'}:${props.pythonProject.docker_image_tag || 'latest'}`
})

const portMappingText = computed(() => {
  return `${props.pythonProject.external_port || '-'} → ${props.pythonProject.internal_port || '-'}`
})

const getDeployText = (time?: any) => {
  if (!time) return '未部署'
  try {
    const now = Date.now()
    const t = new Date(time).getTime()
    if (Number.isNaN(t)) return '-'

    const diff = Math.floor((now - t) / 1000)

    if (diff < 60) return '刚刚'
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
    return `${Math.floor(diff / 86400)}天前`
  } catch {
    return '未部署'
  }
}

const copyValue = async (text?: string) => {
  const value = text?.trim()
  if (!value || value === '-') return

  try {
    await copyToClipboard(value)
    Notify.create({
      type: 'positive',
      message: '复制成功',
      position: 'top',
      timeout: 1000,
    })
  } catch {
    Notify.create({
      type: 'negative',
      message: '复制失败',
      position: 'top',
      timeout: 1000,
    })
  }
}

const openAccessUrl = (url?: string) => {
  const value = url?.trim()
  if (!value || value === '-') return
  window.open(value, '_blank', 'noopener,noreferrer')
}

const formatContainerStatusLabel = (status: string) => {
  const raw = String(status || '').toLowerCase()

  if (!raw) return 'Unknown'
  if (raw.includes('awaiting deployment')) return '未部署'
  if (raw === 'unknown') return 'Unknown'
  return status
}

const fetchContainerStatus = async () => {
  containerStatus.value = 'Checking'

  if (!props.pythonProject.container_name) {
    containerStatus.value = 'Unknown'
    return
  }

  try {
    const response = await agentProxyApi.fetchDockerContainerStatus(
      String(props.pythonProject.container_name)
    )
    containerStatus.value = response?.container_status || 'Unknown'
  } catch {
    containerStatus.value = 'Unknown'
  }
}

const getContainerStatusTagType = (status: string) => {
  const s = status.toLowerCase()

  if (s.includes('awaiting deployment')) return 'info'
  if (s.startsWith('up')) return 'success'
  if (s.startsWith('exited (0)')) return 'info'
  if (s.startsWith('exited')) return 'danger'
  if (s.startsWith('restarting') || s.startsWith('paused')) return 'warning'
  if (s.startsWith('created')) return 'info'
  if (s.startsWith('dead')) return 'danger'
  if (s === 'unknown') return 'warning'
  return 'info'
}

const viewPythonProjectDetail = () => {
  isViewDetailDialogOpen.value = true
}

watch(
  () => props.pythonProject.container_name,
  () => {
    fetchContainerStatus()
  }
)

onMounted(() => {
  fetchContainerStatus()
})
</script>

<style scoped>
.python-project-card {
  width: 100%;
  min-height: 418px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 20px;
  overflow: visible;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
  transition: all 0.22s ease;
}

.python-project-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 44px rgba(15, 23, 42, 0.1);
}

.card-header {
  padding: 18px 18px 10px;
}

.project-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding-bottom: 4px;
}

.project-header-left {
  flex: 1;
  min-width: 0;
}

.project-header-right {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: flex-start;
  gap: 6px;
  padding-top: 2px;
}

.project-title {
  font-size: 20px;
  font-weight: 800;
  color: #111827;
  line-height: 1.35;
  letter-spacing: -0.01em;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-submeta {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.project-submeta-type,
.project-submeta-group {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
}

.project-submeta-divider {
  font-size: 20px;
  font-weight: 600;
  color: #cbd5e1;
}

.runtime-status-inline {
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
}

.project-deploy-text {
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.2;
  white-space: nowrap;
}

.info-list {
  margin-top: 10px;
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  transition: background 0.18s ease;
}

.info-row + .info-row {
  border-top: 1px dashed #e5e7eb;
}

.info-row:hover {
  background: rgba(248, 250, 252, 0.55);
}

.info-key {
  width: 82px;
  flex-shrink: 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
  white-space: nowrap;
}

.info-main-value,
.info-value {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #334155;
  word-break: break-all;
}

.info-main-value {
  font-weight: 600;
  color: #1f2937;
}

.access-url-link {
  color: #2563eb;
  font-weight: 600;
  cursor: pointer;
}

.access-url-link:hover {
  color: #1d4ed8;
}

.multi-line-value {
  white-space: normal;
  overflow: visible;
  text-overflow: unset;
}

.hover-copy {
  cursor: pointer;
  position: relative;
  transition: color 0.18s ease;
}

.hover-copy:hover {
  color: #2563eb;
}

.hover-copy::after {
  content: "点此复制";
  position: absolute;
  right: 0;
  top: calc(100% + 6px);
  z-index: 20;
  padding: 6px 8px;
  font-size: 12px;
  line-height: 1;
  color: #f8fafc;
  background: rgba(15, 23, 42, 0.92);
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.18);
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transform: translateY(4px);
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.hover-copy:hover::after {
  opacity: 1;
  transform: translateY(0);
}

.card-actions.split-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px 14px;
  gap: 12px;
}

.actions-left,
.actions-right {
  display: flex;
  align-items: center;
}

:deep(.card-actions .q-btn) {
  border-radius: 12px;
  transition: all 0.18s ease;
}

:deep(.card-actions .q-btn:hover) {
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
}

:deep(.el-tag) {
  border-radius: 999px;
  font-weight: 600;
  border: none;
}

@media (max-width: 640px) {
  .project-header {
    gap: 10px;
  }

  .project-title {
    font-size: 18px;
  }

  .project-header-right {
    gap: 4px;
  }

  .info-key {
    width: 74px;
  }
}
</style>