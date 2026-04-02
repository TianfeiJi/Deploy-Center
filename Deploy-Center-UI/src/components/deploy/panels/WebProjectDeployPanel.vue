<template>
  <div class="deploy-grid">
    <section class="panel-card">
      <div class="panel-header">
        <div class="panel-title">部署设置</div>
        <div class="panel-actions">
          <button
            v-if="!isDeploying"
            class="ui-btn ui-btn-primary"
            :disabled="isPrimaryActionDisabled"
            @click="handlePrimaryDeployAction"
          >
            {{ primaryActionLabel }}
          </button>

          <button
            v-else
            class="ui-btn ui-btn-primary is-deploying"
            @click="handleAbort"
            title="点击中止部署"
          >
            <span class="deploying-inner">
              <q-spinner size="14px" color="white" class="deploying-spinner" />
              <span class="deploying-text">部署中</span>
              <span class="abort-text">中止</span>
            </span>
          </button>
        </div>
      </div>

      <div class="panel-body">
        <div class="control-grid">
          <div class="control-block">
            <div class="control-label">部署机制</div>
            <div class="toggle-group">
              <button
                class="toggle-btn"
                :class="{ active: deployMechanism === 'upload' }"
                @click="setDeployMechanism('upload')"
              >
                上传部署
              </button>
              <button
                class="toggle-btn"
                :class="{ active: deployMechanism === 'cloud' }"
                @click="setDeployMechanism('cloud')"
              >
                云构建部署
              </button>
            </div>
          </div>

          <div class="control-block">
            <div class="control-label">执行方式</div>
            <div class="toggle-group">
              <button
                class="toggle-btn"
                :class="{ active: executionMode === 'manual' }"
                @click="executionMode = 'manual'"
              >
                立即执行
              </button>
              <button
                class="toggle-btn"
                :class="{ active: executionMode === 'schedule' }"
                @click="executionMode = 'schedule'"
              >
                定时执行
              </button>
            </div>
          </div>
        </div>

        <div v-if="executionMode === 'schedule'" class="schedule-box">
          <div class="inner-section-title">定时配置</div>

          <el-form label-width="110px" class="detail-form-grid">
            <el-form-item label="Cron 表达式" class="full-span">
              <el-input v-model="scheduleForm.cron" placeholder="例如：0 0 2 * * *" />
            </el-form-item>

            <el-form-item label="任务名称">
              <el-input v-model="scheduleForm.job_name" placeholder="例如：凌晨静态资源发布" />
            </el-form-item>

            <el-form-item label="失败策略">
              <el-select v-model="scheduleForm.failure_policy" style="width: 100%">
                <el-option label="仅记录失败" value="record_only" />
                <el-option label="自动通知" value="notify" />
                <el-option label="暂停计划" value="pause" />
              </el-select>
            </el-form-item>

            <el-form-item label="备注" class="full-span">
              <el-input v-model="scheduleForm.remark" type="textarea" :rows="3" />
            </el-form-item>
          </el-form>
        </div>

        <template v-if="deployMechanism === 'upload'">
          <div class="deploy-upload-shell">
            <div class="upload-title-wrap">
              <div class="control-label">上传 dist 压缩包</div>
              <div class="upload-subtext">仅支持构建后的 zip 产物</div>
            </div>

            <el-upload
              drag
              accept=".zip"
              :auto-upload="false"
              :on-change="handleFileChange"
              :file-list="fileList"
              :limit="1"
              :disabled="isDeploying"
              class="web-upload"
            >
              <div class="upload-inner">
                <q-icon name="cloud_upload" size="32px" class="upload-icon" />
                <div class="upload-main-text">将 dist.zip 拖到此处，或点击上传</div>
                <div class="upload-tip-text">必须是打包后的 dist 压缩包（zip 格式）</div>
              </div>
            </el-upload>

            <el-progress
              v-if="uploadProgress > 0"
              class="upload-progress"
              :percentage="uploadProgress"
              :text-inside="true"
              :stroke-width="14"
              :status="uploadProgress === 100 ? 'success' : undefined"
            />
          </div>
        </template>

        <template v-else>
          <div class="placeholder-box">
            <div class="placeholder-title">云构建部署暂未支持</div>
            <div class="placeholder-desc">
              这里预留远端构建、制品管理与静态资源分发能力。
            </div>
            <div class="inline-actions">
              <button class="ui-btn ui-btn-secondary" @click="notifyCloudBuildUnsupported">
                暂不支持
              </button>
            </div>
          </div>
        </template>
      </div>
    </section>

    <section class="panel-card">
      <div class="panel-header">
        <div class="panel-title">部署日志</div>
        <div class="panel-actions">
          <button class="ui-btn ui-btn-sm ui-btn-secondary" @click="copyLogs">
            复制
          </button>
          <button class="ui-btn ui-btn-sm ui-btn-secondary" @click="clearLogs">
            清空
          </button>
        </div>
      </div>

      <div class="terminal-box">
        <div
          v-for="(line, i) in logs"
          :key="i"
          class="terminal-line"
          :class="`line-${line.type}`"
        >
          <span class="terminal-time">[{{ line.time }}]</span>
          <span class="terminal-text">{{ line.text }}</span>
        </div>

        <div v-if="!logs.length" class="terminal-empty">
          暂无日志输出
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AxiosProgressEvent } from 'axios'
import { Notify, copyToClipboard } from 'quasar'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'

