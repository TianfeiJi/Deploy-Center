<template>
  <q-page class="q-pa-md flex flex-center" style="align-items: flex-start">
    <q-card class="q-pa-xl" style="max-width: 720px; width: 100%; box-shadow: 0 8px 24px rgba(0,0,0,0.05); border-radius: 12px;">
      
      <!-- Header -->
      <div class="column items-center q-mb-lg">
        <div class="title">版本历史</div>
        <div class="version">查看 Deploy Center 的版本更新历程</div>
      </div>

      <!-- 简介 -->
      <div class="description q-mb-xl">
        以下是 Deploy Center 的版本历史记录，展示了项目的持续改进和优化历程。
      </div>

      <!-- 版本历史列表 -->
      <q-timeline color="primary">
        <q-timeline-entry title="v1.1.0" subtitle="2026-04-05">
          <ul>
            <li>重构部署体系，引入部署任务模型（Deploy Task），实现任务驱动的部署流程与状态流转</li>
            <li>新增独立部署控制台页面，替代原有部署对话框，提升操作体验</li>
            <li>构建容器可观测体系，新增监控、日志、信息、Inspect、操作等多面板能力</li>
            <li>优化部署日志结构，引入步骤化（Step）执行日志与策略标识</li>
          </ul>
        </q-timeline-entry>
        <q-timeline-entry title="v1.0.8" subtitle="2025-06-15">
          <ul>
            <li>实现实时获取项目的真实运行状态</li>
            <li>移除静态 status 字段，状态改为动态计算</li>
            <li>新增container_name字段</li>
          </ul>
        </q-timeline-entry>
        <q-timeline-entry title="v1.0.6" subtitle="2025-05-15">
          <ul>
            <li>优化</li>
          </ul>
        </q-timeline-entry>
        <q-timeline-entry title="v1.0.4" subtitle="2025-04-27">
          <ul>
            <li>重构</li>
          </ul>
        </q-timeline-entry>
        <q-timeline-entry title="v1.0.2" subtitle="2025-04-16">
          <ul>
            <li>支持2FA</li>
          </ul>
        </q-timeline-entry>
        <q-timeline-entry title="v1.0.0" subtitle="2025-04-09">
          <ul>
            <li>初始版本发布，支持基础部署流程</li>
          </ul>
        </q-timeline-entry>
      </q-timeline>

    </q-card>
  </q-page>
</template>

<script setup lang="ts">

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
</style>