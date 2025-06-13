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
        <q-timeline-entry title="v1.2.0" subtitle="2025-06-01">
          <ul>
            <li>支持定时部署</li>
            <li>支持部署历史记录，并支持一键回滚</li>
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