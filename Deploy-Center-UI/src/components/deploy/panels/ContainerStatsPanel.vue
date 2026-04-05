<template>
  <section class="container-stats-panel">
    <template v-if="projectType === 'web'">
      <div class="empty-state-card">
        <div class="empty-state-title">当前项目无资源监控</div>
        <div class="empty-state-desc">
          Web 项目当前不展示 Docker 容器资源监控信息。
        </div>
      </div>
    </template>

    <template v-else-if="!containerName">
      <div class="empty-state-card">
        <div class="empty-state-title">未配置容器名称</div>
        <div class="empty-state-desc">
          当前项目未配置 container_name，无法获取容器资源监控信息。
        </div>
      </div>
    </template>

    <template v-else>
      <div class="panel-header">
        <div class="panel-header-left">
          <div class="panel-title">容器监控</div>
          <div class="panel-subtitle">
            基于 docker stats 获取当前容器资源快照，默认每 2 秒自动刷新，展示最近采样窗口趋势。
          </div>
        </div>

        <div class="panel-actions">
          <button class="action-btn action-btn-secondary" :disabled="loading" @click="handleRefreshClick">
            {{ loading ? '加载中...' : '立即刷新' }}
          </button>

          <button class="action-btn action-btn-secondary" :disabled="loading || history.length === 0"
            @click="handleExportJson">
            导出 JSON
          </button>
        </div>
      </div>

      <div class="toolbar-card">
        <div class="toolbar-row">
          <div class="toolbar-item">
            <span class="toolbar-label">容器名称</span>
            <span class="toolbar-value">{{ containerName }}</span>
          </div>

          <div class="toolbar-item">
            <span class="toolbar-label">自动刷新</span>
            <el-switch v-model="autoRefresh" inline-prompt active-text="开" inactive-text="关" />
          </div>

          <div class="toolbar-item interval-item">
            <span class="toolbar-label">刷新频率</span>
            <el-input-number v-model="refreshIntervalSeconds" :min="1" :max="30" :step="1" controls-position="right"
              :disabled="!autoRefresh" class="toolbar-number-input" />
            <span class="toolbar-unit">秒</span>
          </div>

          <div class="toolbar-item interval-item">
            <span class="toolbar-label">采样点数</span>
            <el-input-number v-model="maxHistoryPoints" :min="10" :max="120" :step="5" controls-position="right"
              class="toolbar-number-input" />
            <span class="toolbar-unit">点</span>
          </div>
        </div>

        <div class="toolbar-row toolbar-row-actions">
          <div class="toolbar-item toolbar-item-actions">
            <span class="toolbar-label">图表控制</span>

            <div class="chart-batch-actions">
              <button class="mini-btn" @click="enableAllCharts">全部开启</button>
              <button class="mini-btn" @click="disableAllCharts">全部关闭</button>
              <button class="mini-btn" @click="resetDefaultCharts">恢复默认</button>
            </div>
          </div>
        </div>

        <div class="chart-toggle-grid">
          <label class="chart-toggle-item">
            <el-switch v-model="chartVisible.cpu" />
            <span>CPU 使用率趋势</span>
          </label>

          <label class="chart-toggle-item">
            <el-switch v-model="chartVisible.memory" />
            <span>内存使用率趋势</span>
          </label>

          <label class="chart-toggle-item">
            <el-switch v-model="chartVisible.network" />
            <span>网络 I/O 趋势</span>
          </label>

          <label class="chart-toggle-item">
            <el-switch v-model="chartVisible.blockIo" />
            <span>磁盘 I/O 趋势</span>
          </label>

          <label class="chart-toggle-item">
            <el-switch v-model="chartVisible.pids" />
            <span>进程数趋势</span>
          </label>
        </div>
      </div>

      <div v-if="loading && !stats" class="loading-state-card">
        <q-spinner color="primary" size="28px" />
        <div class="loading-state-text">加载容器资源监控中...</div>
      </div>

      <template v-else-if="stats">
        <div class="stats-grid">
          <div class="stats-card">
            <div class="stats-label">CPU 使用率</div>
            <div class="stats-value">{{ stats.CPUPerc || '-' }}</div>
          </div>

          <div class="stats-card">
            <div class="stats-label">内存使用率</div>
            <div class="stats-value">{{ stats.MemPerc || '-' }}</div>
          </div>

          <div class="stats-card">
            <div class="stats-label">内存占用</div>
            <div class="stats-value">{{ stats.MemUsage || '-' }}</div>
          </div>

          <div class="stats-card">
            <div class="stats-label">网络 I/O</div>
            <div class="stats-value">{{ stats.NetIO || '-' }}</div>
          </div>

          <div class="stats-card">
            <div class="stats-label">磁盘 I/O</div>
            <div class="stats-value">{{ stats.BlockIO || '-' }}</div>
          </div>

          <div class="stats-card">
            <div class="stats-label">进程数</div>
            <div class="stats-value">{{ stats.PIDs || '-' }}</div>
          </div>
        </div>

        <div class="chart-grid">
          <div v-if="chartVisible.cpu" class="chart-card">
            <div class="chart-title-row">
              <div class="chart-title">CPU 使用率趋势</div>
              <div class="chart-meta">最近 {{ history.length }} / {{ maxHistoryPoints }} 个采样点</div>
            </div>
            <div ref="cpuChartRef" class="chart-box"></div>
          </div>

          <div v-if="chartVisible.memory" class="chart-card">
            <div class="chart-title-row">
              <div class="chart-title">内存使用率趋势</div>
              <div class="chart-meta">最近 {{ history.length }} / {{ maxHistoryPoints }} 个采样点</div>
            </div>
            <div ref="memoryChartRef" class="chart-box"></div>
          </div>

          <div v-if="chartVisible.network" class="chart-card">
            <div class="chart-title-row">
              <div class="chart-title">网络 I/O 趋势</div>
              <div class="chart-meta">RX / TX</div>
            </div>
            <div ref="networkChartRef" class="chart-box"></div>
          </div>

          <div v-if="chartVisible.blockIo" class="chart-card">
            <div class="chart-title-row">
              <div class="chart-title">磁盘 I/O 趋势</div>
              <div class="chart-meta">Read / Write</div>
            </div>
            <div ref="blockIoChartRef" class="chart-box"></div>
          </div>

          <div v-if="chartVisible.pids" class="chart-card">
            <div class="chart-title-row">
              <div class="chart-title">进程数趋势</div>
              <div class="chart-meta">PIDs</div>
            </div>
            <div ref="pidsChartRef" class="chart-box"></div>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="empty-state-card">
          <div class="empty-state-title">暂无资源监控数据</div>
          <div class="empty-state-desc">
            当前未获取到容器资源快照信息，请稍后重试。
          </div>
        </div>
      </template>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { Notify } from 'quasar'
