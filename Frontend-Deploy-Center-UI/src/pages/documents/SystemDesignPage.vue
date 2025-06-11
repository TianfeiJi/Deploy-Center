<template>
  <q-page class="q-pa-md flex flex-center" style="align-items: flex-start">
    <q-card class="q-pa-xl" style="max-width: 960px; width: 100%; box-shadow: 0 8px 24px rgba(0,0,0,0.05); border-radius: 12px;">
      <!-- 页面主标题 -->
      <div class="column items-center q-mb-lg">
        <div class="text-h4 text-weight-bold">系统架构设计</div>
        <div class="text-subtitle2 text-grey-7 q-mt-xs">Deploy Center 技术栈与架构设计说明</div>
      </div>

      <!-- 小节：项目技术栈 -->
      <div class="q-mb-xl">
        <div class="text-h6 text-weight-medium q-mb-sm">1. 项目技术栈</div>
        <div class="tech-section q-mt-md">
          <div class="tech-title">Deploy Center</div>
          <ul>
            <li><b>前端</b>：Quasar Framework 2 (Vue 3 + TypeScript)、Pinia、Vue Router、Vite</li>
            <li><b>后端</b>：FastAPI (Python 3.9+)</li>
          </ul>
        </div>
        <div class="tech-section q-mt-md">
          <div class="tech-title">Deploy Agent</div>
          <ul>
            <li><b>后端</b>：FastAPI (Python 3.9+)</li>
          </ul>
        </div>
      </div>

      <!-- 小节：项目架构图 -->
      <div class="q-mb-xl">
        <div class="text-h6 text-weight-medium q-mb-sm">2. 项目架构图</div>
        <img src="images/architecture.jpg" alt="系统架构图" class="architecture-img" />
      </div>

      <!-- 小节：架构设计说明 -->
      <div class="q-mb-xl">
        <div class="text-h6 text-weight-medium q-mb-sm">3. 架构设计说明</div>
        <div class="description">
         <div class="tech-title">Deploy Center</div>
          <ul>
            <li><b>Deploy Center UI (部署中心前端)</b>：提供图形化界面，供用户进行操作，发送部署指令和管理任务。</li>
            <li><b>Deploy Center (部署中心后端)</b>：接收来自管理前端的请求，负责调度部署指令，并将指令下发到各个 Deploy Agent。同时负责整个系统的安全校验。</li>
          </ul>
          <p>
            <b>Deploy Center</b> 部署在支持外网访问的中间服务器中，可以接收来自外部网络的请求。它是整个部署系统的管理和控制中心，负责接收用户指令、调度部署任务，并与各个 <b>Deploy Agent</b> 进行通信。
          </p>

         <div class="tech-title">Deploy Agents</div>
          <ul>
            <li><b>项目部署API</b>：部署在业务服务器上，对外暴露API完成项目的部署任务，其API无法直接调用，要通过 <b>Deploy Center</b> 来调用，确保系统的安全性。</li>
            <li><b>业务服务管理</b>：每台业务服务器可以部署多个各种类型的业务服务，由 <b>Deploy Agent</b> 管理和维护。</li>
          </ul>

          <h5 class="q-mt-md q-mb-xs">补充说明</h5>
          <p>
            <b>Deploy Agent</b> 是部署在业务服务器上的后端服务，负责执行具体的部署任务。它接收来自 <b>Deploy Center</b> 的指令，完成服务的部署、更新和管理。<b>Deploy Agent</b> 不一定支持外网访问，通常部署在内部网络中，仅通过 <b>Deploy Center</b> 进行管理和通信。
          </p>
        </div>
      </div>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
</script>

<style scoped>
.tech-section ul {
  padding-left: 1.2em;
  color: #444;
  font-size: 0.95rem;
  line-height: 1.8;
}

.tech-title {
  font-weight: 800;
  color: #555;
  margin-bottom: 4px;
}

.description {
  font-size: 0.95rem;
  color: #444;
  line-height: 1.7;
}

.description ul {
  padding-left: 1.4em;
  margin-bottom: 1em;
}

.description p {
  margin: 0.6em 0;
}

.architecture-img {
  width: 100%;
  max-width: 100%;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}
</style>
