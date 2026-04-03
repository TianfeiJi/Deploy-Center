<template>
  <q-card style="padding: 1rem; width: 98vw">
    <q-card-section>
      <div class="row items-center">
        <div class="text-h5 text-bold">Deploy Agent {{ agentId }}: {{ agent.name }} ({{ agent.ip }})</div>
        <q-space />
        <q-btn flat round icon="settings" @click="handleOpenServerSettingsDialog" />
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section>
      <div class="text-h6 text-bold q-mb-md">服务器基本信息</div>

      <div class="row q-col-gutter-sm">
        <div v-for="(item, index) in serverInfoItems" :key="index" class="col-12 col-md-4">
          <q-card class="info-item" flat bordered>
            <q-card-section class="row no-wrap items-center q-pa-sm">
              <div class="q-mr-md">
                <q-icon :name="item.icon" size="1.5rem" />
              </div>
              <div>
                <div class="text-caption text-grey">{{ item.label }}</div>
                <div class="text-body2 text-bold q-mt-xs">{{ item.value }}</div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section>
      <div class="text-h6 text-bold q-mb-md">
        服务器性能监控
      </div>
      <div class="row q-gutter-md justify-center">
        <div style="width: 200px; display: flex; justify-content: center;">
          <div ref="cpuUsageChart" style="width: 180px; height: 180px;"></div>
        </div>
        <div style="width: 200px; display: flex; justify-content: center;">
          <div ref="memoryUsageChart" style="width: 180px; height: 180px;"></div>
        </div>
        <div style="width: 200px; display: flex; justify-content: center;">
          <div ref="diskUsageChart" style="width: 180px; height: 180px;"></div>
        </div>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section>
      <div class="text-h6 text-bold" style="margin-bottom: 1rem">项目统计</div>
      <div class="row q-col-gutter-md" style="margin-bottom: 0.1rem">
        <div class="col-auto" style="width: 20%;" v-for="(item, index) in projectStats" :key="index">
          <q-card class="info-card">
            <q-card-section>
              <div :class="item.class">
                <div class="text-h6">{{ item.title }}</div>
                <div class="text-h5">
                  {{ item.value }}
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-card-section>

    <q-card-section>
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-bold q-mb-md">项目类型分布</div>
            </q-card-section>
            <q-card-section>
              <div ref="projectTypeChart" style="height: 300px"></div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-bold q-mb-md">部署任务情况</div>
            </q-card-section>
            <q-card-section>
              <div ref="deployHistoryChart" style="height: 300px"></div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-card-section>

    <q-dialog v-model="isShowServerSettingsDialog" persistent>
      <q-card class="q-pa-md bg-white q-rounded-xl shadow-4" style="width: 540px; max-width: 95vw">
        <div class="q-mb-md">
          <div class="text-h6 text-primary">服务器设置</div>
        </div>
        <div class="column q-gutter-md">
          <div class="column">
            <label class="text-body2 text-grey-8 q-mb-xs">Docker 执行路径</label>
            <q-input v-model="dockerPath" dense outlined placeholder="/usr/bin/docker" />
          </div>
          <div class="row items-center justify-between">
            <div>
              <div class="text-body2 text-grey-8">实时获取服务器资源使用情况</div>
              <div class="text-caption text-grey-5">启用后系统会不断获取并刷新资源使用情况仪表盘</div>
            </div>
            <q-toggle v-model="isFetchServerInfoContinuously" />
          </div>
          <div class="column">
            <label class="text-body2 text-grey-8 q-mb-xs">获取频率（秒）</label>
            <q-input
              v-if="isFetchServerInfoContinuously"
              v-model="fetchIntervalInSeconds"
              type="number"
              dense
              outlined
              min="1"
              placeholder="默认为 5 秒"
            />
            <div v-else class="text-caption text-grey-5">当前已禁用</div>
          </div>
        </div>

        <q-separator class="q-my-md" />

        <div class="row justify-end q-gutter-sm">
          <q-btn flat label="取消" color="primary" v-close-popup />
          <q-btn unelevated label="确定" color="primary" @click="saveServerSettings" v-close-popup />
        </div>
      </q-card>
    </q-dialog>
  </q-card>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { Notify } from 'quasar';
import { getAgent } from 'src/api/agentApi';
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory';
import * as echarts from 'echarts';

const props = defineProps({
  agentId: Number,
});

const agent = ref({});

// Docker 可执行路径
const dockerPath = ref('');

// 服务器信息
const systemInfo = ref();

