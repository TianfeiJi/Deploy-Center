<template>
  <section class="container-info-panel">
    <template v-if="projectType === 'web'">
      <div class="empty-state-card">
        <div class="empty-state-title">当前项目无容器信息</div>
        <div class="empty-state-desc">
          Web 项目当前使用站点部署状态，不展示 Docker 容器 ps 信息。
        </div>
      </div>
    </template>

    <template v-else-if="loading">
      <div class="loading-state-card">
        <q-spinner color="primary" size="28px" />
        <div class="loading-state-text">加载容器信息中...</div>
      </div>
    </template>

    <template v-else-if="containerInfo">
      <div class="panel-header">
        <div class="panel-header-left">
          <div class="panel-title">容器信息</div>
          <div class="panel-subtitle">
            展示 docker ps -a --format=json 的结构化结果
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
            @click="loadContainerInfo"
          >
            刷新
          </button>
        </div>
      </div>

      <div class="info-grid">
        <div
          v-for="item in containerInfoItems"
          :key="item.key"
          class="info-card"
        >
          <div class="info-card-label">{{ item.label }}</div>
          <div
            class="info-card-value"
            :title="item.value"
            @click="copyInfoValue(item.value)"
          >
            {{ item.value }}
          </div>
        </div>
      </div>

      <div class="json-block">
        <div class="json-block-header">
          <div class="json-block-title">原始 docker ps -a --format=json 数据</div>
        </div>

        <pre class="json-content">{{ formattedContainerInfoJson }}</pre>
      </div>
    </template>

    <template v-else>
      <div class="empty-state-card">
        <div class="empty-state-title">暂无容器信息</div>
        <div class="empty-state-desc">
          当前项目未查询到容器 ps 信息。
        </div>

        <button
          class="action-btn action-btn-secondary"
          :disabled="loading"
          @click="loadContainerInfo"
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

export interface DockerContainerPsInfo {
  Command?: string
  CreatedAt?: string
  ID?: string
  Image?: string
  Labels?: string
  LocalVolumes?: string
  Mounts?: string
  Names?: string
  Networks?: string
  Ports?: string
  RunningFor?: string
  Size?: string
  State?: string
  Status?: string
}

type ProjectLike = {
  id?: string | number
  project_type?: string
  container_name?: string
}

type InfoItem = {
  key: string
  label: string
  value: string
}

const props = defineProps<{
  project: ProjectLike
}>()

const loading = ref(false)
const containerInfo = ref<DockerContainerPsInfo | null>(null)

const projectType = computed(() => {
  return String(props.project.project_type || '').toLowerCase().trim()
})

const formattedContainerInfoJson = computed(() => {
  if (!containerInfo.value) return ''
  try {
    return JSON.stringify(containerInfo.value, null, 2)
  } catch {
    return ''
  }
})

const containerInfoItems = computed<InfoItem[]>(() => {
  if (!containerInfo.value) return []

  return [
    { key: 'ID', label: '容器 ID', value: containerInfo.value.ID || '-' },
    { key: 'Names', label: '容器名称', value: containerInfo.value.Names || '-' },
    { key: 'Image', label: '镜像', value: containerInfo.value.Image || '-' },
    { key: 'Command', label: '启动命令', value: containerInfo.value.Command || '-' },
    { key: 'CreatedAt', label: '创建时间', value: containerInfo.value.CreatedAt || '-' },
    { key: 'RunningFor', label: '运行时长', value: containerInfo.value.RunningFor || '-' },
    { key: 'Status', label: '状态描述', value: containerInfo.value.Status || '-' },
    { key: 'State', label: '状态标识', value: containerInfo.value.State || '-' },
    { key: 'Ports', label: '端口映射', value: containerInfo.value.Ports || '-' },
    { key: 'Networks', label: '网络', value: containerInfo.value.Networks || '-' },
    { key: 'Mounts', label: '挂载', value: containerInfo.value.Mounts || '-' },
    { key: 'LocalVolumes', label: '本地卷数量', value: containerInfo.value.LocalVolumes || '-' },
    { key: 'Labels', label: 'Labels', value: containerInfo.value.Labels || '-' },
    { key: 'Size', label: '大小', value: containerInfo.value.Size || '-' },
  ]
})

async function copyInfoValue(value?: string) {
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
  if (!formattedContainerInfoJson.value) return

  try {
    await copyToClipboard(formattedContainerInfoJson.value)
    Notify.create({
      type: 'positive',
      message: '容器 JSON 已复制',
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

async function loadContainerInfo() {
  if (projectType.value === 'web') {
    containerInfo.value = null
    return
  }

  const containerName = String(props.project.container_name || '').trim()
  if (!containerName) {
    containerInfo.value = null
    return
  }

  loading.value = true
  try {
    const res = await provideCurrentAgentProxyApi().fetchDockerContainerInfo(containerName)
    containerInfo.value = res || null
  } catch (error) {
    console.error('loadContainerInfo error:', error)
    containerInfo.value = null
    Notify.create({
      type: 'negative',
      message: '加载容器信息失败',
      position: 'top',
    })
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.project.id, props.project.project_type, props.project.container_name],
  async () => {
    await loadContainerInfo()
  },
  { immediate: true }
)
</script>

<style scoped>
.container-info-panel {
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}

.info-card {
  border-radius: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e5e7eb;
  padding: 14px 16px;
  min-width: 0;
  transition: box-shadow 0.18s ease, border-color 0.18s ease;
}

.info-card:hover {
  border-color: #dbeafe;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
}

.info-card-label {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
  margin-bottom: 8px;
}

.info-card-value {
  font-size: 13px;
  line-height: 1.7;
  color: #334155;
  word-break: break-all;
  cursor: pointer;
  transition: color 0.18s ease;
}

.info-card-value:hover {
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
  .info-grid {
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