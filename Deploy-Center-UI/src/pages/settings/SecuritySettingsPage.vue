<template>
  <q-page class="q-pa-md flex flex-center" style="align-items: flex-start">
    <q-card class="q-pa-xl" style="width: 100%; max-width: 900px;">
      <div class="title q-mb-xl">安全设置</div>

      <div
        v-for="item in configList"
        :key="item.config_key"
        class="config-card q-mb-xl"
      >
        <div class="config-name">{{ item.config_name }}</div>
        <div class="config-remark">{{ item.config_remark }}</div>

        <!-- 输入 + 保存 -->
        <div class="row items-center q-gutter-sm q-mb-sm">
          <!-- 布尔值用 element-plus -->
          <el-switch
            v-if="typeof item.config_value === 'boolean'"
            v-model="item.config_value"
            active-text="启用"
            inactive-text="禁用"
          />

          <!-- 数字输入 -->
          <q-input
            v-else-if="typeof item.config_value === 'number'"
            v-model.number="item.config_value"
            type="number"
            filled
            dense
            class="input-field"
          />

          <!-- 字符串输入 -->
          <q-input
            v-else
            v-model="item.config_value"
            type="text"
            filled
            dense
            class="input-field"
          />

          <!-- 保存按钮 -->
          <q-btn
            label="保存"
            color="primary"
            size="sm"
            @click="onSave(item)"
            class="q-ml-sm"
          />
        </div>

        <q-separator class="q-mt-md" />
      </div>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  getSystemConfigList,
  updateSystemConfig
} from 'src/api/systemConfigApi'
import { Notify } from 'quasar'
import { SystemConfig } from 'src/types/SystemConfig'

const configList = ref<SystemConfig[]>([])

const fetchConfigs = async () => {
  const all = await getSystemConfigList()
  configList.value = all.filter((item: SystemConfig) => item.config_group === '安全设置')
}

const onSave = async (item: SystemConfig) => {
  try {
    const updatedData: Partial<SystemConfig> = {
      config_value: item.config_value
    }
    await updateSystemConfig(item.config_key, updatedData)
    Notify.create({ type: 'positive', message: '保存成功' })
  } catch (error) {
    Notify.create({ type: 'negative', message: '保存失败' })
  }
}

onMounted(fetchConfigs)
</script>

<style scoped>
.title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #222;
}

.config-card {
  padding-bottom: 16px;
}

.config-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.config-remark {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 10px;
}

.input-field {
  min-width: 300px;
  flex-grow: 1;
}
</style>
