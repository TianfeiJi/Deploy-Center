<template>
  <div class="deploy-grid">
    <section class="panel-card">
      <div class="panel-header">
        <div class="panel-title">部署设置</div>

        <div class="panel-actions">
          <button v-if="!isDeploying" class="ui-btn ui-btn-primary" :disabled="isPrimaryActionDisabled"
            @click="handlePrimaryDeployAction">
            {{ primaryActionLabel }}
          </button>

          <button v-else class="ui-btn ui-btn-primary is-deploying" @click="handleAbortDeploy" title="点击中止部署">
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
              <button class="toggle-btn" :class="{ active: deployMechanism === 'upload' }"
                @click="setDeployMechanism('upload')">
                上传部署
              </button>
              <button class="toggle-btn" :class="{ active: deployMechanism === 'cloud' }"
                @click="setDeployMechanism('cloud')">
                云构建部署
              </button>
            </div>
          </div>

          <div class="control-block">
            <div class="control-label">执行方式</div>
            <div class="toggle-group">
              <button class="toggle-btn" :class="{ active: executionMode === 'manual' }"
                @click="executionMode = 'manual'">
                立即执行
              </button>
              <button class="toggle-btn" :class="{ active: executionMode === 'schedule' }"
                @click="executionMode = 'schedule'">
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
              <el-input v-model="scheduleForm.job_name" placeholder="例如：凌晨发版任务" />
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
          <div class="editor-stack">
            <div class="editor-block">
              <div class="inner-section-title">Jar 包</div>

              <el-upload ref="uploadRef" drag :auto-upload="false" accept=".jar" :on-change="handleFileChange"
                :file-list="fileList" :disabled="uploadProgress > 0 || isDeploying">
                <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>

                <template #tip>
                  <div class="el-upload__tip upload-tip">
                    只能上传 .jar 文件，且一次仅允许一个文件
                  </div>
                </template>
              </el-upload>

              <el-progress v-if="uploadProgress > 0" class="q-mt-md" :percentage="uploadProgress" :text-inside="true"
                :stroke-width="14" :status="uploadProgress === 100 ? 'success' : undefined" />
            </div>

            <div class="aligned-editor-grid">
              <div class="editor-column">
                <div class="editor-column-header">
                  <div class="template-header">
                    <div class="inner-section-title">Dockerfile 模板</div>

                    <div class="template-actions">
                      <el-select v-model="selectedDockerfileTemplateId" class="template-select" placeholder="选择模板"
                        :disabled="isDeploying || dockerfileTemplateLoading" @change="handleDockerfileTemplateChange">
                        <el-option v-for="item in dockerfileTemplates" :key="item.id" :label="item.template_name"
                          :value="item.id" />
                      </el-select>

                      <button class="text-action-btn" :disabled="isDeploying"
                        @click="openCreateDockerfileTemplateDialog">
                        新增模板
                      </button>
                    </div>
                  </div>
                </div>

                <div class="editor-rendered-tip">
                  以下内容为基于当前 Dockerfile 模板渲染后的结果，可继续手动调整
                </div>

                <div class="editor-column-body">
                  <CodeEditorBox v-model="dockerfileContent" :disabled="isDeploying" :min-rows="16" :max-rows="16" />
                </div>
              </div>

              <div class="editor-column">
                <div class="editor-column-header">
                  <div class="template-header">
                    <div class="inner-section-title">Docker Command 模板</div>

                    <div class="template-actions">
                      <el-select v-model="selectedDockercommandTemplateId" class="template-select" placeholder="选择模板"
                        :disabled="isDeploying || dockercommandTemplateLoading"
                        @change="handleDockercommandTemplateChange">
                        <el-option v-for="item in dockercommandTemplates" :key="item.id" :label="item.template_name"
                          :value="item.id" />
                      </el-select>

                      <button class="text-action-btn" :disabled="isDeploying"
                        @click="openCreateDockercommandTemplateDialog">
                        新增模板
                      </button>
                    </div>
                  </div>
                </div>

                <div class="editor-rendered-tip">
                  以下内容为基于当前 Docker Command 模板渲染后的结果，可继续手动调整
                </div>

                <div class="editor-column-body">
                  <CodeEditorBox v-model="dockerCommand" :disabled="isDeploying" :min-rows="16" :max-rows="16" />
                </div>
              </div>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="placeholder-box">
            <div class="placeholder-title">云构建部署暂未支持</div>
            <div class="placeholder-desc">
              这里预留远端构建、镜像产出、制品管理与多节点分发能力。
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
          <button class="ui-btn ui-btn-secondary ui-btn-sm" @click="copyLogs">复制日志</button>
        </div>
      </div>

      <div class="terminal-box">
        <div v-for="(line, index) in logLines" :key="index" class="terminal-line" :class="`line-${line.type}`">
          <span class="terminal-time">[{{ line.time }}]</span>
          <span class="terminal-text">{{ line.text }}</span>
        </div>

        <div v-if="!logLines.length" class="terminal-empty">
          暂无日志输出。开始部署后，这里会显示过程日志。
        </div>
      </div>
    </section>

    <el-dialog v-model="createDockerfileTemplateDialogVisible" title="新增 Dockerfile 模板" width="720px" destroy-on-close>
      <el-form label-width="96px">
        <el-form-item label="模板名称">
          <el-input v-model="newDockerfileTemplate.template_name" placeholder="例如：SpringBoot 基础模板" />
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="newDockerfileTemplate.description" placeholder="模板说明，可选" />
        </el-form-item>

        <el-form-item label="模板内容">
          <div class="dialog-editor-wrap">
            <CodeEditorBox v-model="newDockerfileTemplate.content" :min-rows="16" :max-rows="16" />
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <button class="ui-btn ui-btn-secondary" @click="createDockerfileTemplateDialogVisible = false">
          取消
        </button>
        <button class="ui-btn ui-btn-primary" :disabled="creatingDockerfileTemplate"
          @click="confirmCreateDockerfileTemplate">
          {{ creatingDockerfileTemplate ? '保存中...' : '保存模板' }}
        </button>
      </template>
    </el-dialog>

    <el-dialog v-model="createDockercommandTemplateDialogVisible" title="新增 Docker Command 模板" width="720px"
      destroy-on-close>
      <el-form label-width="96px">
        <el-form-item label="模板名称">
          <el-input v-model="newDockercommandTemplate.template_name" placeholder="例如：标准启动命令模板" />
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="newDockercommandTemplate.description" placeholder="模板说明，可选" />
        </el-form-item>

        <el-form-item label="模板内容">
          <div class="dialog-editor-wrap">
            <CodeEditorBox v-model="newDockercommandTemplate.content" :min-rows="14" />
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <button class="ui-btn ui-btn-secondary" @click="createDockercommandTemplateDialogVisible = false">
          取消
        </button>
        <button class="ui-btn ui-btn-primary" :disabled="creatingDockercommandTemplate"
          @click="confirmCreateDockercommandTemplate">
          {{ creatingDockercommandTemplate ? '保存中...' : '保存模板' }}
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { Notify, copyToClipboard } from 'quasar'
import type { AxiosProgressEvent } from 'axios'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'
import CodeEditorBox from 'components/deploy/common/CodeEditorBox.vue'

