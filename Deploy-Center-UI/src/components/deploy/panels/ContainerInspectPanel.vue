<template>
  <section class="container-inspect-panel">
    <template v-if="projectType === 'web'">
      <div class="empty-state-card">
        <div class="empty-state-title">当前项目无容器 Inspect 信息</div>
        <div class="empty-state-desc">
          Web 项目当前使用站点部署状态，不展示 Docker 容器 inspect 信息。
        </div>
      </div>
    </template>

    <template v-else-if="loading">
      <div class="loading-state-card">
        <q-spinner color="primary" size="28px" />
        <div class="loading-state-text">加载容器 Inspect 信息中...</div>
      </div>
    </template>

    <template v-else-if="inspectRecord">
      <div class="panel-header">
        <div class="panel-header-left">
          <div class="panel-title">容器 Inspect</div>
          <div class="panel-subtitle">
            展示 Docker inspect 原始结构化信息
          </div>
        </div>

        <div class="panel-actions">
          <button
            class="action-btn action-btn-secondary"
            :disabled="loading"
            @click="copyRawJson"
          >
            复制 JSON
          </button>

          <button
            class="action-btn action-btn-secondary"
            :disabled="loading"
            @click="loadInspectInfo"
          >
            刷新
          </button>
        </div>
      </div>

      <div class="summary-grid">
        <div
          v-for="item in inspectSummaryItems"
          :key="item.key"
          class="summary-card"
        >
          <div class="summary-label">{{ item.label }}</div>
          <div
            class="summary-value"
            :title="item.value"
            @click="copyValue(item.value)"
          >
            {{ item.value }}
          </div>
        </div>
      </div>

      <div class="json-block">
        <div class="json-block-header">
          <div class="json-block-title">原始 docker inspect 数据</div>
        </div>

        <pre class="json-content">{{ formattedInspectJson }}</pre>
      </div>
    </template>

    <template v-else>
      <div class="empty-state-card">
        <div class="empty-state-title">暂无容器 Inspect 信息</div>
        <div class="empty-state-desc">
          当前项目未查询到容器 inspect 信息。
        </div>

        <button
          class="action-btn action-btn-secondary"
          :disabled="loading"
          @click="loadInspectInfo"
        >
          重试
        </button>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Notify, copyToClipboard } from 'quasar'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'

export type DockerContainerInspectRecord = Record<string, any>

type ProjectLike = {
  id?: string | number
  project_type?: string
  container_name?: string
}

type SummaryItem = {
  key: string
  label: string
  value: string
}

const props = defineProps<{
  project: ProjectLike
}>()

const loading = ref(false)
const inspectRecord = ref<DockerContainerInspectRecord | null>(null)

const projectType = computed(() => {
  return String(props.project.project_type || '').toLowerCase().trim()
})

const formattedInspectJson = computed(() => {
  if (!inspectRecord.value) return ''
  try {
    return JSON.stringify(inspectRecord.value, null, 2)
  } catch {
    return ''
  }
})

const inspectSummaryItems = computed<SummaryItem[]>(() => {
  const inspect = inspectRecord.value
  if (!inspect) return []

  return [
    { key: 'Id', label: '容器 ID', value: String(inspect.Id || '-') },
    { key: 'Name', label: '容器名称', value: String(inspect.Name || '-') },
    { key: 'Created', label: '创建时间', value: String(inspect.Created || '-') },
    { key: 'Image', label: '镜像 ID', value: String(inspect.Image || '-') },
    {
      key: 'Config.Image',
      label: '镜像名称',
      value: String(inspect.Config?.Image || '-'),
    },
    {
      key: 'State.Status',
      label: '状态',
      value: String(inspect.State?.Status || '-'),
    },
    {
      key: 'State.Running',
      label: '是否运行中',
      value: inspect.State?.Running == null ? '-' : String(inspect.State.Running),
    },
    {
      key: 'State.ExitCode',
      label: '退出码',
      value: inspect.State?.ExitCode == null ? '-' : String(inspect.State.ExitCode),
    },
    {
      key: 'RestartCount',
      label: '重启次数',
      value: inspect.RestartCount == null ? '-' : String(inspect.RestartCount),
    },
    {
      key: 'Path',
      label: '启动程序',
      value: String(inspect.Path || '-'),
    },
    {
      key: 'HostConfig.NetworkMode',
      label: '网络模式',
      value: String(inspect.HostConfig?.NetworkMode || '-'),
    },
    {
      key: 'NetworkSettings.IPAddress',
      label: 'IP 地址',
      value: String(inspect.NetworkSettings?.IPAddress || '-'),
    },
    {
      key: 'Mounts',
      label: '挂载数量',
      value: Array.isArray(inspect.Mounts) ? String(inspect.Mounts.length) : '-',
    },
  ]
})

