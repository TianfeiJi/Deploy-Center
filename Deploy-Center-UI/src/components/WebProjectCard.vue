<template>
  <q-card class="web-project-card">
    <q-card-section class="card-header">
      <div class="project-header">
        <div class="project-header-left">
          <div class="project-title" :title="webProject.project_name || '-'">
            {{ webProject.project_name || '-' }}
          </div>

          <div class="project-submeta">
            <span class="project-submeta-type">Web</span>
            <span v-if="webProject.project_group" class="project-submeta-divider">·</span>
            <span v-if="webProject.project_group" class="project-submeta-group">
              {{ webProject.project_group }}
            </span>
          </div>
        </div>

        <div class="project-header-right">
          <div class="runtime-status-inline">
            <template v-if="isCheckingStatus">
              <q-spinner color="grey-5" size="16px" />
            </template>
            <template v-else>
              <el-tag :type="deploymentStatusMeta.tagType" effect="light" round>
                {{ deploymentStatusMeta.label }}
              </el-tag>
            </template>
          </div>

          <div class="project-deploy-text">
            最近部署：{{ getDeployText(webProject.last_deployed_at) }}
          </div>
        </div>
      </div>

      <div class="info-list q-mt-sm">
        <div class="info-row">
          <div class="info-key">访问地址</div>

          <div
            v-if="webProject.access_url"
            class="info-value access-url-link two-line-fixed"
            :title="webProject.access_url"
            @click.stop="openAccessUrl(webProject.access_url)"
          >
            {{ webProject.access_url }}
          </div>

          <div v-else class="info-value access-empty two-line-fixed">
            未配置
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">宿主机路径</div>

          <div
            class="info-value hover-copy multi-line-value"
            :title="webProject.host_project_path || '-'"
            @click.stop="copyValue(webProject.host_project_path)"
          >
            {{ webProject.host_project_path || '-' }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">容器内路径</div>

          <div
            class="info-value hover-copy multi-line-value"
            :title="webProject.container_project_path || '-'"
            @click.stop="copyValue(webProject.container_project_path)"
          >
            {{ webProject.container_project_path || '-' }}
          </div>
        </div>
      </div>
    </q-card-section>

    <q-card-actions class="card-actions split-actions">
      <div class="actions-left">
        <q-btn flat color="primary" label="详情" @click="viewWebProjectDetail" />
      </div>

      <div class="actions-right">
        <q-btn
          flat
          dense
          color="positive"
          label="部署"
          @click="goToDeployConsole(webProject.id)"
        />
      </div>
    </q-card-actions>
  </q-card>

  <q-dialog v-model="isViewDetailDialogOpen">
    <q-card class="detail-dialog-card">
      <q-card-section class="row items-center">
        <div class="text-h6">项目详情</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-separator />

      <q-card-section class="detail-table-section">
        <el-table
          :data="tableData"
          border
          stripe
          style="width: 100%"
          max-height="60vh"
        >
          <el-table-column prop="key" label="字段" width="170" />
          <el-table-column prop="label" label="注释" width="130" />
          <el-table-column label="值">
            <template #default="scope">
              <div v-if="!isEditing || !scope.row.editable" class="table-cell-value">
                {{ scope.row.value }}
              </div>
              <el-input
                v-else
                v-model="scope.row.value"
                placeholder="请输入内容"
                clearable
              />
            </template>
          </el-table-column>
        </el-table>
      </q-card-section>

      <q-separator />

      <q-card-actions class="q-px-md q-py-sm">
        <q-btn
          flat
          color="negative"
          label="删除"
          @click="isSecondConfirmDeleteDialogOpen = true"
        />

        <q-space />

        <q-btn
          v-if="isEditing"
          flat
          color="grey-7"
          label="取消"
          :disable="isSaving"
          @click="cancelEdit"
        />

        <q-btn
          v-if="isEditing"
          flat
          color="positive"
          label="保存"
          :loading="isSaving"
          @click="saveEdit"
        />

        <q-btn
          v-else
          flat
          color="secondary"
          label="编辑"
          @click="startEdit"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog v-model="isSecondConfirmDeleteDialogOpen" persistent>
    <q-card class="delete-dialog-card">
      <q-card-section class="text-h6 text-negative">
        危险操作
      </q-card-section>

      <q-card-section>
        <div class="delete-warning-text">
          你正在删除项目：
          <strong>{{ webProject.project_name || '-' }}</strong>
        </div>

        <div class="delete-warning-subtext q-mt-sm">
          请输入“确定删除”以继续操作。
        </div>

        <q-input
          v-model="confirmText"
          outlined
          class="q-mt-md"
          placeholder="请输入：确定删除"
          :disable="isDeleting"
        />
      </q-card-section>

      <q-card-actions align="right" class="q-px-md q-pb-md">
        <q-btn
          flat
          label="取消"
          :disable="isDeleting"
          v-close-popup
        />
        <q-btn
          unelevated
          color="negative"
          label="确定删除"
          icon="delete_forever"
          :loading="isDeleting"
          @click="handleSecondConfirmDelete"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { Notify, copyToClipboard } from 'quasar'
import { formatDate } from 'src/utils/dateFormatter'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'
import { WebProject } from 'src/types/Project.types'
import { UpdateWebProjectRequestDto } from 'src/types/dto/UpdateWebProjectRequestDto'
import { useRouter } from 'vue-router'

type DetailRow = {
  label: string
  value: string
  key: string
  editable: boolean
}

const router = useRouter()

const props = defineProps<{
  webProject: WebProject
}>()

const agentProxyApi = provideCurrentAgentProxyApi()

const isCheckingStatus = ref(true)
const isViewDetailDialogOpen = ref(false)
const isSecondConfirmDeleteDialogOpen = ref(false)

const isEditing = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)

