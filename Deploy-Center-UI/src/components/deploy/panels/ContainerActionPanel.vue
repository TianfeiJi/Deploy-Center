<template>
  <section class="container-action-panel">
    <template v-if="projectType === 'web'">
      <div class="empty-state-card">
        <div class="empty-state-title">当前项目无容器操作</div>
        <div class="empty-state-desc">
          Web 项目当前不提供 Docker 容器启动、停止、重启操作。
        </div>
      </div>
    </template>

    <template v-else-if="!containerName">
      <div class="empty-state-card">
        <div class="empty-state-title">未配置容器名称</div>
        <div class="empty-state-desc">
          当前项目未配置 container_name，无法执行容器操作。
        </div>
      </div>
    </template>

    <template v-else-if="runtimeStatusText === 'Awaiting Deployment'">
      <div class="empty-state-card">
        <div class="empty-state-title">项目暂未部署</div>
        <div class="empty-state-desc">
          当前项目对应的容器尚不存在，暂时无法执行启动、停止、重启等容器操作。
        </div>
      </div>
    </template>

    <template v-else-if="runtimeStatusText === 'Unknown'">
      <div class="empty-state-card">
        <div class="empty-state-title">容器状态未知</div>
        <div class="empty-state-desc">
          当前暂时无法确认容器运行状态，请稍后重试，或先检查 Agent 与容器状态。
        </div>
      </div>
    </template>

    <template v-else>
      <div class="panel-header">
        <div class="panel-header-left">
          <div class="panel-title">容器操作</div>
          <div class="panel-subtitle">
            支持对当前容器执行启动、停止、重启操作，并实时刷新容器运行状态。
          </div>
        </div>
      </div>

      <div class="summary-bar">
        <div class="summary-item">
          <span class="summary-label">容器名称</span>
          <span class="summary-value">{{ containerName }}</span>
        </div>

        <div class="summary-item">
          <span class="summary-label">当前状态</span>
          <span class="summary-value">{{ runtimeStatusLabel }}</span>
        </div>
      </div>

      <div class="action-card">
        <div class="action-card-title">执行操作</div>

        <div class="action-button-group">
          <button
            class="action-btn action-btn-start"
            :disabled="actionLoading || isRunning"
            @click="handleStartContainer"
          >
            {{ actionType === 'start' && actionLoading ? '启动中...' : '启动容器' }}
          </button>

          <button
            class="action-btn action-btn-stop"
            :disabled="actionLoading || !isRunning"
            @click="handleStopContainer"
          >
            {{ actionType === 'stop' && actionLoading ? '停止中...' : '停止容器' }}
          </button>

          <button
            class="action-btn action-btn-restart"
            :disabled="actionLoading || !isRunning"
            @click="handleRestartContainer"
          >
            {{ actionType === 'restart' && actionLoading ? '重启中...' : '重启容器' }}
          </button>
        </div>

        <div class="action-tip">
          启动仅在容器未运行时可用；停止与重启仅在容器运行中可用。
        </div>
      </div>

      <div v-if="lastActionMessage" class="result-card">
        <div class="result-card-header">
          <div class="result-card-title">最近一次操作结果</div>
          <div class="result-card-meta">{{ lastActionLabel }}</div>
        </div>

        <pre class="result-content">{{ lastActionMessage }}</pre>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Notify } from 'quasar'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'

type ProjectLike = {
  id?: string | number
  project_type?: string
  container_name?: string
}

const props = defineProps<{
  project: ProjectLike
  runtimeStatus?: string
}>()

const emit = defineEmits<{
  (e: 'action-success'): void
}>()

const actionLoading = ref(false)
const actionType = ref<'start' | 'stop' | 'restart' | ''>('')
const lastActionMessage = ref('')
const lastActionLabel = ref('')

const projectType = computed(() => {
  return String(props.project.project_type || '').toLowerCase().trim()
})

const containerName = computed(() => {
  return String(props.project.container_name || '').trim()
})

const runtimeStatusText = computed(() => {
  return String(props.runtimeStatus || '').trim()
})

const isRunning = computed(() => {
  return runtimeStatusText.value.startsWith('Up')
})