const serverInfoItems = computed(() => [
  { label: '系统平台', value: systemInfo.value?.platform || '-', icon: 'devices' },
  { label: '系统版本', value: systemInfo.value?.platform_version || '-', icon: 'info' },
  { label: '系统架构', value: systemInfo.value?.architecture || '-', icon: 'memory' },
  { label: '主机名', value: systemInfo.value?.hostname || '-', icon: 'dns' },
  { label: '开机时间', value: systemInfo.value?.boot_time || '-', icon: 'schedule' },
  { label: 'CPU型号', value: systemInfo.value?.cpu_brand ?? '-', icon: 'memory' },
  { label: 'CPU指令集架构', value: systemInfo.value?.cpu_arch ?? '-', icon: 'developer_board' },
  {
    label: 'CPU核心数',
    value: systemInfo.value?.cpu_cores_physical
      ? `${systemInfo.value.cpu_cores_physical} 核（物理） / ${systemInfo.value.cpu_cores_logical} 核（逻辑）`
      : '-',
    icon: 'grid_on'
  },
  {
    label: '总内存',
    value: systemInfo.value?.total_memory
      ? `${(systemInfo.value.total_memory / 1024).toFixed(2)} GB`
      : '-',
    icon: 'storage'
  },
]);

const cpuUsage = ref();
const memoryInfo = ref();
const diskInfo = ref();

// 定时器ID
let intervalId = null;

// 项目列表
const projects = ref([]);
// 部署任务列表
const deployTasks = ref([]);

const cpuUsageChart = ref(null);
const memoryUsageChart = ref(null);
const diskUsageChart = ref(null);

const deployHistoryChart = ref(null);
const projectTypeChart = ref(null);

// 是否显示服务器设置对话框
const isShowServerSettingsDialog = ref(false);
// 是否持续获取服务器信息
const isFetchServerInfoContinuously = ref(true);
// 获取频率（单位秒），默认2秒
const fetchIntervalInSeconds = ref(2);

const saveServerSettings = () => {
  if (intervalId) {
    clearInterval(intervalId);
  }

  if (isFetchServerInfoContinuously.value) {
    intervalId = setInterval(
      updateSystemDataAndCharts,
      fetchIntervalInSeconds.value * 1000
    );
    Notify.create({
      position: 'top',
      type: 'positive',
      message: `已设置成功更新频率为 ${fetchIntervalInSeconds.value} 秒`,
    });
  } else {
    Notify.create({
      position: 'top',
      type: 'positive',
      message: `已关闭实时获取服务器性能指标`,
    });
  }

  isShowServerSettingsDialog.value = false;
};

const handleOpenServerSettingsDialog = async () => {
  isShowServerSettingsDialog.value = true;
  const systemConfig = await provideCurrentAgentProxyApi().fetchSystemConfig("docker_path");
  dockerPath.value = systemConfig.config_value;
};

const updateSystemDataAndCharts = async () => {
  try {
    cpuUsage.value = await provideCurrentAgentProxyApi().fetchServerCpuUsage();
    memoryInfo.value = await provideCurrentAgentProxyApi().fetchServerMemoryInfo();
    diskInfo.value = await provideCurrentAgentProxyApi().fetchServerDiskInfo();

    initCpuUsageChart();
    initMemoryUsageChart();
    initDiskUsageChart();
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

// 项目状态统计数据
const totalProjectCount = ref(0);
const runningProjectCount = ref(0);
const exitedProjectCount = ref(0);
const restartingProjectCount = ref(0);
const awaitingDeploymentProjectCount = ref(0);

onMounted(async () => {
  const response = await getAgent(props.agentId);
  agent.value = response.data;

  systemInfo.value = await provideCurrentAgentProxyApi().fetchServerSystemInfo();
  projects.value = await provideCurrentAgentProxyApi().fetchProjectList() || [];
  deployTasks.value = await provideCurrentAgentProxyApi().fetchDeployTaskList() || [];

  const statistics = await provideCurrentAgentProxyApi().fetchProjectStatusStatistics();
  totalProjectCount.value = statistics.total;
  runningProjectCount.value = statistics.running;
  exitedProjectCount.value = statistics.exited;
  restartingProjectCount.value = statistics.restarting;
  awaitingDeploymentProjectCount.value = statistics.awaiting_deployment;

  initCharts();

  intervalId = setInterval(
    updateSystemDataAndCharts,
    fetchIntervalInSeconds.value * 1000
  );
});

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
});

