import {defineStore} from 'pinia';
import { Server } from 'src/types/Server';

export const useServerStore = defineStore('serverStore', {
  state: () => ({
    serverList: [] as Server[], // 服务器列表
    currentServer: null as Server | null, // 当前选中的服务器
  }),

  actions: {
    // 添加服务器
    addServer(server: Server) {
      this.serverList.push(server);
    },

    // 删除服务器
    removeServer(serverId: number) {
      this.serverList = this.serverList.filter(server => server.id !== serverId);
    },

    // 设置当前选中的服务器
    setCurrentServer(server: Server | null) {
      this.currentServer = server;
    },

    // 清空服务器列表
    clearServers() {
      this.serverList = [];
      this.currentServer = null;
    },
  },

  getters: {
    // 获取服务器列表
    getServerList: (state) => state.serverList,

    // 获取当前选中的服务器
    getCurrentServer: (state) => state.currentServer,
  },
});