const runtimeStatusLabel = computed(() => {
  if (runtimeStatusText.value === 'Awaiting Deployment') return '未部署'
  if (runtimeStatusText.value === 'Unknown') return '未知'
  return runtimeStatusText.value || '-'
})

const agentProxyApi = provideCurrentAgentProxyApi()

async function runContainerAction(
  type: 'start' | 'stop' | 'restart',
  handler: (containerName: string) => Promise<any>,
  successMessage: string
) {
  if (!containerName.value) return

  actionLoading.value = true
  actionType.value = type

  try {
    const res = await handler(containerName.value)
    lastActionMessage.value = String(res || '').trim() || successMessage
    lastActionLabel.value = successMessage

    Notify.create({
      type: 'positive',
      message: successMessage,
      position: 'top',
    })

    emit('action-success')
  } catch (error: any) {
    console.error(`${type} container error:`, error)

    const message = error?.message || `${successMessage}失败`
    lastActionMessage.value = message
    lastActionLabel.value = `${successMessage}失败`

    Notify.create({
      type: 'negative',
      message,
      position: 'top',
    })
  } finally {
    actionLoading.value = false
    actionType.value = ''
  }
}

async function handleStartContainer() {
  await runContainerAction(
    'start',
    (name: string) => agentProxyApi.startDockerContainer(name),
    '容器启动成功'
  )
}

async function handleStopContainer() {
  await runContainerAction(
    'stop',
    (name: string) => agentProxyApi.stopDockerContainer(name),
    '容器停止成功'
  )
}

async function handleRestartContainer() {
  await runContainerAction(
    'restart',
    (name: string) => agentProxyApi.restartDockerContainer(name),
    '容器重启成功'
  )
}

watch(
  () => [props.project.id, props.project.project_type, props.project.container_name],
  () => {
    lastActionMessage.value = ''
    lastActionLabel.value = ''
  },
  { immediate: true }
)
</script>

<style scoped>
.container-action-panel {
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
  flex: 1;
  min-width: 0;
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

.summary-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 14px;
}

.summary-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(248, 250, 252, 0.92);
  border: 1px solid #e5e7eb;
}

.summary-label {
  font-size: 12px;
  color: #94a3b8;
}

.summary-value {
  display: inline-flex;
  align-items: center;
  font-size: 13px;
  color: #334155;
  font-weight: 700;
}

.action-card {
  padding: 16px 18px;
  margin-bottom: 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e5e7eb;
}

.action-card-title {
  font-size: 14px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 14px;
}

.action-button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.action-btn {
  border: none;
  border-radius: 12px;
  height: 38px;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s ease;
}

.action-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.action-btn-start {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: #fff;
  border: 1px solid transparent;
}

.action-btn-start:hover:not(:disabled) {
  box-shadow: 0 10px 20px rgba(34, 197, 94, 0.2);
  transform: translateY(-1px);
}

.action-btn-stop {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
  border: 1px solid transparent;
}

.action-btn-stop:hover:not(:disabled) {
  box-shadow: 0 10px 20px rgba(239, 68, 68, 0.2);
  transform: translateY(-1px);
}

.action-btn-restart {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #fff;
  border: 1px solid transparent;
}

.action-btn-restart:hover:not(:disabled) {
  box-shadow: 0 10px 20px rgba(245, 158, 11, 0.2);
  transform: translateY(-1px);
}

.action-tip {
  margin-top: 12px;
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
}

.result-card {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: #0f172a;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.result-card-header {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.08);
  background: rgba(255, 255, 255, 0.03);
}

.result-card-title {
  font-size: 13px;
  font-weight: 700;
  color: #e2e8f0;
}

.result-card-meta {
  margin-top: 4px;
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.5;
}

.result-content {
  margin: 0;
  padding: 16px;
  font-size: 12px;
  line-height: 1.7;
  color: #e2e8f0;
  overflow: auto;
  max-height: 60vh;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.empty-state-card {
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

.empty-state-desc {
  font-size: 14px;
  color: #64748b;
  line-height: 1.7;
  max-width: 560px;
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    align-items: stretch;
  }

  .summary-bar {
    gap: 10px;
  }

  .action-button-group {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }

  .result-content {
    max-height: 50vh;
  }
}
</style>