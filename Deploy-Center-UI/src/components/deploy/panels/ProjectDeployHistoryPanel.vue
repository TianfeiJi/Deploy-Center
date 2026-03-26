<template>
  <div class="single-panel">
    <section class="panel-card">
      <div class="panel-header">
        <div class="panel-title">部署历史</div>
      </div>

      <div class="table-wrap">
        <el-table
          v-loading="loading"
          :data="records"
          border
          stripe
          style="width: 100%"
          empty-text="暂无部署历史"
        >
          <el-table-column prop="project_code" label="项目代号" min-width="140" />
          <el-table-column prop="project_name" label="项目名称" min-width="180" />
          <el-table-column prop="operator_name" label="操作人" width="120" />

          <el-table-column label="状态" width="120">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)" effect="light" round>
                {{ formatStatus(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="失败原因" min-width="240">
            <template #default="scope">
              <span class="failed-reason">
                {{ scope.row.failed_reason || '-' }}
              </span>
            </template>
          </el-table-column>

          <el-table-column label="部署时间" width="180">
            <template #default="scope">
              {{ formatDateSafe(scope.row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Notify } from 'quasar'
import { formatDate } from 'src/utils/dateFormatter'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'
import { DeployHistoryVo } from 'src/types/vo/DeployHistoryVo'

const props = defineProps<{
  projectId: string | number
}>()

const loading = ref(false)
const records = ref<DeployHistoryVo[]>([])

function getStatusTagType(status: string) {
  const value = String(status || '').toLowerCase()

  if (value === '成功' || value === 'success') return 'success'
  if (value === '失败' || value === 'failed') return 'danger'
  if (value === '运行中' || value === 'running') return 'warning'
  return 'info'
}

function formatStatus(status: string) {
  const value = String(status || '').toLowerCase()

  if (value === 'success') return '成功'
  if (value === 'failed') return '失败'
  if (value === 'running') return '运行中'
  return status || '-'
}

function formatDateSafe(value?: string) {
  if (!value) return '-'
  try {
    return formatDate(value)
  } catch {
    return value
  }
}

async function loadDeployRecords() {
  const currentProjectId = String(props.projectId || '').trim()

  if (!currentProjectId) {
    records.value = []
    return
  }

  loading.value = true
  try {
    const historyList = await provideCurrentAgentProxyApi().fetchDeployHistoryList()

    records.value = (historyList || [])
      .filter((item: DeployHistoryVo) => String(item.project_id || '') === currentProjectId)
      .sort((a: DeployHistoryVo, b: DeployHistoryVo) => {
        const timeA = new Date(a.created_at || 0).getTime()
        const timeB = new Date(b.created_at || 0).getTime()
        return timeB - timeA
      })
  } catch (error) {
    console.error('加载部署历史失败:', error)
    records.value = []
    Notify.create({
      type: 'negative',
      message: '加载部署历史失败',
      position: 'top',
    })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadDeployRecords()
})

watch(
  () => props.projectId,
  async () => {
    await loadDeployRecords()
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
}

.panel-title {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
}

.table-wrap {
  padding: 16px 20px;
}

.failed-reason {
  color: #475569;
  word-break: break-word;
}

:deep(.el-tag) {
  border-radius: 999px;
  font-weight: 700;
  border: none;
}
</style>