const webProjectCount = computed(
  () => (Array.isArray(projects.value) ? projects.value : []).filter((p) => p.project_type === 'Web').length
);
const javaProjectCount = computed(
  () => (Array.isArray(projects.value) ? projects.value : []).filter((p) => p.project_type === 'Java').length
);
const pythonProjectCount = computed(
  () => (Array.isArray(projects.value) ? projects.value : []).filter((p) => p.project_type === 'Python').length
);

const projectStats = computed(() => [
  { title: '总项目数', value: totalProjectCount.value, class: '' },
  { title: '待部署', value: awaitingDeploymentProjectCount.value, class: 'text-grey-6' },
  { title: '运行中', value: runningProjectCount.value, class: 'text-green-6' },
  { title: '已退出', value: exitedProjectCount.value, class: 'text-red-5' },
  { title: '重启中', value: restartingProjectCount.value, class: 'text-orange-6' },
]);

const initCharts = () => {
  initCpuUsageChart();
  initMemoryUsageChart();
  initDiskUsageChart();
  initProjectTypeChart();
  initDeployHistoryChart();
};

const cpuUsageChartInstance = ref(null);
const initCpuUsageChart = () => {
  if (!cpuUsageChartInstance.value) {
    cpuUsageChartInstance.value = echarts.init(cpuUsageChart.value);
  }

  cpuUsageChartInstance.value.setOption({
    title: {
      text: 'CPU使用率',
      left: 'center',
      top: 'bottom',
      textStyle: {
        fontSize: 13,
        color: '#666',
      },
    },
    series: [
      {
        name: 'CPU 使用率',
        type: 'gauge',
        radius: '100%',
        min: 0,
        max: 100,
        startAngle: 225,
        endAngle: -45,
        splitNumber: 10,
        axisLine: {
          lineStyle: {
            width: 5,
          },
        },
        pointer: {
          length: '60%',
          width: 5,
        },
        detail: {
          formatter: `{value}%`,
          color: '#333',
          fontSize: 16,
        },
        data: [
          {
            value: cpuUsage?.value || 0,
          },
        ],
      },
    ],
  });

  updateGaugeColor(cpuUsageChartInstance.value, cpuUsage?.value || 0);
};

const memoryUsageChartInstance = ref(null);
const initMemoryUsageChart = () => {
  if (!memoryUsageChartInstance.value) {
    memoryUsageChartInstance.value = echarts.init(memoryUsageChart.value);
  }

  const totalMemory = memoryInfo.value?.total || 0;
  const usedMemory = memoryInfo.value?.used || 0;

  const totalMemoryGB = (totalMemory / 1024).toFixed(2);
  const usedMemoryGB = (usedMemory / 1024).toFixed(2);

  memoryUsageChartInstance.value.setOption({
    title: {
      text: `内存使用率\n (${usedMemoryGB} / ${totalMemoryGB} GB)`,
      left: 'center',
      top: 'bottom',
      textStyle: {
        fontSize: 13,
        color: '#666',
      },
    },
    series: [
      {
        type: 'gauge',
        radius: '100%',
        min: 0,
        max: 100,
        startAngle: 225,
        endAngle: -45,
        splitNumber: 10,
        axisLine: {
          lineStyle: {
            width: 5,
          },
        },
        pointer: {
          length: '60%',
          width: 5,
        },
        detail: {
          formatter: `{value}%`,
          color: '#333',
          fontSize: 16,
        },
        data: [
          {
            value: memoryInfo.value?.percent || 0,
          },
        ],
      },
    ],
  });

  updateGaugeColor(
    memoryUsageChartInstance.value,
    memoryInfo.value?.percent || 0
  );
};

const diskUsageChartInstance = ref(null);
const initDiskUsageChart = () => {
  if (!diskUsageChartInstance.value) {
    diskUsageChartInstance.value = echarts.init(diskUsageChart.value);
  }

  const totalDisk = diskInfo.value?.total || 0;
  const usedDisk = diskInfo.value?.used || 0;
  const percent = diskInfo.value?.percent || 0;

  diskUsageChartInstance.value.setOption({
    title: {
      text: `磁盘使用率\n (${usedDisk} / ${totalDisk} GB)`,
      left: 'center',
      top: 'bottom',
      textStyle: {
        fontSize: 13,
        color: '#666',
      },
    },
    series: [
      {
        type: 'gauge',
        radius: '100%',
        min: 0,
        max: 100,
        startAngle: 225,
        endAngle: -45,
        splitNumber: 10,
        axisLine: {
          lineStyle: {
            width: 5,
          },
        },
        pointer: {
          length: '60%',
          width: 5,
        },
        detail: {
          formatter: `{value}%`,
          color: '#333',
          fontSize: 16,
        },
        data: [
          {
            value: percent || 0,
          },
        ],
      },
    ],
  });

  updateGaugeColor(diskUsageChartInstance.value, percent || 0);
};
const deployHistoryChartInstance = ref(null);