type DeployMechanism = 'upload' | 'cloud'
type ExecutionMode = 'manual' | 'schedule'

type LogLine = {
  time: string
  text: string
  type: 'info' | 'success' | 'warning' | 'error'
}

type ScheduleForm = {
  cron: string
  job_name: string
  failure_policy: 'record_only' | 'notify' | 'pause'
  remark: string
}

type Template = {
  id: string
  template_name: string
  relative_path?: string
  template_type: string
  project_type: string
  description?: string
  created_at?: string | null
  updated_at?: string | null
}

const props = defineProps<{
  projectId: string
}>()

const emit = defineEmits<{
  (e: 'deploy-success'): void
}>()

const uploadRef = ref()
const deployMechanism = ref<DeployMechanism>('upload')
const executionMode = ref<ExecutionMode>('manual')

const fileList = ref<any[]>([])
const uploadProgress = ref(0)
const dockerfileContent = ref('')
const dockerCommand = ref('')
const isDeploying = ref(false)

const scheduleForm = ref<ScheduleForm>({
  cron: '',
  job_name: '',
  failure_policy: 'record_only',
  remark: '',
})

const logLines = ref<LogLine[]>([])

const dockerfileTemplates = ref<Template[]>([])
const dockercommandTemplates = ref<Template[]>([])

const dockerfileTemplateLoading = ref(false)
const dockercommandTemplateLoading = ref(false)

const selectedDockerfileTemplateId = ref('')
const selectedDockercommandTemplateId = ref('')

const createDockerfileTemplateDialogVisible = ref(false)
const createDockercommandTemplateDialogVisible = ref(false)

const creatingDockerfileTemplate = ref(false)
const creatingDockercommandTemplate = ref(false)

const newDockerfileTemplate = ref({
  template_name: '',
  description: '',
  content: '',
})

