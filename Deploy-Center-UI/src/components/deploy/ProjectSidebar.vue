<template>
  <aside class="sidebar">
    <div class="sidebar-card">
      <div class="project-title-block">
        <div class="project-title-row">
          <h1 class="project-title">{{ props.project.project_name || '-' }}</h1>
          <div class="project-badge" :class="badgeClass">
            {{ typeLabel }}
          </div>
        </div>

        <div class="project-code">{{ props.project.project_code || 'NO_CODE' }}</div>
      </div>

      <div class="status-panel">
        <div class="status-block">
          <div class="status-label">运行状态</div>

          <div class="status-content">
            <template v-if="runtimeStatus === 'Checking'">
              <q-spinner color="grey-5" size="16px" />
            </template>

            <template v-else>
              <el-tag :type="runtimeStatusTagType" effect="light" round class="runtime-status-tag">
                {{ runtimeStatusLabel }}
              </el-tag>
            </template>
          </div>
        </div>

        <div class="status-block">
          <div class="status-label">最近部署</div>
          <div class="status-content">
            <span class="status-text">{{ deployText }}</span>
          </div>
        </div>
      </div>

      <div class="sidebar-section">
        <div class="section-header">
          <div class="section-caption">项目详情</div>

          <div class="section-actions">
            <template v-if="props.editing">
              <button class="text-action-btn text-action-btn-secondary" @click="$emit('cancel-edit')">
                返回
              </button>
              <button class="text-action-btn" @click="$emit('save-edit')">
                保存
              </button>
            </template>

            <template v-else>
              <button class="text-action-btn" @click="$emit('start-edit')">
                编辑
              </button>
            </template>
          </div>
        </div>

        <div v-if="!props.editing" class="info-list">
          <div
            v-for="field in detailFields"
            :key="field.key"
            class="info-row"
            @click.stop="field.copyable ? copyVal(props.project[field.key]) : undefined"
          >
            <div class="info-key">{{ field.label }}</div>
            <div
              class="info-value"
              :class="{
                ellipsis: field.ellipsis,
                'is-copyable': field.copyable
              }"
              :title="String(formatDisplayValue(field.key, props.project[field.key]))"
            >
              {{ formatDisplayValue(field.key, props.project[field.key]) }}
            </div>
          </div>
        </div>

        <div v-else class="sidebar-form-wrap">
          <el-form label-width="88px" :model="props.form" class="sidebar-form">
            <el-form-item
              v-for="field in editableDetailFields"
              :key="field.key"
              :label="field.label"
            >
              <el-input
                v-if="field.editable !== false"
                v-model="props.form[field.key]"
                :readonly="field.readonly"
                :disabled="field.readonly"
              />
              <el-input
                v-else
                :model-value="formatDisplayValue(field.key, props.form[field.key])"
                readonly
                disabled
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Notify, copyToClipboard } from 'quasar'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'

type ProjectSidebarForm = {
  id?: string | number
  project_type?: string
  project_name?: string
  project_code?: string
  project_group?: string
  access_url?: string
  deployment_status?: string
  framework?: string
  runtime_version?: string
  node_version?: string
  container_name?: string
  docker_image_name?: string
  docker_image_tag?: string
  network?: string
  external_port?: string | number
  internal_port?: string | number
  host_project_path?: string
  container_project_path?: string
  git_repository?: string
  jdk_version?: string | number
  python_version?: string
  created_at?: string
  updated_at?: string
  last_deployed_at?: string
  [key: string]: any
}

type FieldConfig = {
  key: string
  label: string
  copyable?: boolean
  ellipsis?: boolean
  editable?: boolean
  readonly?: boolean
}

const props = withDefaults(
  defineProps<{
    project: ProjectSidebarForm
    editing?: boolean
    form?: ProjectSidebarForm
  }>(),
  {
    editing: false,
    form: () => ({}),
  }
)

defineEmits<{
  (e: 'start-edit'): void
  (e: 'cancel-edit'): void
  (e: 'save-edit'): void
}>()