const initDeployHistoryChart = () => {
  if (!deployHistoryChart.value) return;

  if (!deployHistoryChartInstance.value) {
    deployHistoryChartInstance.value = echarts.init(deployHistoryChart.value);
  }

  const chart = deployHistoryChartInstance.value;
  const taskList = Array.isArray(deployTasks.value) ? deployTasks.value : [];

  const validTasks = taskList.filter(task => task && task.created_at);

  if (validTasks.length === 0) {
    chart.setOption({
      title: {
        text: 'No deploy tasks',
        left: 'center',
        top: 'middle',
        textStyle: {
          fontSize: 16,
          fontWeight: 'normal',
          color: '#999',
        },
      },
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['任务次数', '成功率'],
      },
      xAxis: [
        {
          type: 'category',
          data: [],
          axisTick: { alignWithLabel: true },
        },
      ],
      yAxis: [
        {
          type: 'value',
          name: '任务次数',
          minInterval: 1,
        },
        {
          type: 'value',
          name: '成功率(%)',
          max: 100,
          interval: 10,
          axisLabel: {
            formatter: '{value}%',
          },
        },
      ],
      series: [
        {
          name: '任务次数',
          type: 'line',
          yAxisIndex: 0,
          data: [],
          smooth: true,
        },
        {
          name: '成功率',
          type: 'bar',
          yAxisIndex: 1,
          data: [],
          barWidth: '30%',
        },
      ],
    });
    return;
  }

  const days = validTasks
    .map(task => String(task.created_at).split('T')[0])
    .filter((value, index, array) => array.indexOf(value) === index)
    .sort((a, b) => new Date(a).getTime() - new Date(b).getTime())
    .slice(-7);

  const deployCounts = days.map(day =>
    validTasks.filter(task => String(task.created_at).startsWith(day)).length
  );

  const successRates = days.map(day => {
    const dayTasks = validTasks.filter(task => String(task.created_at).startsWith(day));
    const successCount = dayTasks.filter(task => task.status === 'SUCCESS').length;
    const totalCount = dayTasks.length;
    return totalCount > 0 ? Number(((successCount / totalCount) * 100).toFixed(1)) : 0;
  });

  chart.setOption({
    title: {
      text: '',
    },
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['任务次数', '成功率'],
    },
    xAxis: [
      {
        type: 'category',
        data: days,
        axisTick: { alignWithLabel: true },
      },
    ],
    yAxis: [
      {
        type: 'value',
        name: '任务次数',
        minInterval: 1,
      },
      {
        type: 'value',
        name: '成功率(%)',
        max: 100,
        interval: 10,
        axisLabel: {
          formatter: '{value}%',
        },
      },
    ],
    series: [
      {
        name: '任务次数',
        type: 'line',
        yAxisIndex: 0,
        data: deployCounts,
        smooth: true,
      },
      {
        name: '成功率',
        type: 'bar',
        yAxisIndex: 1,
        data: successRates,
        barWidth: '30%',
        itemStyle: {
          color: params => {
            const rate = params.data;
            return rate >= 80
              ? 'rgba(103, 194, 58, 0.4)'
              : 'rgba(245, 108, 108, 0.4)';
          },
        },
      },
    ],
  });
};

const updateGaugeColor = (chart, value) => {
  const defaultColor = '#CCCCCC';

  let colorConfig = [[1, defaultColor]];

  if (value >= 0 && value <= 40) {
    colorConfig = [
      [value / 100, '#67C23A'],
      [1, defaultColor],
    ];
  } else if (value > 40 && value <= 70) {
    colorConfig = [
      [value / 100, '#E6A23C'],
      [1, defaultColor],
    ];
  } else if (value > 70 && value <= 100) {
    colorConfig = [
      [value / 100, '#F56C6C'],
      [1, defaultColor],
    ];
  }

  chart.setOption({
    series: [
      {
        axisLine: {
          lineStyle: {
            color: colorConfig,
          },
        },
      },
    ],
  });
};

const initProjectTypeChart = () => {
  const chart = echarts.init(projectTypeChart.value);
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: [
          { value: webProjectCount.value, name: 'Web' },
          { value: javaProjectCount.value, name: 'Java' },
          { value: pythonProjectCount.value, name: 'Python' },
        ],
      },
    ],
  });
};
</script>

<style scope>
.info-card {
  background: #fff;
  text-align: center;
  border-radius: 8px;
  padding: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
</style>