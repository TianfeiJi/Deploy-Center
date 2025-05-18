<template>
  <q-page class="q-pa-md flex flex-center" style="align-items: flex-start">
    <q-card
      class="q-pa-xl"
      style="max-width: 720px; width: 100%; box-shadow: 0 8px 24px rgba(0,0,0,0.05); border-radius: 12px;"
    >
      <!-- Header -->
      <div class="column items-center q-mb-lg">
        <div class="title">更新计划</div>
        <div class="version">不断改进，持续进化</div>
      </div>

      <!-- 简介 -->
      <div class="description q-mb-xl">
        以下是 Deploy Center 的开发计划与即将推出的新特性，你可以点击
        <span class="highlight">“催更”</span> 来表达你对某项功能的期待。
      </div>

      <!-- 更新列表 -->
      <q-list bordered separator>
        <q-item
          v-for="(feature, index) in sortedFeatures"
          :key="feature.name"
          class="q-py-md items-center"
        >
          <!-- 序号 -->
          <q-item-section avatar>
            <q-avatar color="grey-3" text-color="grey-9" size="32px">
              {{ index + 1 }}
            </q-avatar>
          </q-item-section>

          <!-- 功能名称 -->
          <q-item-section>
            <q-item-label class="feature-name">{{ feature.name }}</q-item-label>
          </q-item-section>

          <!-- 催更按钮 + 数字 -->
          <q-item-section side>
            <div class="row items-center no-wrap">
              <q-badge color="deep-orange-6" class="q-ml-sm">{{ feature.urgency }}</q-badge>

              <q-btn
                dense
                flat
                color="deep-orange-6"
                icon="bolt"
                size="sm"
                class="q-px-sm"
                @click="incrementUrgency(feature)"
              >
                <span class="q-ml-xs">催更</span>
              </q-btn>
            </div>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const features = ref([
  { name: '支持部署记录及部署回滚', urgency: 594 },
  { name: '权限分组优化', urgency: 0 },
  { name: '用户界面优化', urgency: 0 },
  { name: '性能监控与分析', urgency: 123 },
  { name: '实现云构建部署', urgency: 666 },
  { name: '网速监控', urgency: 0 },
  { name: '支持黑夜模式', urgency: 0 },
  { name: '文档与教程完善', urgency: 0 },
  { name: '实现Docker路由', urgency: 758 },
  { name: '通过Docker路由获取项目信息', urgency: 888 }
])

const sortedFeatures = computed(() =>
  [...features.value].sort((a, b) => b.urgency - a.urgency)
)

function incrementUrgency(feature: { name: string; urgency: number }) {
  feature.urgency += 1
}
</script>

<style scoped>
.title {
  font-size: 2rem;
  font-weight: 700;
  color: #222;
}
.version {
  font-size: 1rem;
  color: #666;
  margin-top: 4px;
}
.description {
  font-size: 1.05rem;
  line-height: 1.8;
  text-align: center;
  color: #444;
}
.highlight {
  font-weight: 600;
  color: #fb8c00; /* deep-orange-6 */
}
.feature-name {
  font-size: 1.05rem;
  font-weight: 500;
}
</style>
