// src/factory/agentProxyApiFactory.ts
import { AgentProxyApi } from 'src/api/agentProxyApi';
import { useAgentStore } from 'src/stores/useAgentStore';
import { storeToRefs } from 'pinia';

// 对象池（按 agentId 缓存实例）
const agentProxyApiPool = new Map<number, AgentProxyApi>();

/**
 * 提供指定 agentId 的 AgentProxyApi 实例（带缓存）
 */
export function provideAgentProxyApi(agentId: number): AgentProxyApi {
  if (!agentProxyApiPool.has(agentId)) {
    agentProxyApiPool.set(agentId, new AgentProxyApi(agentId));
    console.log(`[AgentProxyApiFactory] 创建实例 for agentId = ${agentId}`);
  }
  return agentProxyApiPool.get(agentId)!;
}

/**
 * 提供当前选中 Agent 的 AgentProxyApi 实例
 */
export function provideCurrentAgentProxyApi(): AgentProxyApi {
  const { currentAgent } = storeToRefs(useAgentStore());
  if (!currentAgent.value?.id) {
    throw new Error('当前未选择 Agent');
  }
  return provideAgentProxyApi(currentAgent.value.id);
}

/**
 * 清空缓存池
 */
export function resetAgentProxyApiPool() {
  agentProxyApiPool.clear();
}