import * as echarts from 'echarts'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'

type ProjectLike = {
  id?: string | number
  project_type?: string
  container_name?: string
}

type DockerContainerStatsResponse = {
  BlockIO?: string
  CPUPerc?: string
  Container?: string
  ID?: string
  MemPerc?: string
  MemUsage?: string
  Name?: string
  NetIO?: string
  PIDs?: string
}

type HistoryPoint = {
  timestamp: number
  timeLabel: string
  cpu: number
  memory: number
  pids: number
  netRx: number
  netTx: number
  blockRead: number
  blockWrite: number
}

const props = defineProps<{
  project: ProjectLike
}>()

const agentProxyApi = provideCurrentAgentProxyApi()

const loading = ref(false)
const stats = ref<DockerContainerStatsResponse | null>(null)
const history = ref<HistoryPoint[]>([])

const autoRefresh = ref(true)
const refreshIntervalSeconds = ref(2)
const maxHistoryPoints = ref(20)

const chartVisible = reactive({
  cpu: true,
  memory: true,
  network: false,
  blockIo: false,
  pids: false,
})

const cpuChartRef = ref<HTMLElement | null>(null)
const memoryChartRef = ref<HTMLElement | null>(null)
const networkChartRef = ref<HTMLElement | null>(null)
const blockIoChartRef = ref<HTMLElement | null>(null)
const pidsChartRef = ref<HTMLElement | null>(null)

let autoRefreshTimer: number | null = null
let resizeTimer: number | null = null
let resizeObserver: ResizeObserver | null = null

let cpuChart: echarts.ECharts | null = null
let memoryChart: echarts.ECharts | null = null
let networkChart: echarts.ECharts | null = null
let blockIoChart: echarts.ECharts | null = null
let pidsChart: echarts.ECharts | null = null

const projectType = computed(() => {
  return String(props.project.project_type || '').toLowerCase().trim()
})

const containerName = computed(() => {
  return String(props.project.container_name || '').trim()
})