type DeployMechanism = 'upload' | 'cloud'
type ExecutionMode = 'manual' | 'schedule'
type LogType = 'info' | 'success' | 'warning' | 'error'

type UploadFileItem = {
  uid?: number
  name?: string
  percentage?: number
  raw?: File
  size?: number
  status?: string
}

type ScheduleForm = {
  cron: string
  job_name: string
  failure_policy: 'record_only' | 'notify' | 'pause'
  remark: string
}

interface LogLine {
  time: string
  text: string
  type: LogType
}

const props = defineProps<{
  projectId: string
}>()

const deployMechanism = ref<DeployMechanism>('upload')
const executionMode = ref<ExecutionMode>('manual')

const fileList = ref<UploadFileItem[]>([])
const uploadProgress = ref(0)
const isDeploying = ref(false)
const logs = ref<LogLine[]>([])

const scheduleForm = ref<ScheduleForm>({
  cron: '',
  job_name: '',
  failure_policy: 'record_only',
  remark: '',
})

function getAgentApi() {
  return provideCurrentAgentProxyApi()
}

const primaryActionLabel = computed(() => {
  if (executionMode.value === 'schedule') return '创建定时部署'
  if (deployMechanism.value === 'cloud') return '发起云构建'
  return '开始部署'
})

const isPrimaryActionDisabled = computed(() => {
  if (isDeploying.value) return true
  if (executionMode.value === 'schedule') return !scheduleForm.value.cron?.trim()
  if (deployMechanism.value === 'cloud') return false
  return !fileList.value.length
})

function formatNow() {
  const d = new Date()
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  return `${hh}:${mm}:${ss}`
}

function appendLog(text: string, type: LogType = 'info') {
  logs.value.push({
    time: formatNow(),
    text,
    type,
  })
}

function setDeployMechanism(mode: DeployMechanism) {
  deployMechanism.value = mode
  if (mode === 'cloud') {
    Notify.create({
      type: 'warning',
      message: '云构建暂不支持',
      position: 'top',
    })
  }
}

function notifyCloudBuildUnsupported() {
  Notify.create({
    type: 'warning',
    message: '云构建暂不支持',
    position: 'top',
  })
}

function handleFileChange(file: UploadFileItem) {
  fileList.value = [file]
}

function handleAbort() {
  appendLog('用户中止部署', 'warning')
  isDeploying.value = false

  Notify.create({
    type: 'warning',
    message: '已中止',
    position: 'top',
  })
}

async function handlePrimaryDeployAction() {
  if (executionMode.value === 'schedule') {
    Notify.create({
      type: 'info',
      message: '定时部署暂未实现',
      position: 'top',
    })
    return
  }

  if (deployMechanism.value === 'cloud') {
    notifyCloudBuildUnsupported()
    return
  }

  await handleDeploy()
}

async function handleDeploy() {
  const file = fileList.value[0]?.raw
  if (!file) {
    Notify.create({
      type: 'negative',
      message: '请选择上传文件',
      position: 'top',
    })
    return
  }

  isDeploying.value = true
  uploadProgress.value = 0
  logs.value = []

  appendLog(`开始部署：${file.name}`)
  appendLog(`部署机制：${deployMechanism.value === 'cloud' ? '云构建部署' : '上传部署'}`)
  appendLog(`触发方式：${executionMode.value === 'schedule' ? '定时触发' : '手动触发'}`)

  try {
    appendLog('开始上传 dist 压缩包')

    const fd = new FormData()
    fd.append('file', file)
    fd.append('project_id', String(props.projectId))
    fd.append('task_name', 'Web 项目部署')
    fd.append('trigger_type', executionMode.value === 'schedule' ? 'SCHEDULED' : 'MANUAL')
    fd.append('deploy_mechanism', deployMechanism.value === 'cloud' ? 'CLOUD_BUILD' : 'UPLOAD')

    const result = await getAgentApi().deployWebProject(fd, {
      onUploadProgress: (e: AxiosProgressEvent) => {
        if (e.total) {
          uploadProgress.value = Math.round((e.loaded / e.total) * 100)
        }
      },
    })

    appendLog(`部署任务提交成功，任务ID：${result?.data?.task_id || '-'}`, 'success')

    uploadProgress.value = 100

    Notify.create({
      type: 'positive',
      message: '部署任务已提交',
      position: 'top',
    })
  } catch (e: any) {
    console.error(e)
    appendLog(e?.message || '部署失败', 'error')

    Notify.create({
      type: 'negative',
      message: '部署失败',
      position: 'top',
    })

    uploadProgress.value = 0
  } finally {
    isDeploying.value = false
  }
}

