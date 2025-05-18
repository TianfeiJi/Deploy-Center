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

    <!-- 项目统计卡片 -->
    <q-card-section>
      <div class="text-h6 text-bold" style="margin-bottom: 1rem">项目统计</div>
      <div class="row q-col-gutter-md" style="margin-bottom: 0.1rem">
        <div class="col-12 col-sm-6 col-md-3" v-for="(item, index) in infoCards" :key="index">
          <q-card class="info-card">
            <q-card-section>
              <div class="text-h6">{{ item.title }}</div>
              <div class="text-h5" :class="item.class">
                {{ item.value }}
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-card-section>

    <!-- 图表区域 -->
    <q-card-section>
      <div class="row q-col-gutter-md">

        <!-- 项目类型分布图表 -->
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

        <!-- 部署历史情况图表 -->
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-bold q-mb-md">部署历史情况</div>
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
            <q-input v-if="isFetchServerInfoContinuously" v-model="fetchIntervalInSeconds" type="number" dense outlined
              min="1" placeholder="默认为 5 秒" />
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
import { AgentCommandApi } from 'src/api/AgentCommandApi';
import * as echarts from 'echarts';

const props = defineProps({
  agentId: Number,
});

// 创建 AgentCommandApi 实例
const agentCommandApi = new AgentCommandApi(props.agentId);
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
  { label: 'IP地址', value: systemInfo.value?.ip_address || '-', icon: 'public' },
  { label: 'CPU型号', value: systemInfo.value?.cpu_brand ?? '-', icon: 'memory' },
  { label: 'CPU指令集架构', value: systemInfo.value?.cpu_arch ?? '-', icon: 'developer_board' },
  { label: 'CPU逻辑核数', value: systemInfo.value?.cpu_cores_logical ?? '-', icon: 'scatter_plot' },
  { label: 'CPU物理核数', value: systemInfo.value?.cpu_cores_physical ?? '-', icon: 'grid_on' },
  { label: 'CPU主频GHz', value: systemInfo.value?.cpu_freq_ghz ?? '-', icon: 'speed' },
  {
    label: '总内存', value: systemInfo.value?.total_memory
      ? `${(systemInfo.value.total_memory / 1024).toFixed(2)} GB`
      : '-', icon: 'storage'
  },
]);

const cpuUsage = ref();
const memoryInfo = ref();
const diskInfo = ref();

// 定时器ID
let intervalId = null;

// 项目列表
const projects = ref([]);
// 部署历史列表
const deployHistorys = ref([]);

const cpuUsageChart = ref(null);
const memoryUsageChart = ref(null);
const diskUsageChart = ref(null);

const deployHistoryChart = ref(null); // 部署历史情况图表
const projectTypeChart = ref(null); // 项目类型分布图表

// 是否显示服务器设置对话框
const isShowServerSettingsDialog = ref(false);
// 是否持续获取服务器信息
const isFetchServerInfoContinuously = ref(true);
// 获取频率（单位秒），默认2秒
const fetchIntervalInSeconds = ref(2);
// 保存服务器设置
const saveServerSettings = () => {
  // 更新定时器
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

  isShowServerSettingsDialog.value = false; // 关闭对话框
};

// 打开设置对话框
const handleOpenServerSettingsDialog = async () => {
  isShowServerSettingsDialog.value = true;
  const systemConfig = await agentCommandApi.fetchSystemConfig("docker_path");
  dockerPath.value = systemConfig.config_value
};

// 定时更新系统数据和图表
const updateSystemDataAndCharts = async () => {
  try {
    cpuUsage.value = await agentCommandApi.fetchServerCpuUsage();
    memoryInfo.value = await agentCommandApi.fetchServerMemoryInfo();
    diskInfo.value = await agentCommandApi.fetchServerDiskInfo();

    initCpuUsageChart();
    initMemoryUsageChart();
    initDiskUsageChart();
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

onMounted(async () => {
  const response = await getAgent(props.agentId);
  agent.value = response.data;

  // 获取服务器数据
  systemInfo.value = await agentCommandApi.fetchServerSystemInfo();
  // 获取项目数据
  projects.value = await agentCommandApi.fetchProjectList();
  // 获取部署历史数据
  deployHistorys.value = await agentCommandApi.fetchDeployHistoryList();

  // 初始化图表
  initCharts();
  // 设置定时更新图表
  intervalId = setInterval(
    updateSystemDataAndCharts,
    fetchIntervalInSeconds.value * 1000
  );
});

onUnmounted(() => {
  // 清理定时器
  if (intervalId) {
    clearInterval(intervalId);
  }
});

const totalProjectCount = computed(() => projects.value.length); // 总项目数
const runningProjectCount = computed(
  () =>
    // 运行中项目数
    projects.value.filter((p) => p.status === 'running').length
);
const pendingProjectCount = computed(
  () =>
    // 待部署项目数
    projects.value.filter((p) => p.status === 'pending').length
);
const failedProjectCount = computed(
  () =>
    // 失败部署项目数
    projects.value.filter((p) => p.status === 'failed').length
);
const webProjectCount = computed(
  () =>
    // Web 项目数
    projects.value.filter((p) => p.project_type === 'Web').length
);
const javaProjectCount = computed(
  () =>
    // Java 项目数
    projects.value.filter((p) => p.project_type === 'Java').length
);
const pythonProjectCount = computed(
  () =>
    // Python 项目数
    projects.value.filter((p) => p.project_type === 'Python').length
);
const successRate = computed(() => {
  // 部署成功率
  const successCount = projects.value.filter(
    (p) => p.status === 'success'
  ).length;
  const failCount = failedProjectCount.value;
  return successCount + failCount > 0
    ? ((successCount / (successCount + failCount)) * 100).toFixed(1)
    : 100;
});

// 信息卡片数据
const infoCards = computed(() => [
  { title: '总项目数', value: totalProjectCount.value, class: '' },
  { title: '运行中', value: runningProjectCount.value, class: '' },
  { title: '待部署', value: pendingProjectCount.value, class: '' },
  {
    title: '失败部署',
    value: failedProjectCount.value,
    class: 'text-negative',
  },
]);

const initCharts = () => {
  // 服务器信息图表
  initCpuUsageChart();
  initMemoryUsageChart();
  initDiskUsageChart();

  // 项目类型分布图表
  initProjectTypeChart();
  // 部署历史图表
  initDeployHistoryChart();
};

// ** 只初始化一次 ECharts 实例，并在需要时更新它的配置 **
const cpuUsageChartInstance = ref(null); // 用于存储 ECharts 实例
const initCpuUsageChart = () => {
  // 只初始化一次 ECharts 实例，即只执行一次 echarts.init(), 并存储ECharts 实例，如果实例已经存在，则不再需要初始化
  // 避免Echarts警告：[ECharts] There is a chart instance already initialized on the dom.
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
            value: cpuUsage?.value || 0, // 确保有默认值
          },
        ],
      },
    ],
  });

  // 动态更新颜色
  updateGaugeColor(cpuUsageChartInstance.value, cpuUsage?.value || 0);
};

