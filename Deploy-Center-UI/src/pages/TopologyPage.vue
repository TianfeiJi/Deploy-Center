<!--
  TopologyPage.vue 拓扑图页面
  ----------------------------
  设计目的：
    展示 Deploy Center 的系统拓扑结构，包括 UI、Center 和多个 Agent 节点，
    便于用户直观理解系统架构与节点连接关系。

  设计要点：
    - 使用 Cytoscape 构建节点连接关系图
    - 借助 cytoscape-node-html-label 插件为每个节点渲染自定义 HTML 卡片作为视觉层
    - 点击节点触发 Quasar Dialog 弹窗，展示节点详细信息，提升可读性与交互体验
    - 控制 label 宽度与节点尺寸适配，避免内容溢出

  Author  Tianfei Ji
  Date    2025-06-13
-->
<template>
  <!-- Cytoscape 图可视化容器 -->
  <div id="cy" class="w-full h-screen bg-[#f9fafb] relative"></div>

  <!-- 节点详情弹窗：点击节点后展示详细信息 -->
  <q-dialog v-model="dialogVisible">
    <q-card class="min-w-[320px] bg-white rounded-xl shadow-md">
      <q-card-section class="text-h6 text-primary">
        {{ selectedNode?.label || '节点详情' }}
      </q-card-section>
      <q-card-section v-if="selectedNode">
        <div v-if="selectedNode.type === 'agent'">
          <div class="text-body2">IP：{{ selectedNode.data.ip }}</div>
          <div class="text-body2">端口：{{ selectedNode.data.port }}</div>
          <div class="text-body2 break-all">服务地址：{{ selectedNode.data.service_url }}</div>
          <div class="text-body2">
            状态：
            <q-badge :color="getHealthColor(selectedNode.data.health)">
              {{ selectedNode.data.health }}
            </q-badge>
          </div>
          <div class="text-body2">版本：
            <q-badge color="blue">
              {{ selectedNode.data.agent_version }}
            </q-badge>
          </div>
        </div>
        <div v-else-if="selectedNode.type === 'center'">
          <div class="text-body2 break-all">服务地址：{{ selectedNode.data.centerUrl }}</div>
        </div>
        <div v-else>
          <div class="text-body2 break-all">前端地址：{{ selectedNode.data.frontendUrl }}</div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import cytoscape from 'cytoscape'
// @ts-ignore
import nodeHtmlLabel from 'cytoscape-node-html-label'
import { getAgentList } from 'src/api/agentApi'
import type { Agent } from 'src/types/Agent'
import type { AgentRuntimeInfo } from 'src/types/AgentRuntimeInfo'
import { AgentCommandApi } from 'src/api/AgentCommandApi'

interface NodeCard {
  id: string
  type: 'ui' | 'center' | 'agent'
  label: string
  data: any
}

const nodes = ref<NodeCard[]>([])

const agents = ref<Agent[]>([])
const agentRuntimeInfoMap = reactive<Record<number, AgentRuntimeInfo>>({})

const dialogVisible = ref(false)
const selectedNode = ref<NodeCard | null>(null)

const getHealthColor = (health?: string) => {
  switch (health) {
    case 'healthy': return 'green'
    case 'error': return 'red'
    default: return 'grey'
  }
}

