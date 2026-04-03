<template>
  <q-dialog v-model="dialogVisible">
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
          <el-table-column prop="key" label="字段" width="180" />
          <el-table-column prop="label" label="说明" width="140" />
          <el-table-column label="值" min-width="240">
            <template #default="scope">
              <div v-if="!isEditing || !scope.row.editable" class="table-cell-value">
                {{ scope.row.value || '-' }}
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
          unelevated
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
          <strong>{{ pythonProject.project_name || '-' }}</strong>
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
import { computed, ref, watch } from 'vue'
import { Notify } from 'quasar'
import { formatDate } from 'src/utils/dateFormatter'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'
import type { PythonProject } from 'src/types/Project.types'
import type { UpdatePythonProjectRequestDto } from 'src/types/dto/UpdatePythonProjectRequestDto'

type DetailRow = {
  label: string
  value: string
  key: string
  editable: boolean
}

const props = defineProps<{
  modelValue: boolean
  project: any
}>()

const pythonProject = props.project as PythonProject

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved'): void
  (e: 'deleted'): void
}>()

const agentProxyApi = provideCurrentAgentProxyApi()

const isSecondConfirmDeleteDialogOpen = ref(false)
const isEditing = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)

const confirmText = ref('')
const tableData = ref<DetailRow[]>([])
const originalTableDataSnapshot = ref<DetailRow[]>([])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

const formatDateSafe = (value: any): string => {
  if (!value) return '-'
  try {
    return formatDate(value)
  } catch {
    return String(value)
  }
}

const buildDetailTableData = (): DetailRow[] => {
  return [
    { label: '项目ID', key: 'id', value: String(pythonProject.id ?? ''), editable: false },
    { label: '项目代号', key: 'project_code', value: String(pythonProject.project_code ?? ''), editable: true },
    { label: '项目名称', key: 'project_name', value: String(pythonProject.project_name ?? ''), editable: true },
    { label: '项目分组', key: 'project_group', value: String(pythonProject.project_group ?? ''), editable: true },
    { label: '项目类型', key: 'project_type', value: String(pythonProject.project_type ?? ''), editable: false },
    { label: '镜像名称', key: 'docker_image_name', value: String(pythonProject.docker_image_name ?? ''), editable: true },
    { label: '镜像标签', key: 'docker_image_tag', value: String(pythonProject.docker_image_tag ?? ''), editable: true },
    { label: '容器名称', key: 'container_name', value: String(pythonProject.container_name ?? ''), editable: true },
    { label: '外部端口', key: 'external_port', value: String(pythonProject.external_port ?? ''), editable: true },
    { label: '内部端口', key: 'internal_port', value: String(pythonProject.internal_port ?? ''), editable: true },
    { label: 'Docker网络', key: 'network', value: String(pythonProject.network ?? ''), editable: false },
    { label: 'Python版本', key: 'python_version', value: String(pythonProject.python_version ?? ''), editable: false },
    { label: '宿主机路径', key: 'host_project_path', value: String(pythonProject.host_project_path ?? ''), editable: true },
    { label: '容器内路径', key: 'container_project_path', value: String(pythonProject.container_project_path ?? ''), editable: true },
    { label: '访问地址', key: 'access_url', value: String(pythonProject.access_url ?? ''), editable: true },
    { label: 'Git地址', key: 'git_repository', value: String(pythonProject.git_repository ?? ''), editable: true },
    { label: '创建时间', key: 'created_at', value: formatDateSafe(pythonProject.created_at), editable: false },
    { label: '更新时间', key: 'updated_at', value: formatDateSafe(pythonProject.updated_at), editable: false },
    { label: '最近部署', key: 'last_deployed_at', value: formatDateSafe(pythonProject.last_deployed_at), editable: false },
  ]
}

const resetTableData = () => {
  const rows = buildDetailTableData()
  tableData.value = rows
  originalTableDataSnapshot.value = JSON.parse(JSON.stringify(rows))
  isEditing.value = false
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
    const updateData: Partial<UpdatePythonProjectRequestDto> = {
      id: pythonProject.id,
    }

    const skipKeys = ['created_at', 'updated_at', 'last_deployed_at', 'project_type']
    const numberFields = ['external_port', 'internal_port']

    tableData.value.forEach((item) => {
      if (skipKeys.includes(item.key)) return

      const rawValue = item.value ?? ''

      if (numberFields.includes(item.key)) {
        updateData[item.key as keyof UpdatePythonProjectRequestDto] =
          rawValue === '' ? undefined as any : Number(rawValue) as any
      } else {
        updateData[item.key as keyof UpdatePythonProjectRequestDto] = rawValue as any
      }
    })

    await agentProxyApi.updatePythonProject(updateData as UpdatePythonProjectRequestDto)

    Notify.create({
      type: 'positive',
      message: '保存成功',
      position: 'top',
    })

    isEditing.value = false
    dialogVisible.value = false
    emit('saved')
  } catch (error: any) {
    Notify.create({
      type: 'negative',
      message: `保存失败${error?.message ? '：' + error.message : ''}`,
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
    await agentProxyApi.deletePythonProject(pythonProject.id)

    Notify.create({
      message: '删除成功',
      type: 'positive',
      position: 'top',
    })

    isSecondConfirmDeleteDialogOpen.value = false
    dialogVisible.value = false
    confirmText.value = ''
    emit('deleted')
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

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      resetTableData()
    }
  },
  { immediate: true }
)

watch(
  () => pythonProject,
  () => {
    if (props.modelValue) {
      resetTableData()
    }
  },
  { deep: true }
)

watch(isSecondConfirmDeleteDialogOpen, (val) => {
  if (!val) {
    confirmText.value = ''
  }
})
</script>

<style scoped>
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
</style>