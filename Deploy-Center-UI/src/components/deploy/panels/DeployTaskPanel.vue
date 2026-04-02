<template>
  <div class="single-panel">
    <section class="panel-card">
      <div class="panel-header">
        <div class="panel-title">部署任务</div>

        <div class="panel-actions">
          <button
            class="ui-btn ui-btn-secondary ui-btn-sm"
            :disabled="loading"
            @click="loadProjectTasks"
          >
            {{ loading ? '刷新中...' : '刷新' }}
          </button>
        </div>
      </div>

      <div class="table-wrap">
        <el-table
          v-loading="loading"
          :data="records"
          border
          stripe
          style="width: 100%"
          empty-text="暂无部署任务"
        >
          <el-table-column prop="id" label="ID" width="120" />

          <el-table-column prop="operator_name" label="操作人" width="120" />

          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)" effect="light" round>
                {{ formatStatus(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="触发方式" width="120">
            <template #default="scope">
              {{ formatTriggerType(scope.row.trigger_type) }}
            </template>
          </el-table-column>

          <el-table-column label="部署方式" width="120">
            <template #default="scope">
              {{ formatDeployMechanism(scope.row.deploy_mechanism) }}
            </template>
          </el-table-column>

          <el-table-column label="耗时" width="120">
            <template #default="scope">
              {{ formatDuration(scope.row.duration_ms) }}
            </template>
          </el-table-column>

          <el-table-column label="提交时间" min-width="220">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }} ({{ formatTimeAgo(scope.row.created_at) }}前)
            </template>
          </el-table-column>

          <el-table-column label="操作" width="100" fixed="right">
            <template #default="scope">
              <div class="action-group">
                <button
                  class="table-action-btn table-action-info"
                  title="查看详情"
                  @click="openDetail(scope.row)"
                >
                  详情
                </button>

                <button
                  v-if="canCancel(scope.row.status)"
                  class="table-action-btn table-action-warning"
                  title="中止任务"
                  @click="handleCancel(scope.row)"
                >
                  中止
                </button>

                <button
                  v-if="canDelete(scope.row.status)"
                  class="table-action-btn table-action-danger"
                  title="删除任务"
                  @click="handleDelete(scope.row)"
                >
                  删除
                </button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </section>

    <el-dialog
      v-model="detailDialogVisible"
      title="部署任务详情"
      width="760px"
      destroy-on-close
    >
      <template v-if="currentTask">
        <div class="detail-grid">
          <div class="detail-item">
            <div class="detail-label">任务ID</div>
            <div class="detail-value">{{ currentTask.id }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">状态</div>
            <div class="detail-value">
              <el-tag :type="getStatusTagType(currentTask.status)" effect="light" round>
                {{ formatStatus(currentTask.status) }}
              </el-tag>
            </div>
          </div>

          <div class="detail-item">
            <div class="detail-label">操作人ID</div>
            <div class="detail-value">{{ currentTask.operator_id || '-' }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">操作人</div>
            <div class="detail-value">{{ currentTask.operator_name || '-' }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">触发方式</div>
            <div class="detail-value">{{ formatTriggerType(currentTask.trigger_type) }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">部署方式</div>
            <div class="detail-value">{{ formatDeployMechanism(currentTask.deploy_mechanism) }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">上传文件</div>
            <div class="detail-value break-all">{{ currentTask.upload_file_name || '-' }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">容器名称</div>
            <div class="detail-value break-all">{{ currentTask.container_name || '-' }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">镜像名称</div>
            <div class="detail-value break-all">{{ currentTask.build_image_name || '-' }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">镜像标签</div>
            <div class="detail-value">{{ currentTask.build_image_tag || '-' }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">提交时间</div>
            <div class="detail-value">{{ formatDate(currentTask.created_at) }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">开始时间</div>
            <div class="detail-value">{{ formatDate(currentTask.started_at) }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">完成时间</div>
            <div class="detail-value">{{ formatDate(currentTask.finished_at) }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">耗时</div>
            <div class="detail-value">{{ formatDuration(currentTask.duration_ms) }}</div>
          </div>
        </div>

        <div v-if="currentTask.failed_reason" class="detail-block">
          <div class="detail-block-title">失败原因</div>
          <div class="detail-block-content failed-reason-box">
            {{ currentTask.failed_reason }}
          </div>
        </div>

        <div v-if="currentTask.dockerfile_content" class="detail-block">
          <div class="detail-block-title">Dockerfile</div>
          <pre class="code-block">{{ currentTask.dockerfile_content }}</pre>
        </div>

        <div v-if="currentTask.dockercommand_content" class="detail-block">
          <div class="detail-block-title">Docker Command</div>
          <pre class="code-block">{{ currentTask.dockercommand_content }}</pre>
        </div>

      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Notify, Dialog } from 'quasar'
import { formatDate, formatTimeAgo } from 'src/utils/dateFormatter'
import { formatDuration } from 'src/utils/displayFormatter'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'
import type { DeployTask } from 'src/types/DeployTask'

type DeployTaskWithProjectInfo = DeployTask & {
  project_code?: string
  project_name?: string
}

const props = defineProps<{
  projectId: string | number
}>()

const loading = ref(false)
const records = ref<DeployTaskWithProjectInfo[]>([])
const detailDialogVisible = ref(false)
const currentTask = ref<DeployTaskWithProjectInfo | null>(null)

function getStatusTagType(status?: string) {
  const value = String(status || '').toUpperCase()

  if (value === 'SUCCESS') return 'success'
  if (value === 'FAILED') return 'danger'
  if (value === 'RUNNING') return 'warning'
  if (value === 'PENDING') return 'info'
  return 'info'
}

function formatStatus(status?: string) {
  const value = String(status || '').toUpperCase()

  if (value === 'PENDING') return '等待中'
  if (value === 'RUNNING') return '部署中'
  if (value === 'SUCCESS') return '成功'
  if (value === 'FAILED') return '失败'
  if (value === 'CANCELLED') return '已取消'
  return status || '-'
}

function formatTriggerType(value?: string) {
  const type = String(value || '').toUpperCase()
  if (type === 'MANUAL') return '手动触发'
  if (type === 'SCHEDULED') return '定时触发'
  return value || '-'
}

function formatDeployMechanism(value?: string) {
  const mechanism = String(value || '').toUpperCase()
  if (mechanism === 'UPLOAD') return '上传部署'
  if (mechanism === 'CLOUD_BUILD') return '云构建部署'
  return value || '-'
}

function canCancel(status?: string) {
  const value = String(status || '').toUpperCase()
  return ['PENDING', 'RUNNING'].includes(value)
}

function canDelete(status?: string) {
  const value = String(status || '').toUpperCase()
  return ['SUCCESS', 'FAILED', 'CANCELLED'].includes(value)
}

function openDetail(task: DeployTaskWithProjectInfo) {
  currentTask.value = task
  detailDialogVisible.value = true
}

async function handleCancel(task: DeployTaskWithProjectInfo) {
  Dialog.create({
    title: '确认中止',
    message: `确定要中止任务 ${task.id} 吗？`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      Notify.create({
        type: 'warning',
        message: '中止任务暂未实现',
        position: 'top',
      })
    } catch (error) {
      console.error(error)
      Notify.create({
        type: 'negative',
        message: '中止任务失败',
        position: 'top',
      })
    }
  })
}

async function handleDelete(task: DeployTaskWithProjectInfo) {
  Dialog.create({
    title: '确认删除',
    message: `确定要删除任务 ${task.id} 吗？`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await provideCurrentAgentProxyApi().deleteDeployTask(task.id)
      records.value = records.value.filter(item => item.id !== task.id)

      Notify.create({
        type: 'positive',
        message: '删除成功',
        position: 'top',
      })

    } catch (error) {
      console.error(error)
      Notify.create({
        type: 'negative',
        message: '删除任务失败',
        position: 'top',
      })
    }
  })
}

async function loadProjectTasks() {
  const currentProjectId = String(props.projectId || '').trim()

  if (!currentProjectId) {
    records.value = []
    return
  }

  loading.value = true
  try {
    const taskList = await provideCurrentAgentProxyApi().fetchDeployTaskList()

    records.value = (taskList || [])
      .filter((item: DeployTaskWithProjectInfo) => String(item.project_id || '') === currentProjectId)
      .sort((a: DeployTaskWithProjectInfo, b: DeployTaskWithProjectInfo) => {
        const timeA = new Date(a.created_at || 0).getTime()
        const timeB = new Date(b.created_at || 0).getTime()
        return timeB - timeA
      })
  } catch (error) {
    console.error('加载部署任务失败:', error)
    records.value = []
    Notify.create({
      type: 'negative',
      message: '加载部署任务失败',
      position: 'top',
    })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadProjectTasks()
})

watch(
  () => props.projectId,
  async () => {
    await loadProjectTasks()
  }
)
</script>

<style scoped>
.single-panel {
  height: 100%;
}

.panel-card {
  border-radius: 20px;
  background: rgba(250, 250, 250, 0.78);
  border: 1px solid rgba(15, 23, 42, 0.06);
  overflow: hidden;
}

.panel-header {
  padding: 18px 20px 14px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-title {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-wrap {
  padding: 16px 20px;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-action-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  padding: 0;
}

.table-action-info {
  color: #2563eb;
}

.table-action-warning {
  color: #d97706;
}

.table-action-danger {
  color: #dc2626;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 18px;
}

.detail-item {
  min-width: 0;
}

.detail-label {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 14px;
  color: #0f172a;
  line-height: 1.6;
  word-break: break-word;
}

.detail-block {
  margin-top: 18px;
}

.detail-block-title {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  margin-bottom: 8px;
}

.detail-block-content {
  font-size: 13px;
  line-height: 1.7;
  color: #475569;
}

.failed-reason-box {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 12px;
  padding: 12px 14px;
  color: #9a3412;
  white-space: pre-wrap;
  word-break: break-word;
}

.code-block {
  margin: 0;
  padding: 14px;
  border-radius: 12px;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 12px;
  line-height: 1.7;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.break-all {
  word-break: break-all;
}

.ui-btn {
  border: none;
  border-radius: 12px;
  height: 38px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s ease;
}

.ui-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.ui-btn-secondary {
  background: #fff;
  color: #334155;
  border: 1px solid #dbe4ee;
}

.ui-btn-secondary:hover:not(:disabled) {
  border-color: #bfd2ff;
  color: #2563eb;
}

.ui-btn-sm {
  height: 32px;
  padding: 0 12px;
  font-size: 12px;
}

:deep(.el-tag) {
  border-radius: 999px;
  font-weight: 700;
  border: none;
}
</style>