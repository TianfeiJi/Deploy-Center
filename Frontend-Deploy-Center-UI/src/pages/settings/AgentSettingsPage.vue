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

        <!-- 动态获取 版本、状态  -->
        <el-table-column label="状态" min-width="90">
          <template #default="{ row }">
            <template v-if="agentRuntimeInfoMap[row.id]">
              <el-tag
                :type="agentRuntimeInfoMap[row.id].health === 'healthy' ? 'success' : 'danger'"
                effect="light"
                style="font-style: italic"
              >
                {{ agentRuntimeInfoMap[row.id].health === 'healthy' ? '正常' : '异常' }}
              </el-tag>
            </template>
            <template v-else>
              <el-icon><Loading /></el-icon>
            </template>
          </template>
        </el-table-column>

        <el-table-column label="版本" min-width="90">
          <template #default="{ row }">
            <template v-if="agentRuntimeInfoMap[row.id]">
              <span style="font-style: italic">{{ agentRuntimeInfoMap[row.id].agent_version }}</span>
            </template>
            <template v-else>
              <el-icon><Loading /></el-icon>
            </template>
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
import { AgentCommandApi } from 'src/api/AgentCommandApi';
import type { Agent } from 'src/types/Agent'
import type { AgentRuntimeInfo } from 'src/types/AgentRuntimeInfo'

const agentList = ref<Agent[]>([])
const agentRuntimeInfoMap = ref<Record<number, AgentRuntimeInfo>>({})

const fetchAgents = async () => {
  const response = await getAgentList();
  agentList.value = response.data

  // 加载每个 Agent 的运行状态和版本信息
  for (const agent of response.data) {
    const api = new AgentCommandApi(agent.id)
    try {
      const info = await api.fetchInspectInfo();

      agentRuntimeInfoMap.value[agent.id] = {
        health: info.status,
        agent_version: info.agent_version,
        // productName: info.product_name,
        // sysVendor: info.sys_vendor
      };

    } catch (e) {
      agentRuntimeInfoMap.value[agent.id] = {
        health: 'error',
        agent_version: '未知'
      }
    }
  }
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
