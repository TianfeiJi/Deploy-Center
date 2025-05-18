<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6 text-bold">部署历史</div>
      </q-card-section>
      <q-separator />
      <q-card-section>
        <el-timeline>
          <el-timeline-item
            v-for="history in deployHistorys"
            :key="history.id"
            :timestampString="formatDate(history.created_at)"
            :color="history.status === 'success' ? 'green' : 'red'"
          >
            <div><strong>项目名称：</strong>{{ history.project_name }}</div>
            <div>
              <strong>状态：</strong
              >{{ history.status === 'success' ? '成功' : '失败' }}
            </div>
            <div>
              <strong>时间：</strong>{{ formatDate(history.created_at) }}（{{ timeAgo(history.created_at) }}前）
            </div>
          </el-timeline-item>
        </el-timeline>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { DeployHistoryVo } from 'src/types/vo/DeployHistoryVo';
import { AgentCommandApi } from 'src/api/AgentCommandApi';
import { formatDate } from 'src/utils/dateFormatter';
import { storeToRefs } from 'pinia';
import { useAgentStore } from 'src/stores/useAgentStore';

const agentStore = useAgentStore();

const { currentAgent } = storeToRefs(agentStore);

const agentCommandApi = ref<AgentCommandApi | null>(null);

const deployHistorys = ref<DeployHistoryVo[]>([]);

onMounted(async () => {
  agentCommandApi.value = new AgentCommandApi(currentAgent.value!.id)
  deployHistorys.value = await agentCommandApi.value.fetchDeployHistoryList();
});

// 监听 currentAgent 变化
watch(
  currentAgent,
  async (agent) => {
    if (agent?.id) {
      agentCommandApi.value = new AgentCommandApi(agent.id);
      console.log(`Agent 切换到: ${agent.name} (${agent.ip})`);
      deployHistorys.value = await agentCommandApi.value.fetchDeployHistoryList();
    } else {
      deployHistorys.value = []
      agentCommandApi.value = null;
    }
  },
);

// 计算属性：返回“xxx前”格式的时间差
const timeAgo = (timestampString: string) => {
  const now = new Date();
  const past = new Date(timestampString);
  const diff = now.getTime() - past.getTime();

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  if (days > 0) {
    return `${days}天`;
  }

  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  if (hours > 0) {
    return `${hours}小时`;
  }

  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  if (minutes > 0) {
    return `${minutes}分钟`;
  }

  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  return `${seconds}秒`;
};
</script>

<style scoped>
</style>