async function copyLogs() {
  const text = logs.value.map((i) => `[${i.time}] ${i.text}`).join('\n')
  if (!text.trim()) return

  await copyToClipboard(text)
  Notify.create({
    type: 'positive',
    message: '已复制',
    position: 'top',
  })
}

function clearLogs() {
  logs.value = []
}
</script>

<style scoped>
.deploy-grid {
  display: grid;
  grid-template-rows: auto minmax(320px, 1fr);
  gap: 16px;
  min-height: 680px;
}

.panel-card {
  border-radius: 20px;
  background: rgba(250, 250, 250, 0.78);
  border: 1px solid rgba(15, 23, 42, 0.06);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding: 18px 20px 14px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.85);
}

.panel-title {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.25;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.panel-body {
  padding: 18px 20px 20px;
}

.control-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.control-block {
  min-width: 0;
}

.control-label {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  margin-bottom: 10px;
}

.toggle-group {
  display: inline-flex;
  gap: 8px;
  flex-wrap: wrap;
}

.toggle-btn {
  border: 1px solid #dbe4ee;
  background: #fff;
  color: #475569;
  height: 38px;
  padding: 0 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s ease;
}

.toggle-btn:hover {
  border-color: #bfd2ff;
  color: #2563eb;
}

.toggle-btn.active {
  background: rgba(37, 99, 235, 0.08);
  border-color: rgba(37, 99, 235, 0.28);
  color: #2563eb;
}

.schedule-box,
.placeholder-box,
.deploy-upload-shell {
  margin-top: 18px;
}

.upload-title-wrap {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.upload-subtext {
  font-size: 12px;
  color: #94a3b8;
}

.upload-inner {
  padding: 8px 0;
  text-align: center;
}

.upload-icon {
  color: #38bdf8;
  margin-bottom: 8px;
}

.upload-main-text {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
}

.upload-tip-text {
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
}

.upload-progress {
  margin-top: 12px;
}

.inner-section-title {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 10px;
}

.inline-actions {
  margin-top: 14px;
  display: flex;
  gap: 10px;
}

.placeholder-title {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
}

.placeholder-desc {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.7;
  color: #64748b;
}

.terminal-box {
  min-height: 320px;
  overflow: auto;
  padding: 16px 18px;
  background: #0f172a;
  font-family: Consolas, Monaco, monospace;
}

.terminal-line {
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.terminal-line + .terminal-line {
  margin-top: 4px;
}

.terminal-time {
  color: #94a3b8;
  margin-right: 8px;
}

.terminal-text {
  color: #e2e8f0;
}

.line-info .terminal-text {
  color: #cbd5e1;
}

.line-success .terminal-text {
  color: #86efac;
}

.line-warning .terminal-text {
  color: #fde68a;
}

.line-error .terminal-text {
  color: #fca5a5;
}

.terminal-empty {
  color: #94a3b8;
  font-size: 13px;
}

.detail-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.full-span {
  grid-column: 1 / -1;
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

.ui-btn-primary {
  background: #0ea5e9;
  color: white;
}

.ui-btn-primary:hover:not(:disabled) {
  background: #0284c7;
}

.ui-btn-secondary {
  background: white;
  color: #334155;
  border: 1px solid #dbe4ee;
}

.ui-btn-secondary:hover:not(:disabled) {
  border-color: #bae6fd;
  color: #0284c7;
}

.ui-btn-danger {
  background: rgba(239, 68, 68, 0.08);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.ui-btn-danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.12);
}

.ui-btn-sm {
  height: 32px;
  padding: 0 12px;
  font-size: 12px;
}

.is-deploying {
  position: relative;
  overflow: hidden;
}

.deploying-inner {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.abort-text {
  display: none;
}

.is-deploying:hover .deploying-spinner,
.is-deploying:hover .deploying-text {
  display: none;
}

.is-deploying:hover .abort-text {
  display: inline;
}

:deep(.web-upload .el-upload-dragger) {
  width: 100%;
  border-radius: 18px;
  border: 1px dashed #cbd5e1;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  transition: all 0.18s ease;
  padding: 18px 12px;
}

:deep(.web-upload .el-upload-dragger:hover) {
  border-color: #7dd3fc;
  background: linear-gradient(180deg, #ffffff 0%, #f0f9ff 100%);
}

@media (max-width: 980px) {
  .deploy-grid {
    grid-template-rows: auto auto;
    min-height: unset;
  }

  .control-grid,
  .detail-form-grid {
    grid-template-columns: 1fr;
  }

  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>