function enableAllCharts() {
  chartVisible.cpu = true
  chartVisible.memory = true
  chartVisible.network = true
  chartVisible.blockIo = true
  chartVisible.pids = true
  void nextTick().then(() => {
    renderCharts()
    setupResizeObserver()
  })
}

function disableAllCharts() {
  chartVisible.cpu = false
  chartVisible.memory = false
  chartVisible.network = false
  chartVisible.blockIo = false
  chartVisible.pids = false
  disposeInvisibleCharts()
}

function resetDefaultCharts() {
  chartVisible.cpu = true
  chartVisible.memory = true
  chartVisible.network = false
  chartVisible.blockIo = false
  chartVisible.pids = false
  void nextTick().then(() => {
    renderCharts()
    setupResizeObserver()
  })
}

function stopAutoRefresh() {
  if (autoRefreshTimer !== null) {
    window.clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
}

function startAutoRefresh() {
  stopAutoRefresh()

  if (!autoRefresh.value) return
  if (!containerName.value) return

  autoRefreshTimer = window.setInterval(() => {
    if (loading.value) return
    void loadContainerStats(false)
  }, refreshIntervalSeconds.value * 1000)
}

function parsePercent(value?: string): number {
  if (!value) return 0
  const num = parseFloat(String(value).replace('%', '').trim())
  return Number.isNaN(num) ? 0 : num
}

function parseInteger(value?: string): number {
  if (!value) return 0
  const num = parseInt(String(value).trim(), 10)
  return Number.isNaN(num) ? 0 : num
}

function parseSizeToBytes(value: string): number {
  const text = String(value || '').trim()
  if (!text) return 0

  const match = text.match(/^([\d.]+)\s*([a-zA-Z]+)?$/)
  if (!match) return 0

  const num = parseFloat(match[1])
  const unit = (match[2] || 'B').toUpperCase()

  if (Number.isNaN(num)) return 0

  const unitMap: Record<string, number> = {
    B: 1,
    KB: 1024,
    KIB: 1024,
    MB: 1024 ** 2,
    MIB: 1024 ** 2,
    GB: 1024 ** 3,
    GIB: 1024 ** 3,
    TB: 1024 ** 4,
    TIB: 1024 ** 4,
  }

  return num * (unitMap[unit] || 1)
}

function parseIoPair(value?: string): [number, number] {
  const text = String(value || '').trim()
  if (!text) return [0, 0]

  const parts = text.split('/').map(item => item.trim())
  if (parts.length < 2) return [0, 0]

  return [parseSizeToBytes(parts[0]), parseSizeToBytes(parts[1])]
}

function formatBytes(value: number): string {
  if (!Number.isFinite(value) || value <= 0) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = value
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex += 1
  }

  return `${size.toFixed(size >= 100 ? 0 : size >= 10 ? 1 : 2)} ${units[unitIndex]}`
}

function formatTimeLabel(ts: number): string {
  const date = new Date(ts)
  return date.toLocaleTimeString()
}

function appendHistory(res: DockerContainerStatsResponse) {
  const now = Date.now()
  const [netRx, netTx] = parseIoPair(res.NetIO)
  const [blockRead, blockWrite] = parseIoPair(res.BlockIO)

  history.value.push({
    timestamp: now,
    timeLabel: formatTimeLabel(now),
    cpu: parsePercent(res.CPUPerc),
    memory: parsePercent(res.MemPerc),
    pids: parseInteger(res.PIDs),
    netRx,
    netTx,
    blockRead,
    blockWrite,
  })

  if (history.value.length > maxHistoryPoints.value) {
    history.value.splice(0, history.value.length - maxHistoryPoints.value)
  }
}

function trimHistoryToLimit() {
  if (history.value.length > maxHistoryPoints.value) {
    history.value.splice(0, history.value.length - maxHistoryPoints.value)
  }
}

function ensureChart(
  chartRef: HTMLElement | null,
  currentChart: echarts.ECharts | null
): echarts.ECharts | null {
  if (!chartRef) return null
  if (currentChart) return currentChart
  return echarts.init(chartRef)
}

function disposeInvisibleCharts() {
  if (!chartVisible.cpu && cpuChart) {
    cpuChart.dispose()
    cpuChart = null
  }
  if (!chartVisible.memory && memoryChart) {
    memoryChart.dispose()
    memoryChart = null
  }
  if (!chartVisible.network && networkChart) {
    networkChart.dispose()
    networkChart = null
  }
  if (!chartVisible.blockIo && blockIoChart) {
    blockIoChart.dispose()
    blockIoChart = null
  }
  if (!chartVisible.pids && pidsChart) {
    pidsChart.dispose()
    pidsChart = null
  }
}

