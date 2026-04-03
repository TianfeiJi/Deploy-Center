<template>
  <q-dialog v-model="visible">
    <q-card class="detail-dialog-card">
      <q-card-section class="row items-center">
        <div class="text-h6">项目详情</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-separator />

      <q-card-section class="detail-table-section">
        <el-table :data="tableData" border stripe max-height="60vh">
          <el-table-column prop="key" label="字段" width="170" />
          <el-table-column prop="label" label="说明" width="130" />
          <el-table-column label="值">
            <template #default="scope">
              <div v-if="!isEditing || !scope.row.editable">
                {{ scope.row.value || '-' }}
              </div>
              <el-input
                v-else
                v-model="scope.row.value"
                clearable
              />
            </template>
          </el-table-column>
        </el-table>
      </q-card-section>

      <q-separator />

      <q-card-actions>
        <q-btn flat color="negative" label="删除" @click="isDeleteDialogOpen = true" />
        <q-space />

        <q-btn v-if="isEditing" flat label="取消" @click="cancelEdit" />
        <q-btn v-if="isEditing" color="positive" label="保存" @click="saveEdit" />
        <q-btn v-else flat label="编辑" @click="startEdit" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <!-- 删除确认 -->
  <q-dialog v-model="isDeleteDialogOpen">
    <q-card>
      <q-card-section class="text-h6 text-negative">
        危险操作
      </q-card-section>

      <q-card-section>
        请输入“确定删除”
        <q-input v-model="confirmText" />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn label="取消" v-close-popup />
        <q-btn color="negative" label="确定" @click="handleDelete" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Notify } from 'quasar'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'
import { formatDate } from 'src/utils/dateFormatter'
import type { WebProject } from 'src/types/Project.types'
import type { UpdateWebProjectRequestDto } from 'src/types/dto/UpdateWebProjectRequestDto'

const props = defineProps<{
  modelValue: boolean
  project: any
}>()

const webProject = props.project as WebProject

const emit = defineEmits(['update:modelValue', 'saved', 'deleted'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const agentApi = provideCurrentAgentProxyApi()

const isEditing = ref(false)
const isDeleteDialogOpen = ref(false)
const confirmText = ref('')
const tableData = ref<any[]>([])
const snapshot = ref<any[]>([])

function buildTable() {
  return [
    { key: 'id', label: '项目ID', value: webProject.id, editable: false },
    { key: 'project_name', label: '项目名称', value: webProject.project_name, editable: true },
    { key: 'project_code', label: '项目代号', value: webProject.project_code, editable: true },
    { key: 'project_group', label: '分组', value: webProject.project_group, editable: true },
    { key: 'access_url', label: '访问地址', value: webProject.access_url, editable: true },
    { key: 'host_project_path', label: '宿主机路径', value: webProject.host_project_path, editable: true },
    { key: 'container_project_path', label: '容器路径', value: webProject.container_project_path, editable: true },
    { key: 'created_at', label: '创建时间', value: formatDate(webProject.created_at), editable: false },
  ]
}

watch(
  () => props.modelValue,
  (v) => {
    if (v) {
      tableData.value = buildTable()
      snapshot.value = JSON.parse(JSON.stringify(tableData.value))
      isEditing.value = false
    }
  }
)

function startEdit() {
  snapshot.value = JSON.parse(JSON.stringify(tableData.value))
  isEditing.value = true
}

function cancelEdit() {
  tableData.value = JSON.parse(JSON.stringify(snapshot.value))
  isEditing.value = false
}

async function saveEdit() {
  try {
    const data: any = { id: webProject.id }

    tableData.value.forEach((item) => {
      if (item.editable) {
        data[item.key] = item.value
      }
    })

    await agentApi.updateWebProject(data as UpdateWebProjectRequestDto)

    Notify.create({ type: 'positive', message: '保存成功' })
    emit('saved')
    visible.value = false
  } catch {
    Notify.create({ type: 'negative', message: '保存失败' })
  }
}

async function handleDelete() {
  if (confirmText.value !== '确定删除') return

  await agentApi.deleteWebProject(webProject.id)

  Notify.create({ type: 'positive', message: '删除成功' })
  emit('deleted')
  visible.value = false
}
</script>