// src/stores/useSystemConfigStore.ts
import { defineStore } from 'pinia'
import { getSystemConfigList } from 'src/api/systemConfigApi'
import type { SystemConfig } from 'src/types/SystemConfig'

export const useSystemConfigStore = defineStore('systemConfigStore', {
  //  state（类型自动推断）
  state: () => ({
    configList: [] as SystemConfig[]
  }),

  //  getters
  getters: {
    configMap(state): Record<string, SystemConfig> {
      const map: Record<string, SystemConfig> = {}
      state.configList.forEach(item => {
        map[item.config_key] = item
      })
      return map
    },

    get: (state) => {
      return (key: string) =>
        state.configList.find(item => item.config_key === key)?.config_value
    },

    getConfigItem: (state) => {
      return (key: string) =>
        state.configList.find(item => item.config_key === key)
    }
  },

  //  actions
  actions: {
    async loadConfig() {
      try {
        const list = await getSystemConfigList()
        this.configList = list
      } catch (error) {
        console.error('加载系统配置失败:', error)
      }
    },

    remove(key: string) {
      this.configList = this.configList.filter(item => item.config_key !== key)
    },

    clearAll() {
      this.configList = []
    }
  }
})
