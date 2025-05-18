<template>
    <div id="cy" class="w-full h-screen bg-[#1e1e1e]"></div>

    <!-- 节点详情弹窗 -->
    <q-dialog v-model="dialogVisible">
        <q-card class="min-w-[320px] bg-white rounded-xl shadow-md">
            <q-card-section class="text-h6 text-primary">
                节点详情
            </q-card-section>
            <q-card-section v-if="selectedAgent">
                <div class="text-body2">名称：{{ selectedAgent.name }}</div>
                <div class="text-body2">IP：{{ selectedAgent.ip }}</div>
                <div class="text-body2">类型：{{ selectedAgent.type }}</div>
                <div class="text-body2">系统：{{ selectedAgent.os }}</div>
                <div class="text-body2">状态：
                    <q-badge :color="selectedAgent.status === 'online' ? 'green' : 'red'">
                        {{ selectedAgent.status }}
                    </q-badge>
                </div>
                <div class="text-body2 break-all">服务地址：{{ selectedAgent.service_url }}</div>
            </q-card-section>
            <q-card-actions align="right">
                <q-btn flat label="关闭" v-close-popup />
            </q-card-actions>
        </q-card>
    </q-dialog>

</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { getAgentList } from 'src/api/agentApi'
import type { Agent } from 'src/types/Agent'
import cytoscape from 'cytoscape'

const dialogVisible = ref(false)
const selectedAgent = ref<Agent | null>(null)

onMounted(async () => {
    const res = await getAgentList()
    const agents: Agent[] = res.data || []

    await nextTick()

    const elements = {
        nodes: [
            {
                data: { id: 'deploy-center', label: 'Deploy Center\n部署中心' },
                position: { x: 500, y: 100 }
            },
            ...agents.map((a, i) => ({
                data: {
                    id: `agent-${a.id}`,
                    label:
                        `Deploy Agent ${i + 1} (${a.name})\n` +
                        `IP: ${a.ip}\n` +
                        `类型: ${a.type} | 系统: ${a.os}\n` +
                        `状态: ${a.status === 'online' ? '在线' : '离线'}`
                },
                position: { x: 200 + i * 320, y: 350 }
            }))
        ],
        edges: agents.map(a => ({
            data: { source: 'deploy-center', target: `agent-${a.id}` }
        }))
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