import { defineStore } from 'pinia';
import { Agent } from 'src/types/Agent';
import {
  getAgentList,
  getAgent,
  createAgent,
  updateAgent,
  deleteAgent,
} from 'src/api/agentApi';

export const useAgentStore = defineStore('agentStore', {
  state: () => ({
    agentList: [] as Agent[], // Agent 列表
    currentAgent: null as Agent | null, // 当前选中的 Agent
  }),
  actions: {
    // 初始化方法：拉列表 & 设置 currentAgent
    async initAgentStore() {
        try {
            const response = await getAgentList();
            if (response.code === 200 && response.data) {
              this.agentList = response.data;
              // 在初始化时设置 currentAgent 为第一个
              if (this.agentList.length > 0) {
                  this.currentAgent = this.agentList[0];
              }
              console.log(this.agentList)
            } else {
              console.error('Failed to init agent list:', response.msg);
            }
        } catch (error) {
            console.error('Error initializing agent store:', error);
        }
    },
          
    // 从 API 获取 Agent 列表
    async fetchAgentList() {
      try {
        const response = await getAgentList();
        if (response.code === 200 && response.data) {
          this.agentList = response.data;
        } else {
          console.error('Failed to fetch agent list:', response.msg);
        }
      } catch (error) {
        console.error('Error fetching agent list:', error);
      }
    },

    // 从 API 获取 Agent 详情
    async fetchAgent(agentId: number) {
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

    // 注册 Agent
    async createAgent(agentInfo: Agent) {
      try {
        const response = await createAgent(agentInfo);
        if (response.code === 200 && response.data) {
          this.agentList.push(response.data);
        } else {
          console.error('Failed to register agent:', response.msg);
        }
      } catch (error) {
        console.error('Error registering agent:', error);
      }
    },

    // 更新 Agent 信息
    async updateAgent(agentId: number, updatedData: Partial<Agent>) {
      try {
        const response = await updateAgent(agentId, updatedData);
        if (response.code === 200) {
          this.agentList = this.agentList.map((agent) =>
            agent.id === agentId ? { ...agent, ...updatedData } : agent
          );
        } else {
          console.error('Failed to update agent:', response.msg);
        }
      } catch (error) {
        console.error('Error updating agent:', error);
      }
    },

    // 删除 Agent
    async deleteAgent(agentId: number) {
      try {
        const response = await deleteAgent(agentId);
        if (response.code === 200) {
          this.agentList = this.agentList.filter(
            (agent) => agent.id !== agentId
          );
        } else {
          console.error('Failed to delete agent:', response.msg);
        }
      } catch (error) {
        console.error('Error deleting agent:', error);
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

    // 清空 Agent 列表
    clearAgents() {
      this.agentList = [];
      this.currentAgent = null;
    },
  },

  getters: {
    // 获取 Agent 列表
    getAgentList: (state) => state.agentList,

    // 获取当前选中的 Agent
    getCurrentAgent: (state) => state.currentAgent,
  },
});