async function copyValue(value?: string) {
  const text = String(value || '').trim()
  if (!text || text === '-') return

  try {
    await copyToClipboard(text)
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

async function copyRawJson() {
  if (!formattedInspectJson.value) return

  try {
    await copyToClipboard(formattedInspectJson.value)
    Notify.create({
      type: 'positive',
      message: 'Inspect JSON 已复制',
      position: 'top',
      timeout: 1200,
    })
  } catch {
    Notify.create({
      type: 'negative',
      message: '复制 JSON 失败',
      position: 'top',
      timeout: 1200,
    })
  }
}

async function loadInspectInfo() {
  if (projectType.value === 'web') {
    inspectRecord.value = null
    return
  }

  const containerName = String(props.project.container_name || '').trim()
  if (!containerName) {
    inspectRecord.value = null
    return
  }

  loading.value = true
  try {
    const res = await provideCurrentAgentProxyApi().fetchDockerContainerInspect(containerName)
    inspectRecord.value = res || null
  } catch (error) {
    console.error('loadInspectInfo error:', error)
    inspectRecord.value = null
    Notify.create({
      type: 'negative',
      message: '加载容器 Inspect 信息失败',
      position: 'top',
    })
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.project.id, props.project.project_type, props.project.container_name],
  async () => {
    await loadInspectInfo()
  },
  { immediate: true }
)
</script>

<style scoped>
.container-inspect-panel {
  min-height: 320px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 14px;
}

.panel-header-left {
  min-width: 0;
  flex: 1;
}

.panel-title {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
}

.panel-subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.action-btn {
  border: none;
  border-radius: 12px;
  height: 36px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s ease;
}

.action-btn-secondary {
  background: #fff;
  color: #334155;
  border: 1px solid #dbe4ee;
}

.action-btn-secondary:hover:not(:disabled) {
  border-color: #bfd2ff;
  color: #2563eb;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.08);
}

.action-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}

.summary-card {
  border-radius: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e5e7eb;
  padding: 14px 16px;
  min-width: 0;
  transition: box-shadow 0.18s ease, border-color 0.18s ease;
}

.summary-card:hover {
  border-color: #dbeafe;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
}

.summary-label {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 13px;
  line-height: 1.7;
  color: #334155;
  word-break: break-all;
  cursor: pointer;
  transition: color 0.18s ease;
}

.summary-value:hover {
  color: #2563eb;
}

.json-block {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: #0f172a;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.json-block-header {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.08);
  background: rgba(255, 255, 255, 0.03);
}

.json-block-title {
  font-size: 13px;
  font-weight: 700;
  color: #cbd5e1;
}

.json-content {
  margin: 0;
  padding: 16px;
  font-size: 12px;
  line-height: 1.7;
  color: #e2e8f0;
  overflow: auto;
  max-height: 70vh;
  white-space: pre-wrap;
  word-break: break-word;
}

.empty-state-card,
.loading-state-card {
  min-height: 280px;
  border-radius: 20px;
  border: 1px dashed #cbd5e1;
  background: rgba(255, 255, 255, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #64748b;
  gap: 10px;
  text-align: center;
  padding: 24px;
}

.empty-state-title {
  font-size: 18px;
  font-weight: 700;
  color: #334155;
}

.empty-state-desc,
.loading-state-text {
  font-size: 14px;
  color: #64748b;
  line-height: 1.7;
  max-width: 560px;
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .panel-header {
    flex-direction: column;
    align-items: stretch;
  }

  .panel-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .json-content {
    max-height: 56vh;
  }
}
</style>