function resizeAllCharts() {
  cpuChart?.resize()
  memoryChart?.resize()
  networkChart?.resize()
  blockIoChart?.resize()
  pidsChart?.resize()
}

function debounceResizeAllCharts() {
  if (resizeTimer !== null) {
    window.clearTimeout(resizeTimer)
  }

  resizeTimer = window.setTimeout(() => {
    resizeAllCharts()
  }, 80)
}

function setupResizeObserver() {
  resizeObserver?.disconnect()

  resizeObserver = new ResizeObserver(() => {
    debounceResizeAllCharts()
  })

  const refs = [
    cpuChartRef.value,
    memoryChartRef.value,
    networkChartRef.value,
    blockIoChartRef.value,
    pidsChartRef.value,
  ]

  refs.forEach((el) => {
    if (el) {
      resizeObserver?.observe(el)
    }
  })
}

function buildBaseChartOption() {
  return {
    animation: true,
    animationDuration: 200,
    animationDurationUpdate: 300,
    animationEasing: 'linear' as const,
    animationEasingUpdate: 'linear' as const,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line',
      },
      backgroundColor: 'rgba(15, 23, 42, 0.94)',
      borderColor: 'rgba(148, 163, 184, 0.25)',
      textStyle: {
        color: '#e2e8f0',
      },
    },
    grid: {
      left: 44,
      right: 16,
      top: 28,
      bottom: 34,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: history.value.map(item => item.timeLabel),
      axisLine: {
        lineStyle: {
          color: '#e2e8f0',
        },
      },
      axisTick: {
        show: false,
      },
      axisLabel: {
        rotate: 30,
        color: '#94a3b8',
        hideOverlap: true,
        interval: 'auto',
      },
      splitLine: {
        show: false,
      },
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false,
      },
      axisTick: {
        show: false,
      },
      axisLabel: {
        color: '#94a3b8',
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(226, 232, 240, 0.7)',
        },
      },
    },
  }
}

function renderCharts() {
  const baseOption = buildBaseChartOption()

  if (chartVisible.cpu) {
    cpuChart = ensureChart(cpuChartRef.value, cpuChart)
    cpuChart?.setOption({
      ...baseOption,
      yAxis: {
        ...baseOption.yAxis,
        min: 0,
        axisLabel: { color: '#94a3b8', formatter: '{value}%' },
      },
      series: [
        {
          name: 'CPU',
          type: 'line',
          smooth: 0,
          showSymbol: true,
          symbol: 'circle',
          symbolSize: 5,
          sampling: 'none',
          lineStyle: { width: 2 },
          areaStyle: { opacity: 0.08 },
          data: history.value.map(item => item.cpu),
        },
      ],
    }, true)
  }

  if (chartVisible.memory) {
    memoryChart = ensureChart(memoryChartRef.value, memoryChart)
    memoryChart?.setOption({
      ...baseOption,
      yAxis: {
        ...baseOption.yAxis,
        min: 0,
        axisLabel: { color: '#94a3b8', formatter: '{value}%' },
      },
      series: [
        {
          name: 'Memory',
          type: 'line',
          smooth: 0,
          showSymbol: true,
          symbol: 'circle',
          symbolSize: 5,
          sampling: 'none',
          lineStyle: { width: 2 },
          areaStyle: { opacity: 0.08 },
          data: history.value.map(item => item.memory),
        },
      ],
    }, true)
  }

  if (chartVisible.network) {
    networkChart = ensureChart(networkChartRef.value, networkChart)
    networkChart?.setOption({
      ...baseOption,
      legend: {
        top: 0,
        right: 0,
        textStyle: {
          color: '#64748b',
        },
        data: ['RX', 'TX'],
      },
      grid: {
        ...baseOption.grid,
        top: 42,
      },
      tooltip: {
        ...baseOption.tooltip,
        valueFormatter: (value: number) => formatBytes(value),
      },
      yAxis: {
        ...baseOption.yAxis,
        axisLabel: {
          color: '#94a3b8',
          formatter: (value: number) => formatBytes(value),
        },
      },
      series: [
        {
          name: 'RX',
          type: 'line',
          smooth: 0,
          showSymbol: true,
          symbolSize: 5,
          sampling: 'none',
          lineStyle: { width: 2 },
          data: history.value.map(item => item.netRx),
        },
        {
          name: 'TX',
          type: 'line',
          smooth: 0,
          showSymbol: true,
          symbolSize: 5,
          sampling: 'none',
          lineStyle: { width: 2 },
          data: history.value.map(item => item.netTx),
        },
      ],
    }, true)
  }

  if (chartVisible.blockIo) {
    blockIoChart = ensureChart(blockIoChartRef.value, blockIoChart)
    blockIoChart?.setOption({
      ...baseOption,
      legend: {
        top: 0,
        right: 0,
        textStyle: {
          color: '#64748b',
        },
        data: ['Read', 'Write'],
      },
      grid: {
        ...baseOption.grid,
        top: 42,
      },
      tooltip: {
        ...baseOption.tooltip,
        valueFormatter: (value: number) => formatBytes(value),
      },
      yAxis: {
        ...baseOption.yAxis,
        axisLabel: {
          color: '#94a3b8',
          formatter: (value: number) => formatBytes(value),
        },
      },
      series: [
        {
          name: 'Read',
          type: 'line',
          smooth: 0,
          showSymbol: true,
          symbolSize: 5,
          sampling: 'none',
          lineStyle: { width: 2 },
          data: history.value.map(item => item.blockRead),
        },
        {
          name: 'Write',
          type: 'line',
          smooth: 0,
          showSymbol: true,
          symbolSize: 5,
          sampling: 'none',
          lineStyle: { width: 2 },
          data: history.value.map(item => item.blockWrite),
        },
      ],
    }, true)
  }

  if (chartVisible.pids) {
    pidsChart = ensureChart(pidsChartRef.value, pidsChart)
    pidsChart?.setOption({
      ...baseOption,
      yAxis: {
        ...baseOption.yAxis,
        min: 0,
        minInterval: 1,
      },
      series: [
        {
          name: 'PIDs',
          type: 'line',
          smooth: 0,
          showSymbol: true,
          symbolSize: 5,
          sampling: 'none',
          lineStyle: { width: 2 },
          areaStyle: { opacity: 0.05 },
          data: history.value.map(item => item.pids),
        },
      ],
    }, true)
  }

  disposeInvisibleCharts()
  debounceResizeAllCharts()
}