onMounted(async () => {
  cytoscape.use(nodeHtmlLabel)

  const res = await getAgentList()
  agents.value = res.data || []

  // 查询每个 Agent 的运行时状态
  for (const agent of agents.value) {
    try {
      const api = new AgentCommandApi(agent.id)
      const info = await api.fetchInspectInfo()
      agentRuntimeInfoMap[agent.id] = {
        health: info.status,
        agent_version: info.agent_version
      }
    } catch (e) {
      agentRuntimeInfoMap[agent.id] = { health: '未知', agent_version: '未知' }
    }
  }

  await nextTick()

  // 构建节点数据：Center UI、Center、Center Agents
  const frontendUrl = window.location.origin
  const centerUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:2000'

  nodes.value = [
    {
      id: 'deploy-center-ui',
      type: 'ui',
      label: 'Deploy Center UI',
      data: { frontendUrl }
    },
    {
      id: 'deploy-center',
      type: 'center',
      label: 'Deploy Center',
      data: { centerUrl }
    },
    ...agents.value.map((a, i) => ({
      id: `agent-${a.id}`,
      type: 'agent' as const,
      label: `Deploy Agent ${i + 1} (${a.name})`,
      data: {
        ip: a.ip,
        port: a.port,
        service_url: a.service_url,
        health: agentRuntimeInfoMap[a.id]?.health || '未知',
        agent_version: agentRuntimeInfoMap[a.id]?.agent_version || '未知'
      }
    }))
  ]

  // Cytoscape 图元素：包含节点和边（连接 UI -> Center -> Agent）
  const elements = {
    nodes: [
      { data: { id: 'deploy-center-ui' }, position: { x: 500, y: 0 } },
      { data: { id: 'deploy-center' }, position: { x: 500, y: 150 } },
      ...agents.value.map((a, i) => ({
        data: { id: `agent-${a.id}` },
        position: { x: 300 + i * 300, y: 350 }
      }))
    ],
    edges: [
      { data: { source: 'deploy-center-ui', target: 'deploy-center' } },
      ...agents.value.map(a => ({
        data: { source: 'deploy-center', target: `agent-${a.id}` }
      }))
    ]
  }

  // 初始化 Cytoscape 实例
  const cy = cytoscape({
    container: document.getElementById('cy')!,
    elements,
    style: [
      {
        selector: 'node',
        style: {
          width: 300,
          height: 220,
          shape: 'round-rectangle',
          'background-opacity': 0,
          'border-color': '#cbd5e1',
          'border-width': 2,
          label: ''
        }
      },
      {
        selector: 'edge',
        style: {
          width: 2,
          'line-color': '#6b7280',
          'target-arrow-color': '#6b7280',
          'target-arrow-shape': 'triangle',
          'curve-style': 'taxi',
          'line-style': 'dashed',
          'line-dash-pattern': [6, 4],
          'line-dash-offset': 0
        }
      }
    ],
    layout: { 
      name: 'breadthfirst',
      directed: true,
      roots: ['deploy-center-ui'],
      spacingFactor: 1.5,
      padding: 100
     }
  })

  // 添加点击事件，点击节点弹出详情对话框
  cy.on('tap', 'node', evt => {
    const id = evt.target.id()
    const node = nodes.value.find(n => n.id === id)
    if (node) {
      selectedNode.value = node
      dialogVisible.value = true
    }
  })

  // cytoscape-node-html-label插件：为每个节点添加 HTML label 卡片
  // @ts-ignore
  cy.nodeHtmlLabel([
    {
      query: 'node',
      halign: 'center',
      valign: 'center',
      halignBox: 'center',
      valignBox: 'center',
      tpl: function (data: any) {
        const node = nodes.value.find(n => n.id === data.id)
        if (!node) return ''
        return `
          <div style="
            background: white;
            border-radius: 8px;
            padding: 8px;
            width: 300px;
            height: 220px;
            font-size: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            pointer-events: none;
            user-select: none;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
          ">
            <div style="font-weight: bold; margin-bottom: 16px; text-align: center; font-size: 1.2rem">${node.label}</div>
            ${node.type === 'agent' ?
            `<div>IP: ${node.data.ip} | 端口: ${node.data.port}</div>
              <div>服务地址: ${node.data.service_url}</div>
              <div>状态: ${node.data.health}</div>
              <div>版本: ${node.data.agent_version}</div>`
            : node.type === 'center'
              ? `<div style="text-align: center">${node.data.centerUrl}</div>`
              : `<div style="text-align: center">${node.data.frontendUrl}</div>`}
          </div>
          `
      }
    }
  ])

  // 初始视图调整（缩放、居中）
  cy.fit(undefined, 50)
  cy.zoom(cy.zoom() * 0.7)
  cy.center()

  // 边缘虚线动画（持续位移 line-dash-offset）
  let dashOffset = 0
  setInterval(() => {
    dashOffset = (dashOffset - 1 + 1000) % 10
    cy.edges().forEach(edge => {
      edge.style('line-dash-offset', dashOffset)
    })
  }, 60)
})
</script>

<style scoped>
#cy {
  height: 100vh;
  position: relative;
  overflow: hidden;
}
</style>