<template>
  <q-page class="q-pa-md">
    <!-- 页面说明 -->
    <div class="text-h5 q-mb-sm">Self Deployment</div>

    <div class="text-subtitle1 text-grey-8 q-mb-lg">
      Of course, <span class="text-bold text-primary">Deploy Center</span> can deploy itself —  
      with a little help from its buddy <span class="text-bold text-primary">Deploy Agent</span>.  
      Just remember to deploy the <span class="text-bold text-primary">Deploy Agent</span> first —  
      the one that must be on the same server as <span class="text-bold text-primary">Deploy Center</span> .  
      It deploys itself, so it can deploy more Deploy Agents,  
      which then help deploy the one and only <span class="text-bold text-primary">Deploy Center</span>.  
      It’s not recursion... it’s ambition {{ '\uD83D\uDE02' }}. 
      {{ 'No Agent, no magic! \u2728' }}
    </div>

    <!-- Section: Deploy Center -->
    <div class="text-subtitle1 text-bold q-mb-sm"> Deploy Center</div>
    <div class="row q-col-gutter-md q-mb-xl">
      <!-- UI -->
      <div class="col-12 col-md-6">
        <q-card class="self-deploy-card">
          <q-card-section>
            <div class="text-h6">Deploy Center UI</div>
            <div class="text-subtitle2 q-mt-xs">前端界面</div>
          </q-card-section>
          <q-separator />
          <q-card-section>
            <p>上传内容：打包好的前端静态资源</p>
            <p>部署方式：解压到目标路径</p>
            <p>目标路径：<code>/data/docker/projects/webs/deploy-center</code></p>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat color="primary" icon="cloud_upload" label="上传部署" @click="deployCenterUI" />
          </q-card-actions>
        </q-card>
      </div>

      <!-- Backend -->
      <div class="col-12 col-md-6">
        <q-card class="self-deploy-card">
          <q-card-section>
            <div class="text-h6">Deploy Center Backend</div>
            <div class="text-subtitle2 q-mt-xs">后端服务</div>
          </q-card-section>
          <q-separator />
          <q-card-section>
            <p>上传内容：后端项目压缩包（包含 Dockerfile）</p>
            <p>部署方式：自动执行 <code>docker build</code> 与 <code>docker run</code></p>
            <p>部署路径：<code>/data/docker/projects/deploy-center</code></p>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat color="primary" icon="cloud_upload" label="上传部署" @click="deployCenterBackend" />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Section: Deploy Agents -->
    <div class="text-subtitle1 text-bold q-mb-sm"> Deploy Agents</div>
    <div class="row q-col-gutter-md">
      <div
        v-for="agent in agentList"
        :key="agent.id"
        class="col-12 col-md-4"
      >
        <q-card class="self-deploy-card">
          <q-card-section>
            <div class="text-h6">Deploy Agent - {{ agent.name }}</div>
            <div class="text-subtitle2 q-mt-xs">{{ agent.ip }}</div>
          </q-card-section>
          <q-separator />
          <q-card-section>
            <p>上传内容：Deploy Agent 项目压缩包</p>
            <p>部署方式：自动执行 <code>docker build</code> 与 <code>docker run</code></p>
            <!-- <p>
              状态：
              <q-badge
                :color="agent.status === 'online' ? 'green' : 'grey'"
                :label="agent.status === 'online' ? '在线' : '离线'"
              />
            </p> -->
          </q-card-section>
          <!-- <q-card-actions align="right">
            <q-btn
              flat
              color="primary"
              icon="cloud_upload"
              label="上传部署"
              @click="deployAgent(agent)"
              :disable="agent.status !== 'online'"
            />
          </q-card-actions> -->
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Notify } from 'quasar'
import { getAgentList } from 'src/api/agentApi'
import type { Agent } from 'src/types/Agent'

const agentList = ref<Agent[]>([])

const fetchAgents = async () => {
  try {
    const response = await getAgentList()
    agentList.value = response.data
  } catch (error) {
    console.error('获取 agent 列表失败', error)
  }
}

const deployCenterUI = () => {
  Notify.create({ type: 'info', message: '上传并部署前端静态资源 - 暂未实现，敬请期待！' })
}

const deployCenterBackend = () => {
  Notify.create({ type: 'info', message: '上传并部署后端代码压缩包 - 暂未实现，敬请期待！' })
}

const deployAgent = (agent: Agent) => {
  Notify.create({ type: 'info', message: '上传并部署 Agent [${agent.name}] 的代码压缩包 - 暂未实现，敬请期待！' })
}

onMounted(() => {
  fetchAgents()
})
</script>

<style scoped>
.self-deploy-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
code {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.95em;
}
</style>