async function loadContainerStats(showError = true) {
  if (projectType.value === 'web') {
    stats.value = null
    history.value = []
    return
  }

  if (!containerName.value) {
    stats.value = null
    history.value = []
    return
  }

  if (loading.value) return

  loading.value = true
  try {
    const res: DockerContainerStatsResponse =
      await agentProxyApi.fetchDockerContainerStats(containerName.value)

    stats.value = res || null

    if (res) {
      appendHistory(res)
      trimHistoryToLimit()
      await nextTick()
      renderCharts()
      setupResizeObserver()
    }
  } catch (error) {
    console.error('loadContainerStats error:', error)
    stats.value = null

    if (showError) {
      Notify.create({
        type: 'negative',
        message: '加载容器资源监控失败',
        position: 'top',
      })
    }
  } finally {
    loading.value = false
  }
}

function handleRefreshClick() {
  void loadContainerStats(true)
}

function handleExportJson() {
  if (history.value.length === 0) {
    Notify.create({
      type: 'warning',
      message: '当前没有可导出的监控数据',
      position: 'top',
    })
    return
  }

  try {
    const payload = {
      container_name: containerName.value,
      exported_at: new Date().toISOString(),
      auto_refresh: autoRefresh.value,
      refresh_interval_seconds: refreshIntervalSeconds.value,
      max_history_points: maxHistoryPoints.value,
      current_stats: stats.value,
      history: history.value,
    }

    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: 'application/json;charset=utf-8',
    })

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    const safeContainerName = containerName.value || 'container'
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')

    link.href = url
    link.download = `${safeContainerName}-stats-${timestamp}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    Notify.create({
      type: 'positive',
      message: 'JSON 导出成功',
      position: 'top',
    })
  } catch (error) {
    console.error('export json error:', error)
    Notify.create({
      type: 'negative',
      message: 'JSON 导出失败',
      position: 'top',
    })
  }
}

watch(
  autoRefresh,
  () => {
    if (autoRefresh.value) {
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }
  },
  { immediate: true }
)

watch(refreshIntervalSeconds, () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

watch(maxHistoryPoints, () => {
  trimHistoryToLimit()
  void nextTick().then(renderCharts)
})

watch(
  () => [
    chartVisible.cpu,
    chartVisible.memory,
    chartVisible.network,
    chartVisible.blockIo,
    chartVisible.pids,
  ],
  async () => {
    await nextTick()
    renderCharts()
    setupResizeObserver()
  }
)

watch(
  () => [props.project.id, props.project.project_type, props.project.container_name],
  async () => {
    stopAutoRefresh()
    stats.value = null
    history.value = []
    disposeInvisibleCharts()

    await loadContainerStats()

    if (autoRefresh.value) {
      startAutoRefresh()
    }
  },
  { immediate: true }
)

window.addEventListener('resize', debounceResizeAllCharts)

onBeforeUnmount(() => {
  stopAutoRefresh()

  if (resizeTimer !== null) {
    window.clearTimeout(resizeTimer)
    resizeTimer = null
  }

  resizeObserver?.disconnect()
  resizeObserver = null

  window.removeEventListener('resize', debounceResizeAllCharts)

  cpuChart?.dispose()
  memoryChart?.dispose()
  networkChart?.dispose()
  blockIoChart?.dispose()
  pidsChart?.dispose()

  cpuChart = null
  memoryChart = null
  networkChart = null
  blockIoChart = null
  pidsChart = null
})
</script>

<style scoped>
.container-stats-panel {
  min-height: 320px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 14px;
}

.panel-header-left {
  flex: 1;
  min-width: 0;
}

.panel-title {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
}

.panel-subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.toolbar-card {
  padding: 14px 16px;
  margin-bottom: 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e5e7eb;
}

.toolbar-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.toolbar-row+.toolbar-row {
  margin-top: 12px;
}

.toolbar-row-actions {
  align-items: flex-start;
}

.toolbar-item {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 34px;
}

.toolbar-item-actions {
  align-items: flex-start;
  flex-direction: column;
}

.toolbar-label {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
}

.toolbar-value {
  font-size: 13px;
  color: #334155;
  font-weight: 700;
}

.toolbar-unit {
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
}

.interval-item {
  flex-wrap: nowrap;
}

.toolbar-number-input {
  width: 110px;
}

.chart-batch-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chart-toggle-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px 14px;
}

.chart-toggle-item {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  font-size: 13px;
  color: #334155;
}

.mini-btn,
.action-btn {
  border: none;
  border-radius: 12px;
  height: 36px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s ease;
}

.mini-btn {
  height: 32px;
  padding: 0 12px;
  background: #fff;
  color: #334155;
  border: 1px solid #dbe4ee;
}

.mini-btn:hover {
  border-color: #bfd2ff;
  color: #2563eb;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.08);
}

.action-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.action-btn-secondary {
  background: #fff;
  color: #334155;
  border: 1px solid #dbe4ee;
}

.action-btn-secondary:hover:not(:disabled) {
  border-color: #bfd2ff;
  color: #2563eb;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.08);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 14px;
}

.stats-card {
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e5e7eb;
  padding: 16px 18px;
  min-width: 0;
}

.stats-label {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
  margin-bottom: 10px;
}

.stats-value {
  font-size: 20px;
  line-height: 1.35;
  font-weight: 800;
  color: #0f172a;
  word-break: break-word;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.chart-card {
  border-radius: 18px;
  background: #fff;
  border: 1px solid #e5e7eb;
  padding: 14px;
  min-width: 0;
}

.chart-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.chart-title {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
}

.chart-meta {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
}

.chart-box {
  width: 100%;
  height: 260px;
}

.empty-state-card,
.loading-state-card {
  min-height: 280px;
  border-radius: 20px;
  border: 1px dashed #cbd5e1;
  background: rgba(255, 255, 255, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #64748b;
  gap: 10px;
  text-align: center;
  padding: 24px;
}

.empty-state-title {
  font-size: 18px;
  font-weight: 700;
  color: #334155;
}

.empty-state-desc,
.loading-state-text {
  font-size: 14px;
  color: #64748b;
  line-height: 1.7;
  max-width: 560px;
}

:deep(.el-input-number),
:deep(.el-switch) {
  vertical-align: middle;
}

@media (max-width: 1180px) {

  .stats-grid,
  .chart-toggle-grid,
  .chart-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    align-items: stretch;
  }

  .panel-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .toolbar-row {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-item {
    justify-content: space-between;
  }

  .toolbar-item-actions {
    align-items: stretch;
  }

  .chart-batch-actions {
    justify-content: flex-start;
  }

  .stats-grid,
  .chart-toggle-grid,
  .chart-grid {
    grid-template-columns: 1fr;
  }

  .chart-title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .chart-box {
    height: 220px;
  }
}
</style>