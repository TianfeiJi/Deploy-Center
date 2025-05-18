<template>
  <q-page class="q-pa-md flex flex-center" style="align-items: flex-start">
    <q-card class="q-pa-xl" style="width: 100%;">
      <div class="title q-mb-xl">系统配置</div>

      <el-table
        :data="configList"
        style="width: 100%"
        border
        stripe
        highlight-current-row
        :row-key="(row: SystemConfig) => row.config_key"
        class="custom-config-table"
      >
        <!-- ID -->
        <el-table-column label="ID" prop="id" width="40" />

        <!-- 配置名称 -->
        <el-table-column label="名称" prop="config_name" min-width="200" />

        <!-- 配置键名 -->
        <el-table-column label="Key" prop="config_key" min-width="200" />

        <!-- 配置值 -->
        <el-table-column label="值" min-width="300">
          <template #default="{ row }: { row: SystemConfig }">
            <el-switch
              v-if="typeof row.config_value === 'boolean'"
              v-model="row.config_value"
              active-text="启用"
              inactive-text="禁用"
              class="rounded"
            />
            <el-input
              v-else-if="typeof row.config_value === 'number'"
              v-model.number="row.config_value"
              type="number"
              class="input-value"
            />
            <el-input
              v-else
              v-model="row.config_value"
              class="input-value"
            />
          </template>
        </el-table-column>

        <!-- 备注 -->
        <el-table-column label="备注" prop="config_remark" min-width="260" />

        <!-- 分组 -->
        <el-table-column label="分组" prop="config_group" width="100" />

        <!-- 创建时间 -->
        <!--
          <el-table-column label="创建时间" prop="created_at" min-width="180" align="right">
            <template #default="{ row }: { row: SystemConfig }">
              <span class="text-grey">{{ formatDate(row.created_at) }}</span>
            </template>
          </el-table-column>
        -->

        <!-- 更新时间 -->
        <!--
          <el-table-column label="更新时间" prop="updated_at" min-width="180" align="right">
            <template #default="{ row }: { row: SystemConfig }">
              <span class="text-grey">{{ formatDate(row.updated_at) }}</span>
            </template>
          </el-table-column>
        -->

        <!-- 操作 -->
        <el-table-column label="操作" width="100">
          <template #default="{ row }: { row: SystemConfig }">
            <el-button
              size="small"
              type="primary"
              @click="onSave(row)"
            >保存</el-button>
          </template>
        </el-table-column>
      </el-table>
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
  configList.value = await getSystemConfigList()
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

const formatDate = (date: Date | string | null | undefined): string => {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString()
}

onMounted(() => {
  fetchConfigs()
})
</script>


<style scoped>
.title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #222;
}

.input-value {
  width: 250px;
}

.rounded {
  border-radius: 6px;
}

.text-grey {
  color: #888;
}

.custom-config-table >>> .el-table__header th {
  font-weight: 600;
  background-color: #fafafa;
}
</style>
