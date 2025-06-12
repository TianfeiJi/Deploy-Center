<template>
    <div id="cy" class="w-full h-screen bg-[#1e1e1e]"></div>

    <!-- 节点详情弹窗 -->
    <q-dialog v-model="dialogVisible">
        <q-card class="min-w-[320px] bg-white rounded-xl shadow-md">
            <q-card-section class="text-h6 text-primary">
                节点详情
            </q-card-section>
            <q-card-section v-if="selectedAgent">
                <!-- Agent静态信息 -->
                <div class="text-body2">名称：{{ selectedAgent.name }}</div>
                <div class="text-body2">IP：{{ selectedAgent.ip }}</div>
                <div class="text-body2">端口：{{ selectedAgent.port }}</div>
                <div class="text-body2 break-all">服务地址：{{ selectedAgent.service_url }}</div>

                <!-- Agent运行时信息 -->
                <div class="text-body2">系统：{{ agentRuntimeInfoMap[selectedAgent.id]?.os || '未知' }}</div>
                <div class="text-body2">硬件平台：{{ agentRuntimeInfoMap[selectedAgent.id]?.product_name || '未知' }}</div>
                <div class="text-body2">状态：
                    <q-badge :color="getHealthColor(agentRuntimeInfoMap[selectedAgent.id]?.health)">
                        {{ agentRuntimeInfoMap[selectedAgent.id]?.health || '未知' }}
                    </q-badge>
                </div>
                <div class="text-body2">版本：{{ agentRuntimeInfoMap[selectedAgent.id]?.agent_version || '未知' }}</div>
            </q-card-section>
            <q-card-actions align="right">
                <q-btn flat label="关闭" v-close-popup />
            </q-card-actions>
        </q-card>
    </q-dialog>

</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import cytoscape from 'cytoscape'
import { getAgentList } from 'src/api/agentApi'
import type { Agent } from 'src/types/Agent'
import type { AgentRuntimeInfo } from 'src/types/AgentRuntimeInfo'
import { AgentCommandApi } from 'src/api/AgentCommandApi'

const dialogVisible = ref(false)
const selectedAgent = ref<Agent | null>(null)

const agentRuntimeInfoMap = ref<Record<number, AgentRuntimeInfo>>({})

const getHealthColor = (health?: string) => {
  switch (health) {
    case 'healthy':
      return 'green'
    case 'error':
      return 'red'
    default:
      return 'grey'
  }
}

onMounted(async () => {
    const res = await getAgentList()
    const agents: Agent[] = res.data || []

    // 获取每个 Agent 的运行时信息
    for (const agent of agents) {
        try {
        const api = new AgentCommandApi(agent.id)
        const info = await api.fetchInspectInfo();

        agentRuntimeInfoMap.value[agent.id] = {
            health: info.status,
            agent_version: info.agent_version,
            // productName: info.product_name,
            // sysVendor: info.sys_vendor
        };
        } catch (e) {
            agentRuntimeInfoMap.value[agent.id] = {
                health: "未知",
                agent_version: "未知",
            }
        }
    }

    await nextTick()

    const frontendUrl = window.location.origin 
    const centerUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:2000'

    const elements = {
        nodes: [
            {
                data: { id: 'deploy-center-ui', label: `Deploy Center UI\n${frontendUrl}` },
                position: { x: 500, y: 0 }
            },
            {
                data: { id: 'deploy-center', label: `Deploy Center\n${centerUrl}` },
                position: { x: 500, y: 100 }
            },
            ...agents.map((a, i) => {
                const rt = agentRuntimeInfoMap.value[a.id]
                return {
                    data: {
                        id: `agent-${a.id}`,
                        label:
                            `Deploy Agent ${i + 1} (${a.name})\n` +
                            `IP: ${a.ip}\n` +
                            `硬件平台: ${rt?.product_name || '未知'} | 系统: ${rt.os || '未知'}\n` +
                            `状态: ${rt?.health || '未知'} | 版本: ${rt?.agent_version || '未知'}`
                    },
                    position: { x: 200 + i * 320, y: 350 }
                }
            })
        ],
        edges: [
            { data: { source: 'deploy-center-ui', target: 'deploy-center' } },
            ...agents.map(a => ({
            data: { source: 'deploy-center', target: `agent-${a.id}` }
            }))
        ]
    }

    const cy = cytoscape({
        container: document.getElementById('cy'),
        elements,
        style: [
            {
                selector: 'node',
                style: {
                    shape: 'round-rectangle',
                    'background-color': '#1f2937',
                    'border-color': '#4b5563',
                    'border-width': 2,
                    width: 260,
                    height: 110,
                    label: 'data(label)',
                    'text-wrap': 'wrap',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    color: '#e5e7eb',
                    'font-family': 'monospace',
                    'font-size': 14,
                    'line-height': 1.3
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
                    'line-dash-offset': 0,
                }
            }
        ],
        layout: {
            name: 'breadthfirst',
            directed: true,
            roots: ['deploy-center'],
            spacingFactor: 1.5,
            padding: 100
        } 
    })


    // 缩放居中，适配屏幕
    cy.fit(undefined, 50)
    cy.zoom(cy.zoom() * 0.7)
    cy.center()

    // 流动动画
    let dashOffset = 0
    setInterval(() => {
        dashOffset = (dashOffset - 1 + 1000) % 10
        cy.edges().forEach(edge => {
            edge.style('line-dash-offset', dashOffset)
        })
    }, 60)

    // 点击节点事件
    cy.on('tap', 'node', (evt) => {
        const nodeId = evt.target.id()
        if (nodeId.startsWith('agent-')) {
            const agentId = parseInt(nodeId.replace('agent-', ''))
            const agent = agents.find(a => a.id === agentId)
            if (agent) {
                selectedAgent.value = agent
                dialogVisible.value = true
            }
        }
    })

})

</script>

<style scoped>
#cy {
    height: 100vh;
}
</style>