const runtimeStatus = ref('Checking')

const typeLabel = computed(() => {
  const t = String(props.project.project_type || '').toLowerCase()
  if (t === 'web' || t === 'frontend') return 'Web'
  if (t === 'java') return 'Java'
  if (t === 'python') return 'Python'
  if (t === 'container') return 'Container'
  return '服务'
})

const badgeClass = computed(() => {
  const t = String(props.project.project_type || '').toLowerCase()
  if (t === 'java') return 'badge-java'
  if (t === 'web' || t === 'frontend') return 'badge-web'
  if (t === 'python') return 'badge-python'
  if (t === 'container') return 'badge-container'
  return 'badge-default'
})

const deployText = computed(() => {
  const t = props.project.last_deployed_at
  if (!t) return '未部署'
  try {
    const diff = Math.floor((Date.now() - new Date(t).getTime()) / 1000)
    if (diff < 60) return '刚刚'
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
    return `${Math.floor(diff / 86400)}天前`
  } catch {
    return '未部署'
  }
})

const runtimeStatusLabel = computed(() => {
  const status = String(runtimeStatus.value || '')
  if (status === 'Awaiting Deployment') return '未部署'
  if (!status || status === 'Unknown') return 'Status Unknown'
  return status
})

const runtimeStatusTagType = computed(() => {
  const status = String(runtimeStatus.value || '').toLowerCase()

  if (status === 'unknown') return 'warning'
  if (status.startsWith('up')) return 'success'
  if (status.startsWith('exited (0)')) return 'info'
  if (status.startsWith('exited')) return 'danger'
  if (status.startsWith('restarting') || status.startsWith('paused')) return 'warning'
  if (status.startsWith('created')) return 'info'
  if (status.startsWith('dead')) return 'danger'
  if (status === 'deployed' || status === '已部署') return 'success'
  if (status === 'awaiting deployment') return 'info'
  return 'info'
})

function displayValue(v: unknown) {
  if (v === null || v === undefined || v === '') return '-'
  return v
}

function formatDateValue(v: unknown) {
  if (!v) return '-'
  try {
    return new Date(String(v)).toLocaleString()
  } catch {
    return String(v)
  }
}

function formatDisplayValue(key: string, value: unknown) {
  if (key === 'created_at' || key === 'updated_at' || key === 'last_deployed_at') {
    return formatDateValue(value)
  }
  return displayValue(value)
}

const commonFields: FieldConfig[] = [
  { key: 'project_name', label: '项目名称' },
  { key: 'project_code', label: '项目代号' },
  { key: 'project_group', label: '项目分组' },
  { key: 'access_url', label: '访问地址' },
  { key: 'created_at', label: '创建时间', editable: false, readonly: true },
]

const commonContainerFields: FieldConfig[] = [
  { key: 'container_name', label: '容器名称' },
  { key: 'docker_image_name', label: '镜像名称' },
  { key: 'docker_image_tag', label: '镜像标签' },
  { key: 'network', label: 'Docker网络' },
  { key: 'external_port', label: '外部端口' },
  { key: 'internal_port', label: '内部端口' },
]

const webFields: FieldConfig[] = [
  { key: 'framework', label: '框架', editable: false, readonly: true },
  { key: 'node_version', label: 'Node版本', editable: false, readonly: true },
]

const javaFields: FieldConfig[] = [
  { key: 'git_repository', label: 'Git仓库' },
  { key: 'host_project_path', label: '宿主机路径' },
  { key: 'container_project_path', label: '容器内路径' },
  { key: 'jdk_version', label: 'JDK版本', editable: false, readonly: true },
]

const pythonFields: FieldConfig[] = [
  { key: 'python_version', label: 'Python版本', editable: false, readonly: true },
]

const detailFields = computed<FieldConfig[]>(() => {
  const t = String(props.project.project_type || '').toLowerCase()

  if (t === 'java') {
    return [...commonFields, ...commonContainerFields, ...javaFields]
  }

  if (t === 'python') {
    return [...commonFields, ...commonContainerFields, ...pythonFields]
  }

  return [...commonFields, ...webFields]
})

