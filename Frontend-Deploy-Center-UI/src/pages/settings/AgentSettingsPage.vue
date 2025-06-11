<template>
  <q-page class="q-pa-md flex flex-center" style="align-items: flex-start">
    <q-card class="q-pa-xl" style="width: 100%">
      <div class="row items-center justify-between q-mb-xl">
        <div class="title">Agent 管理</div>
        <el-button type="primary" @click="showAddDialog = true">新增 Agent</el-button>
      </div>

      <el-table
        :data="agentList"
        style="width: 100%"
        border
        stripe
        highlight-current-row
        row-key="id"
      >
        <el-table-column label="ID" prop="id" width="40" />
        <el-table-column label="名称" prop="name" min-width="120" />
        <el-table-column label="IP地址" prop="ip" min-width="150" />
        <el-table-column label="端口" prop="port" min-width="70" />
        <el-table-column label="服务地址" prop="service_url" min-width="220" show-overflow-tooltip />
        <el-table-column label="系统" prop="os" min-width="90" />
        <el-table-column label="类型" prop="type" min-width="70" />
        <el-table-column label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'info'" effect="light">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后更新" min-width="150" show-overflow-tooltip >
          <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="onEditAgent(row)">修改</el-button>
          </template>
        </el-table-column>
      </el-table>
    </q-card>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑 Agent" width="500px">
      <el-form :model="editAgent" label-width="100px">
        <el-form-item label="名称"><el-input v-model="editAgent.name" /></el-form-item>
        <el-form-item label="IP 地址"><el-input v-model="editAgent.ip" /></el-form-item>
        <el-form-item label="端口"><el-input v-model="editAgent.port" /></el-form-item>
        <el-form-item label="服务地址"><el-input v-model="editAgent.service_url" /></el-form-item>
        <el-form-item label="系统"><el-input v-model="editAgent.os" /></el-form-item>
        <el-form-item label="类型"><el-input v-model="editAgent.type" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editAgent.status" placeholder="选择状态">
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="onUpdateAgent">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新增弹窗 -->
    <el-dialog v-model="showAddDialog" title="新增 Agent" width="500px">
      <el-form :model="newAgent" label-width="100px">
        <el-form-item label="名称"><el-input v-model="newAgent.name" /></el-form-item>
        <el-form-item label="IP 地址"><el-input v-model="newAgent.ip" /></el-form-item>
        <el-form-item label="端口"><el-input v-model="newAgent.port" /></el-form-item>
        <el-form-item label="服务地址"><el-input v-model="newAgent.service_url" /></el-form-item>
        <el-form-item label="系统"><el-input v-model="newAgent.os" /></el-form-item>
        <el-form-item label="类型"><el-input v-model="newAgent.type" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="newAgent.status" placeholder="选择状态">
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="onAddAgent">确认</el-button>
      </template>
    </el-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Notify } from 'quasar'
import { getAgentList, updateAgent, createAgent } from 'src/api/agentApi'
import type { Agent } from 'src/types/Agent'

const agentList = ref<Agent[]>([])

const fetchAgents = async () => {
  const response = await getAgentList();
  agentList.value = response.data
}

const formatDate = (date: string) => {
  const d = new Date(date)
  return d.toLocaleString()
}

const showEditDialog = ref(false)
const editAgent = ref<Partial<Agent>>({})

const onEditAgent = (agent: Agent) => {
  editAgent.value = { ...agent }
  showEditDialog.value = true
}

const onUpdateAgent = async () => {
  try {
    await updateAgent(editAgent.value.id!, editAgent.value)
    Notify.create({ type: 'positive', message: '更新成功' })
    showEditDialog.value = false
    fetchAgents()
  } catch (e) {
    Notify.create({ type: 'negative', message: '更新失败' })
  }
}

const showAddDialog = ref(false)
const newAgent = ref<Partial<Agent>>({
  name: '',
  ip: '',
  port: 2333,
  service_url: '',
  os: '',
  type: 'ECS',
  status: 'online'
})

const onAddAgent = async () => {
  try {
    await createAgent(newAgent.value)
    Notify.create({ type: 'positive', message: '新增成功' })
    showAddDialog.value = false
    fetchAgents()
  } catch (e) {
    Notify.create({ type: 'negative', message: '新增失败' })
  }
}

onMounted(() => {
  fetchAgents()
})
</script>

<style scoped>
.title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #222;
}
</style>