const confirmText = ref('')
const tableData = ref<DetailRow[]>([])
const originalTableDataSnapshot = ref<DetailRow[]>([])

const goToDeployConsole = (id?: string | number) => {
  if (!id) return
  router.push({
    path: `/project/deploy/${id}`,
  })
}

const formatDateSafe = (value: any) => {
  if (!value) return '-'
  try {
    return formatDate(value)
  } catch {
    return String(value)
  }
}

const getDeployText = (time?: any) => {
  if (!time) return '未部署'

  try {
    const now = Date.now()
    const t = new Date(time).getTime()
    if (Number.isNaN(t)) return '未部署'

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

const viewWebProjectDetail = () => {
  const rows: DetailRow[] = [
    { label: '项目Id', key: 'id', value: String(props.webProject.id ?? ''), editable: false },
    {
      label: '项目代号',
      key: 'project_code',
      value: String(props.webProject.project_code ?? ''),
      editable: true,
    },
    {
      label: '项目名称',
      key: 'project_name',
      value: String(props.webProject.project_name ?? ''),
      editable: true,
    },
    {
      label: '项目分组',
      key: 'project_group',
      value: String(props.webProject.project_group ?? ''),
      editable: true,
    },
    {
      label: '宿主机路径',
      key: 'host_project_path',
      value: String(props.webProject.host_project_path ?? ''),
      editable: true,
    },
    {
      label: '容器内路径',
      key: 'container_project_path',
      value: String(props.webProject.container_project_path ?? ''),
      editable: true,
    },
    {
      label: 'Git地址',
      key: 'git_repository',
      value: String(props.webProject.git_repository ?? ''),
      editable: true,
    },
    {
      label: '访问地址',
      key: 'access_url',
      value: String(props.webProject.access_url ?? ''),
      editable: true,
    },
    {
      label: '创建时间',
      key: 'created_at',
      value: formatDateSafe(props.webProject.created_at),
      editable: false,
    },
    {
      label: '更新时间',
      key: 'updated_at',
      value: formatDateSafe(props.webProject.updated_at),
      editable: false,
    },
    {
      label: '最近部署时间',
      key: 'last_deployed_at',
      value: formatDateSafe(props.webProject.last_deployed_at),
      editable: false,
    },
  ]

  tableData.value = rows
  originalTableDataSnapshot.value = JSON.parse(JSON.stringify(rows))
  isEditing.value = false
  isViewDetailDialogOpen.value = true
}

const startEdit = () => {
  originalTableDataSnapshot.value = JSON.parse(JSON.stringify(tableData.value))
  isEditing.value = true
}

const cancelEdit = () => {
  tableData.value = JSON.parse(JSON.stringify(originalTableDataSnapshot.value))
  isEditing.value = false
}

const saveEdit = async () => {
  isSaving.value = true

  try {
    const updateData: Partial<UpdateWebProjectRequestDto> = {
      id: props.webProject.id,
    }

    const skipKeys = ['created_at', 'updated_at', 'last_deployed_at']

    tableData.value.forEach((item) => {
      if (skipKeys.includes(item.key)) return
      updateData[item.key as keyof UpdateWebProjectRequestDto] = item.value as any
    })

    await agentProxyApi.updateWebProject(updateData as UpdateWebProjectRequestDto)

    Notify.create({
      type: 'positive',
      message: '保存成功',
      position: 'top',
    })

    isEditing.value = false
    isViewDetailDialogOpen.value = false
  } catch {
    Notify.create({
      type: 'negative',
      message: '保存失败',
      position: 'top',
    })
  } finally {
    isSaving.value = false
  }
}

const handleSecondConfirmDelete = async () => {
  if (confirmText.value !== '确定删除') {
    Notify.create({
      message: '请输入“确定删除”',
      type: 'negative',
      position: 'top',
    })
    return
  }

  isDeleting.value = true

  try {
    await agentProxyApi.deleteWebProject(props.webProject.id)

    Notify.create({
      message: '删除成功',
      type: 'positive',
      position: 'top',
    })

    isSecondConfirmDeleteDialogOpen.value = false
    isViewDetailDialogOpen.value = false
    confirmText.value = ''
  } catch (error: any) {
    Notify.create({
      message: `删除失败${error?.message ? ': ' + error.message : ''}`,
      type: 'negative',
      position: 'top',
    })
  } finally {
    isDeleting.value = false
  }
}

const deploymentStatus = ref<'Deployed' | 'Awaiting Deployment' | 'Checking' | 'Unknown'>(
  'Checking'
)

const deploymentStatusMeta = computed(() => {
  if (deploymentStatus.value === 'Deployed') {
    return { label: 'Deployed', tagType: 'success' }
  }
  if (deploymentStatus.value === 'Awaiting Deployment') {
    return { label: 'Awaiting Deployment', tagType: 'info' }
  }
  if (deploymentStatus.value === 'Unknown') {
    return { label: 'Status Unknown', tagType: 'warning' }
  }
  return { label: deploymentStatus.value, tagType: 'info' }
})

const fetchDeploymentStatus = async () => {
  try {
    const response = await agentProxyApi.checkWebProjectDeploymentStatus(props.webProject.id)
    deploymentStatus.value = response.deployment_status
  } catch {
    deploymentStatus.value = 'Unknown'
  } finally {
    isCheckingStatus.value = false
  }
}

watch(isSecondConfirmDeleteDialogOpen, (val) => {
  if (!val) {
    confirmText.value = ''
  }
})

onMounted(async () => {
  await fetchDeploymentStatus()
})
</script>

<style scoped>
.web-project-card {
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

.web-project-card:hover {
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

.info-value {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #334155;
  word-break: break-all;
}

.access-url-link {
  color: #2563eb;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.18s ease;
}

.access-url-link:hover {
  color: #1d4ed8;
}

.access-empty {
  color: #94a3b8;
}

.two-line-fixed {
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: calc(1.6em * 2);
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

.detail-dialog-card {
  width: 88vw;
  max-width: 1100px;
  border-radius: 18px;
}

.detail-table-section {
  padding-top: 16px;
  padding-bottom: 16px;
}

.table-cell-value {
  white-space: pre-wrap;
  word-break: break-word;
  color: #334155;
}

.delete-dialog-card {
  width: 420px;
  max-width: 92vw;
  border-radius: 18px;
}

.delete-warning-text {
  color: #1f2937;
  line-height: 1.7;
}

.delete-warning-subtext {
  color: #dc2626;
  font-size: 14px;
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