import { defineStore } from 'pinia';
import { Agent } from 'src/types/Agent';
import {
  getAgentList,
  getAgent,
} from 'src/api/agentApi';
import { AgentProxyApi } from 'src/api/agentProxyApi';
import { provideAgentProxyApi } from 'src/factory/agentProxyApiFactory';
import type { AgentRuntimeInfo } from 'src/types/AgentRuntimeInfo';

export const useAgentStore = defineStore('agentStore', {
  state: () => ({
    agentList: [] as Agent[], // Agent 列表
    currentAgent: null as Agent | null, // 当前选中的 Agent
    agentRuntimeInfoMap: {} as Record<number, AgentRuntimeInfo>, // id -> Agent 运行时信息 映射
  }),
  actions: {
    // 获取agentList
    async getAllAgentList() {
      if (this.agentList.length > 0) {
        return;
      }

      try {
          const response = await getAgentList();
          if (response.code === 200 && response.data) {
            this.agentList = response.data;
            console.log(this.agentList)
          } else {
            console.error('Failed to init agent list:', response.msg);
          }
      } catch (error) {
          console.error('Error initializing agent store:', error);
      }
    },
    // 获取单个 Agent 详情
    async getAgent(agentId: number) {
      try {
        const response = await getAgent(agentId);
        if (response.code === 200 && response.data) {
          this.currentAgent = response.data;
        } else {
          console.error('Failed to fetch agent details:', response.msg);
        }
      } catch (error) {
        console.error('Error fetching agent details:', error);
      }
    },
    // 设置当前选中的 Agent
    async setCurrentAgentById(agentId: number) {
      try {
        const response = await getAgent(agentId);
        if (response.code === 200 && response.data) {
          this.currentAgent = response.data;
        } else {
          console.error('Failed to set current agent:', response.msg);
        }
      } catch (error) {
        console.error('Error setting current agent:', error);
      }
    },
    // 获取当前 agent 的运行时状态（优先读缓存）
    async getAgentRuntimeInfo(agentId: number): Promise<AgentRuntimeInfo> {
      if (this.agentRuntimeInfoMap[agentId]) {
        return this.agentRuntimeInfoMap[agentId];
      }

      try {
        const agentProxyApi: AgentProxyApi = provideAgentProxyApi(agentId);
        const info = await agentProxyApi.fetchInspectInfo();
        const result: AgentRuntimeInfo = {
          health: info.status,
          agent_version: info.agent_version,
        };
        this.agentRuntimeInfoMap[agentId] = result;
        return result;
      } catch (e) {
        const fallback: AgentRuntimeInfo = {
          health: '未知',
          agent_version: '未知',
        };
        this.agentRuntimeInfoMap[agentId] = fallback;
        return fallback;
      }
    },
    // 获取所有 agent 的运行时信息
    async getAllAgentRuntimeInfo() {
      if (Object.keys(this.agentRuntimeInfoMap).length === this.agentList.length) {
        return; // 缓存已存在，直接return;
      }

      for (const agent of this.agentList) {
        await this.getAgentRuntimeInfo(agent.id);
      }
    },
    // 清空 agent 数据
    clearAgents() {
      this.agentList = [];
      this.currentAgent = null;
      this.agentRuntimeInfoMap = {};
    },
  },

  getters: {
    // 获取 Agent 列表
    getAgentList: (state) => state.agentList,

    // 获取当前选中的 Agent
    getCurrentAgent: (state) => state.currentAgent,

    // 获取指定 agent 的运行时信息
    getAgentRuntimeInfoById: (state) => (id: number) => state.agentRuntimeInfoMap[id],
  },
});