const newDockercommandTemplate = ref({
  template_name: '',
  description: '',
  content: '',
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

function appendLog(text: string, type: LogLine['type'] = 'info') {
  logLines.value.push({
    time: formatNow(),
    text,
    type,
  })
}

async function loadDockerfileTemplates() {
  dockerfileTemplateLoading.value = true
  try {
    const api = getAgentApi()
    const list = await api.fetchTemplateList('dockerfile')
    dockerfileTemplates.value = (list || []).filter((item: Template) => {
      return item.template_type === 'dockerfile' && item.project_type === 'java'
    })

    if (!selectedDockerfileTemplateId.value && dockerfileTemplates.value.length > 0) {
      selectedDockerfileTemplateId.value = dockerfileTemplates.value[0].id
      await loadDockerfileRenderedContent()
    }
  } catch (e) {
    console.error('loadDockerfileTemplates error:', e)
    Notify.create({
      type: 'negative',
      message: '加载 Dockerfile 模板失败',
      position: 'top',
    })
  } finally {
    dockerfileTemplateLoading.value = false
  }
}

async function loadDockercommandTemplates() {
  dockercommandTemplateLoading.value = true
  try {
    const api = getAgentApi()
    const list = await api.fetchTemplateList('dockercommand')
    dockercommandTemplates.value = (list || []).filter((item: Template) => {
      return item.template_type === 'dockercommand' && item.project_type === 'java'
    })

    if (!selectedDockercommandTemplateId.value && dockercommandTemplates.value.length > 0) {
      selectedDockercommandTemplateId.value = dockercommandTemplates.value[0].id
      await loadDockercommandRenderedContent()
    }
  } catch (e) {
    console.error('loadDockercommandTemplates error:', e)
    Notify.create({
      type: 'negative',
      message: '加载 Docker Command 模板失败',
      position: 'top',
    })
  } finally {
    dockercommandTemplateLoading.value = false
  }
}

async function loadDockerfileRenderedContent() {
  if (!props.projectId || !selectedDockerfileTemplateId.value) return

  try {
    const api = getAgentApi()
    dockerfileContent.value = await api.renderTemplateContent(
      props.projectId,
      selectedDockerfileTemplateId.value
    )
  } catch (e) {
    console.error('loadDockerfileRenderedContent error:', e)
    dockerfileContent.value = ''
    Notify.create({
      type: 'negative',
      message: '加载 Dockerfile 渲染结果失败',
      position: 'top',
    })
  }
}

async function loadDockercommandRenderedContent() {
  if (!props.projectId || !selectedDockercommandTemplateId.value) return

  try {
    const api = getAgentApi()
    dockerCommand.value = await api.renderTemplateContent(
      props.projectId,
      selectedDockercommandTemplateId.value
    )
  } catch (e) {
    console.error('loadDockercommandRenderedContent error:', e)
    dockerCommand.value = ''
    Notify.create({
      type: 'negative',
      message: '加载 Docker Command 渲染结果失败',
      position: 'top',
    })
  }
}

async function handleDockerfileTemplateChange() {
  await loadDockerfileRenderedContent()
}

async function handleDockercommandTemplateChange() {
  await loadDockercommandRenderedContent()
}

function openCreateDockerfileTemplateDialog() {
  newDockerfileTemplate.value = {
    template_name: '',
    description: '',
    content: dockerfileContent.value || '',
  }
  createDockerfileTemplateDialogVisible.value = true
}

function openCreateDockercommandTemplateDialog() {
  newDockercommandTemplate.value = {
    template_name: '',
    description: '',
    content: dockerCommand.value || '',
  }
  createDockercommandTemplateDialogVisible.value = true
}

async function confirmCreateDockerfileTemplate() {
  const templateName = newDockerfileTemplate.value.template_name.trim()
  const content = newDockerfileTemplate.value.content.trim()

  if (!templateName || !content) {
    Notify.create({
      type: 'negative',
      message: '请填写模板名称和模板内容',
      position: 'top',
    })
    return
  }

  creatingDockerfileTemplate.value = true
  try {
    const api = getAgentApi()
    const created = await api.createTemplate({
      template_name: templateName,
      template_type: 'dockerfile',
      project_type: 'java',
      description: newDockerfileTemplate.value.description?.trim() || '',
      content,
    })

    createDockerfileTemplateDialogVisible.value = false
    await loadDockerfileTemplates()
    selectedDockerfileTemplateId.value = created.id
    await loadDockerfileRenderedContent()

    Notify.create({
      type: 'positive',
      message: 'Dockerfile 模板创建成功',
      position: 'top',
    })
  } catch (e) {
    console.error('confirmCreateDockerfileTemplate error:', e)
    Notify.create({
      type: 'negative',
      message: 'Dockerfile 模板创建失败',
      position: 'top',
    })
  } finally {
    creatingDockerfileTemplate.value = false
  }
}

async function confirmCreateDockercommandTemplate() {
  const templateName = newDockercommandTemplate.value.template_name.trim()
  const content = newDockercommandTemplate.value.content.trim()

  if (!templateName || !content) {
    Notify.create({
      type: 'negative',
      message: '请填写模板名称和模板内容',
      position: 'top',
    })
    return
  }

  creatingDockercommandTemplate.value = true
  try {
    const api = getAgentApi()
    const created = await api.createTemplate({
      template_name: templateName,
      template_type: 'dockercommand',
      project_type: 'java',
      description: newDockercommandTemplate.value.description?.trim() || '',
      content,
    })

    createDockercommandTemplateDialogVisible.value = false
    await loadDockercommandTemplates()
    selectedDockercommandTemplateId.value = created.id
    await loadDockercommandRenderedContent()

    Notify.create({
      type: 'positive',
      message: 'Docker Command 模板创建成功',
      position: 'top',
    })
  } catch (e) {
    console.error('confirmCreateDockercommandTemplate error:', e)
    Notify.create({
      type: 'negative',
      message: 'Docker Command 模板创建失败',
      position: 'top',
    })
  } finally {
    creatingDockercommandTemplate.value = false
  }
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

function handleFileChange(file: any) {
  fileList.value = [file]
}

function handleAbortDeploy() {
  appendLog('用户中止部署', 'warning')
  isDeploying.value = false

  Notify.create({
    type: 'warning',
    message: '已中止部署',
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

  await handleImmediateUploadDeploy()
}

async function handleImmediateUploadDeploy() {
  const file = fileList.value[0]?.raw
  if (!file) {
    Notify.create({
      type: 'negative',
      message: '请选择文件',
      position: 'top',
    })
    return
  }

  isDeploying.value = true
  uploadProgress.value = 0
  logLines.value = []
  appendLog(`开始部署：${file.name}`)

  try {
    appendLog('上传 Jar 中...')

    const fd = new FormData()
    fd.append('id', String(props.projectId))
    fd.append('file', file)
    fd.append('dockerfile_content', dockerfileContent.value)
    fd.append('dockercommand_content', dockerCommand.value)

    await getAgentApi().deployJavaProject(fd, {
      onUploadProgress: (e: AxiosProgressEvent) => {
        if (e.total) {
          uploadProgress.value = Math.round((e.loaded / e.total) * 100)
        }
      },
    })

    appendLog('上传完成', 'success')
    appendLog('开始执行部署', 'info')
    appendLog('部署成功', 'success')

    uploadProgress.value = 100

    Notify.create({
      type: 'positive',
      message: '部署成功',
      position: 'top',
    })

    emit('deploy-success')
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
  const text = logLines.value.map((i) => `[${i.time}] ${i.text}`).join('\n')
  if (!text.trim()) return

  try {
    await copyToClipboard(text)
    Notify.create({
      type: 'positive',
      message: '日志已复制',
      position: 'top',
    })
  } catch {
    Notify.create({
      type: 'negative',
      message: '复制失败',
      position: 'top',
    })
  }
}

onMounted(async () => {
  await Promise.all([
    loadDockerfileTemplates(),
    loadDockercommandTemplates(),
  ])
})
</script>

<style scoped>
.deploy-grid {
  display: grid;
  grid-template-rows: auto minmax(320px, 1fr);
  gap: 16px;
  min-height: 760px;
}

.panel-card {
  border-radius: 20px;
  background: rgba(250, 250, 250, 0.76);
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
.editor-stack {
  margin-top: 18px;
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

.aligned-editor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  align-items: stretch;
  margin-top: 18px;
}

.editor-column {
  display: grid;
  grid-template-rows: auto auto 1fr;
  min-width: 0;
}

.editor-column-header {
  min-height: 34px;
  display: flex;
  align-items: center;
}

.editor-column-body {
  min-width: 0;
  margin-top: 6px;
}

.template-header {
  width: 100%;
}

.template-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.template-select {
  flex: 1;
  min-width: 0;
}

.dialog-editor-wrap {
  width: 100%;
  min-width: 0;
  flex: 1;
}

.editor-rendered-tip {
  margin-top: 12px;
  margin-bottom: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(37, 99, 235, 0.05);
  border: 1px solid rgba(37, 99, 235, 0.08);
  color: #64748b;
  font-size: 12px;
  line-height: 1.6;
}

.text-action-btn {
  border: none;
  background: transparent;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  padding: 0;
}

.text-action-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
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

.terminal-line+.terminal-line {
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
  background: #2563eb;
  color: #fff;
}

.ui-btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
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

.upload-tip {
  text-align: right;
  color: #909399;
}

:deep(.el-tag) {
  border-radius: 999px;
  font-weight: 700;
  border: none;
}

@media (max-width: 980px) {
  .deploy-grid {
    grid-template-rows: auto auto;
    min-height: unset;
  }

  .control-grid,
  .aligned-editor-grid,
  .detail-form-grid {
    grid-template-columns: 1fr;
  }

  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .template-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>