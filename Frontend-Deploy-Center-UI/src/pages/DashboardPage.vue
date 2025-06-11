<template>
  <q-page class="q-pa-md">
    <div class="dashboard-cards-container">
      <AgentDashboardCard :key="currentAgent.id" :agentId="currentAgent.id" />
    </div>
  </q-page>
</template>

<script setup>
import { storeToRefs } from 'pinia';
import AgentDashboardCard from 'src/components/AgentDashboardCard.vue';
import { useAgentStore } from 'src/stores/useAgentStore';

const agentStore = useAgentStore();
const { currentAgent } = storeToRefs(agentStore);

</script>

<style scoped>
.dashboard-cards-container {
  display: flex;
  flex-wrap: wrap;
  /* 允许换行 */
  gap: 16px;
  /* 控制卡片之间的间距 */
  justify-content: center;
  /* 使卡片整体居中 */
  padding: 0 16px;
  /* 为容器添加内边距，使卡片距离页面边缘有间距 */
}
</style>