const memoryUsageChartInstance = ref(null);
const initMemoryUsageChart = () => {
  if (!memoryUsageChartInstance.value) {
    memoryUsageChartInstance.value = echarts.init(memoryUsageChart.value);
  }

  const totalMemory = memoryInfo.value?.total || 0; // 总内存，单位MB
  const usedMemory = memoryInfo.value?.used || 0; // 已用内存，单位MB

  // 转换内存大小为 GB
  const totalMemoryGB = (totalMemory / 1024).toFixed(2); // 转换为 GB 并保留两位小数
  const usedMemoryGB = (usedMemory / 1024).toFixed(2); // 转换为 GB 并保留两位小数

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
            value: memoryInfo.value?.percent || 0, // 确保有默认值
          },
        ],
      },
    ],
  });

  // 动态更新颜色
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

  const totalDisk = diskInfo.value?.total || 0; // 总磁盘，单位GB
  const usedDisk = diskInfo.value?.used || 0; // 已用磁盘，单位GB
  const freeDisk = diskInfo.value?.free || 0; // 空闲磁盘，单位GB
  const percent = diskInfo.value?.percent || 0; // 使用率

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
            value: percent || 0, // 确保有默认值
          },
        ],
      },
    ],
  });

  // 动态更新颜色
  updateGaugeColor(diskUsageChartInstance.value, percent || 0);
};

const initDeployHistoryChart = () => {
  const days = deployHistorys.value
    .map((p) => p.created_at.split('T')[0])
    .filter((v, i, a) => a.indexOf(v) === i)
    .sort((a, b) => new Date(a) - new Date(b))
    .slice(-7);

  const deployCounts = days.map(day =>
    deployHistorys.value.filter(p => p.created_at.startsWith(day)).length
  );

  const successRates = days.map(day => {
    const dayHistories = deployHistorys.value.filter(h => h.created_at.startsWith(day));
    const successCount = dayHistories.filter(h => h.status === 'success').length;
    const totalCount = dayHistories.length;
    return totalCount > 0 ? (successCount / totalCount * 100).toFixed(1) : 0;
  });

  const chart = echarts.init(deployHistoryChart.value);
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['部署次数', '成功率'],
    },
    xAxis: [
      { type: 'category', data: days, axisTick: { alignWithLabel: true } }
    ],
    yAxis: [
      {
        type: 'value',
        name: '部署次数',
        minInterval: 1,   // 保证是整数间隔
      },
      {
        type: 'value',
        name: '成功率(%)',
        max: 100,
        interval: 10,
        axisLabel: {
          formatter: '{value}%'
        }
      }
    ],
    series: [
      {
        name: '部署次数',
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
            return rate >= 80 ? 'rgba(103, 194, 58, 0.4)' : 'rgba(245, 108, 108, 0.4)';
          }
        },
      },
    ],
  });
};

const updateGaugeColor = (chart, value) => {
  // 定义默认颜色为灰色
  const defaultColor = '#CCCCCC'; // 灰色

  // 根据当前值动态更新颜色
  let colorConfig = [[1, defaultColor]]; // 默认全部为灰色

  if (value >= 0 && value <= 40) {
    colorConfig = [
      [value / 100, '#67C23A'], // 绿色
      [1, defaultColor], // 剩余的显示灰色
    ];
  } else if (value > 40 && value <= 70) {
    colorConfig = [
      [value / 100, '#E6A23C'], // 黄色
      [1, defaultColor],
    ];
  } else if (value > 70 && value <= 100) {
    colorConfig = [
      [value / 100, '#F56C6C'], // 红色
      [1, defaultColor],
    ];
  }

  // 更新图表配置
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
  /* 按钮组靠右对齐 */
  display: flex;
  justify-content: flex-end;
  /* 垂直居中 */
  align-items: center;
}
</style>
