<template>
  <section class="container-log-panel">
    <template v-if="projectType === 'web'">
      <div class="empty-state-card">
        <div class="empty-state-title">当前项目无容器日志</div>
        <div class="empty-state-desc">
          Web 项目当前不展示 Docker 容器日志。
        </div>
      </div>
    </template>

    <template v-else-if="!containerName">
      <div class="empty-state-card">
        <div class="empty-state-title">未配置容器名称</div>
        <div class="empty-state-desc">
          当前项目未配置 container_name，无法查询容器日志。
        </div>
      </div>
    </template>

    <template v-else>
      <div class="panel-header">
        <div class="panel-header-left">
          <div class="panel-title">容器日志</div>
          <div class="panel-subtitle">
            基于 docker logs 获取容器运行日志，默认拉取最后 50 行
          </div>
        </div>

        <div class="panel-actions">
          <button
            class="action-btn action-btn-secondary"
            :disabled="loading || !logsText"
            @click="copyLogs"
          >
            复制日志
          </button>

          <button
            class="action-btn action-btn-primary"
            :disabled="loading"
            @click="loadLogs"
          >
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>

      <div class="filter-bar">
        <div class="filter-item">
          <div class="filter-label">最近行数</div>
          <el-input-number
            v-model="queryForm.tail"
            :min="1"
            :max="2000"
            :step="50"
            controls-position="right"
            class="filter-number"
          />
        </div>

        <div class="filter-item">
          <div class="filter-label">起始时间</div>
          <el-input
            v-model="queryForm.since"
            placeholder="如 10m / 1h / 2026-04-03T10:00:00"
            clearable
          />
        </div>

        <div class="filter-item">
          <div class="filter-label">结束时间</div>
          <el-input
            v-model="queryForm.until"
            placeholder="如 5m / 2026-04-03T11:00:00"
            clearable
          />
        </div>

        <div class="filter-item filter-item-checkbox">
          <div class="filter-label">日志选项</div>
          <el-checkbox v-model="queryForm.timestamps">
            附带时间戳
          </el-checkbox>
        </div>
      </div>

      <div class="quick-actions">
        <button class="quick-btn" :disabled="loading" @click="applyQuickTail(50)">
          最近 50 行
        </button>
        <button class="quick-btn" :disabled="loading" @click="applyQuickTail(200)">
          最近 200 行
        </button>
        <button class="quick-btn" :disabled="loading" @click="applyQuickSince('10m')">
          最近 10 分钟
        </button>
        <button class="quick-btn" :disabled="loading" @click="applyQuickSince('1h')">
          最近 1 小时
        </button>
        <button class="quick-btn quick-btn-primary" :disabled="loading" @click="loadLogs">
          查询日志
        </button>
      </div>

      <div class="summary-bar">
        <div class="summary-item">
          <span class="summary-label">容器名称</span>
          <span class="summary-value">{{ containerName }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">最近行数</span>
          <span class="summary-value">{{ queryForm.tail }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">时间戳</span>
          <span class="summary-value">{{ queryForm.timestamps ? '开启' : '关闭' }}</span>
        </div>
      </div>

      <div v-if="loading" class="loading-state-card">
        <q-spinner color="primary" size="28px" />
        <div class="loading-state-text">加载容器日志中...</div>
      </div>

      <template v-else-if="logsText">
        <div class="log-card">
          <div class="log-card-header">
            <div class="log-card-title">日志输出</div>
            <div class="log-card-meta">
              <span v-if="lastQuerySummary.since">since={{ lastQuerySummary.since }}</span>
              <span v-if="lastQuerySummary.until">· until={{ lastQuerySummary.until }}</span>
              <span>· tail={{ lastQuerySummary.tail }}</span>
            </div>
          </div>

          <pre class="log-content">{{ logsText }}</pre>
        </div>
      </template>

      <template v-else>
        <div class="empty-state-card">
          <div class="empty-state-title">暂无日志内容</div>
          <div class="empty-state-desc">
            当前条件下没有查询到日志，试试调整最近行数或时间范围。
          </div>
        </div>
      </template>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { Notify, copyToClipboard } from 'quasar'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'

type ProjectLike = {
  id?: string | number
  project_type?: string
  container_name?: string
}

type DockerLogsResponse = {
  container_name?: string
  tail?: number
  timestamps?: boolean
  since?: string | null
  until?: string | null
  logs?: string
}

const props = defineProps<{
  project: ProjectLike
}>()

const loading = ref(false)
const logsText = ref('')
const lastQuerySummary = reactive({
  tail: 50,
  timestamps: false,
  since: '',
  until: '',
})

const queryForm = reactive({
  tail: 50,
  timestamps: false,
  since: '',
  until: '',
})

const projectType = computed(() => {
  return String(props.project.project_type || '').toLowerCase().trim()
})

const containerName = computed(() => {
  return String(props.project.container_name || '').trim()
})

async function copyLogs() {
  if (!logsText.value) return

  try {
    await copyToClipboard(logsText.value)
    Notify.create({
      type: 'positive',
      message: '日志已复制',
      position: 'top',
      timeout: 1200,
    })
  } catch {
    Notify.create({
      type: 'negative',
      message: '复制日志失败',
      position: 'top',
      timeout: 1200,
    })
  }
}

function applyQuickTail(tail: number) {
  queryForm.tail = tail
  queryForm.since = ''
  queryForm.until = ''
  void loadLogs()
}

function applyQuickSince(since: string) {
  queryForm.since = since
  queryForm.until = ''
  void loadLogs()
}

async function loadLogs() {
  if (projectType.value === 'web') {
    logsText.value = ''
    return
  }

  if (!containerName.value) {
    logsText.value = ''
    return
  }

  loading.value = true
  try {
    const res: DockerLogsResponse = await provideCurrentAgentProxyApi().fetchDockerContainerLogs({
        container_name: containerName.value,
        tail: queryForm.tail,
        timestamps: queryForm.timestamps,
        since: queryForm.since || undefined,
        until: queryForm.until || undefined,
      })

    logsText.value = String(res?.logs || '').trim()

    lastQuerySummary.tail = queryForm.tail
    lastQuerySummary.timestamps = queryForm.timestamps
    lastQuerySummary.since = queryForm.since
    lastQuerySummary.until = queryForm.until
  } catch (error) {
    console.error('loadLogs error:', error)
    logsText.value = ''
    Notify.create({
      type: 'negative',
      message: '加载容器日志失败',
      position: 'top',
    })
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.project.id, props.project.project_type, props.project.container_name],
  async () => {
    queryForm.tail = 50
    queryForm.timestamps = false
    queryForm.since = ''
    queryForm.until = ''
    logsText.value = ''
    await loadLogs()
  },
  { immediate: true }
)
</script>

<style scoped>
.container-log-panel {
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

.panel-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.filter-bar {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr) minmax(0, 1fr) 180px;
  gap: 14px;
  margin-bottom: 12px;
}

.filter-item {
  min-width: 0;
}

.filter-item-checkbox {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.filter-label {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
  margin-bottom: 8px;
}

.filter-number {
  width: 100%;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
}

.quick-btn,
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

.quick-btn,
.action-btn-secondary {
  background: #fff;
  color: #334155;
  border: 1px solid #dbe4ee;
}

.quick-btn:hover:not(:disabled),
.action-btn-secondary:hover:not(:disabled) {
  border-color: #bfd2ff;
  color: #2563eb;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.08);
}

.quick-btn-primary,
.action-btn-primary {
  background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
  color: #fff;
  border: 1px solid transparent;
}

.quick-btn-primary:hover:not(:disabled),
.action-btn-primary:hover:not(:disabled) {
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2);
  transform: translateY(-1px);
}

.quick-btn:disabled,
.action-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
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
  font-size: 13px;
  color: #334155;
  font-weight: 700;
}

.log-card {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: #0f172a;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.log-card-header {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.08);
  background: rgba(255, 255, 255, 0.03);
}

.log-card-title {
  font-size: 13px;
  font-weight: 700;
  color: #e2e8f0;
}

.log-card-meta {
  margin-top: 4px;
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.5;
  word-break: break-all;
}

.log-content {
  margin: 0;
  padding: 16px;
  font-size: 12px;
  line-height: 1.7;
  color: #e2e8f0;
  overflow: auto;
  max-height: 72vh;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
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

:deep(.el-input-number),
:deep(.el-input) {
  width: 100%;
}

@media (max-width: 1080px) {
  .filter-bar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    align-items: stretch;
  }

  .panel-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .filter-bar {
    grid-template-columns: 1fr;
  }

  .summary-bar {
    gap: 10px;
  }

  .log-content {
    max-height: 56vh;
  }
}
</style>