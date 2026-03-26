<template>
  <div class="deploy-grid">
    <section class="panel-card">
      <div class="panel-header">
        <div class="panel-title">部署设置</div>
        <div class="panel-actions">
          <button
            class="ui-btn ui-btn-primary"
            :disabled="isDeploying || !fileList.length"
            @click="handleDeploy"
          >
            开始部署
          </button>

          <button
            v-if="isDeploying"
            class="ui-btn ui-btn-danger"
            @click="handleAbort"
          >
            中止部署
          </button>
        </div>
      </div>

      <div class="panel-body">
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
          />
        </div>
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
import { ref } from 'vue'
import { Notify, copyToClipboard } from 'quasar'

type LogType = 'info' | 'success' | 'error'
type UploadFileItem = {
  uid?: number
  name?: string
  percentage?: number
  raw?: File
  size?: number
  status?: string
}

interface LogLine {
  time: string
  text: string
  type: LogType
}

const fileList = ref<UploadFileItem[]>([])
const uploadProgress = ref(0)
const isDeploying = ref(false)
const logs = ref<LogLine[]>([])

function handleFileChange(file: UploadFileItem) {
  fileList.value = [file]
}

function appendLog(text: string, type: LogType = 'info') {
  logs.value.push({
    time: new Date().toLocaleTimeString(),
    text,
    type,
  })
}

async function handleDeploy() {
  if (!fileList.value.length) {
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

  try {
    appendLog('开始上传 dist 压缩包')
    uploadProgress.value = 100
    await sleep(700)
    appendLog('压缩包上传完成', 'success')

    appendLog('开始解压并同步到目标目录')
    await sleep(600)
    appendLog('解压部署完成', 'success')

    appendLog('正在更新静态资源')
    await sleep(500)
    appendLog('站点资源更新完成', 'success')

    appendLog('归档本次部署产物与记录')
    await sleep(400)
    appendLog('归档完成', 'success')

    Notify.create({
      type: 'positive',
      message: '部署成功',
      position: 'top',
    })
  } catch {
    appendLog('部署失败', 'error')
    Notify.create({
      type: 'negative',
      message: '部署失败',
      position: 'top',
    })
  } finally {
    isDeploying.value = false
  }
}

function handleAbort() {
  isDeploying.value = false
  appendLog('已中止部署', 'error')
  Notify.create({
    type: 'warning',
    message: '已中止',
    position: 'top',
  })
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

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
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

.deploy-upload-shell {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.upload-title-wrap {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.control-label {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
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
  margin-top: 4px;
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

.line-error .terminal-text {
  color: #fca5a5;
}

.terminal-empty {
  color: #94a3b8;
  font-size: 13px;
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

:deep(.el-tag) {
  border-radius: 999px;
  font-weight: 700;
  border: none;
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

  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>