const editableDetailFields = computed(() => {
  return detailFields.value.filter((field) => field.key !== 'created_at')
})

async function copyVal(v: unknown) {
  if (!v || v === '-') return
  try {
    await copyToClipboard(String(v))
    Notify.create({
      type: 'positive',
      message: '已复制',
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

async function fetchRuntimeStatus() {
  const containerName = String(props.project.container_name || '').trim()

  if (containerName) {
    runtimeStatus.value = 'Checking'
    try {
      const api = provideCurrentAgentProxyApi()
      const res = await api.fetchDockerContainerStatus(containerName)
      runtimeStatus.value = res?.container_status || 'Unknown'
      return
    } catch (error) {
      console.error('fetchRuntimeStatus error:', error)
      runtimeStatus.value = 'Unknown'
      return
    }
  }

  const deploymentStatus = String(props.project.deployment_status || '').trim()
  if (deploymentStatus) {
    runtimeStatus.value = deploymentStatus
    return
  }

  runtimeStatus.value = 'Unknown'
}

watch(
  () => [
    props.project.id,
    props.project.project_type,
    props.project.container_name,
    props.project.deployment_status,
  ],
  async () => {
    await fetchRuntimeStatus()
  },
  { immediate: true }
)
</script>

<style scoped>
.sidebar {
  min-width: 0;
}

.sidebar-card {
  height: 100%;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
  padding: 22px 20px 20px;
  overflow: hidden;
}

.project-title-block {
  margin-top: 4px;
}

.project-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.project-title {
  margin: 0;
  font-size: 28px;
  line-height: 1.16;
  font-weight: 800;
  color: #0f172a;
  word-break: break-word;
  flex: 1;
  min-width: 0;
}

.project-badge {
  flex-shrink: 0;
  height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
}

.badge-java {
  background: rgba(59, 130, 246, 0.12);
  color: #2563eb;
}

.badge-web {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
}

.badge-python {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
}

.badge-container {
  background: rgba(139, 92, 246, 0.12);
  color: #7c3aed;
}

.badge-default {
  background: rgba(148, 163, 184, 0.14);
  color: #475569;
}

.project-code {
  margin-top: 8px;
  font-size: 13px;
  color: #64748b;
}

.status-panel {
  margin-top: 18px;
  display: grid;
  gap: 10px;
}

.status-block {
  padding: 14px 16px;
  border-radius: 16px;
  background: linear-gradient(180deg, #fff 0%, #f8fafc 100%);
  border: 1px solid #e5e7eb;
}

.status-label {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
  line-height: 1.4;
}

.status-content {
  min-height: 28px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.status-text {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  line-height: 1.5;
  word-break: break-word;
}

.runtime-status-tag {
  max-width: 100%;
}

.sidebar-section {
  margin-top: 22px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-caption {
  font-size: 13px;
  color: #64748b;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.text-action-btn {
  border: none;
  background: transparent;
  color: #0284c7;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  padding: 0;
}

.text-action-btn-secondary {
  color: #64748b;
}

.info-list {
  border-top: 1px dashed #e2e8f0;
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px dashed #e2e8f0;
}

.info-key {
  width: 82px;
  flex-shrink: 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
}

.info-value {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #334155;
  word-break: break-all;
}

.is-copyable {
  cursor: pointer;
  transition: color 0.18s ease;
}

.is-copyable:hover {
  color: #2563eb;
}

.sidebar-form-wrap {
  padding: 0;
}

.sidebar-form :deep(.el-form-item) {
  margin-bottom: 14px;
}

.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.el-tag) {
  border-radius: 999px;
  font-weight: 700;
  border: none;
  max-width: 100%;
  white-space: normal;
  height: auto;
  line-height: 1.4;
  padding-top: 4px;
  padding-bottom: 4px;
}
</style>