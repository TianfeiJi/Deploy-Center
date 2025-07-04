<template>
  <q-page class="q-pa-md">
    <!-- 日志列表 -->
    <div class="row q-col-gutter-md">
      <div class="col-12">
        <q-table title="部署日志" :rows="logList" :columns="columns" row-key="filename" :loading="loading"
          :pagination="pagination" @request="onPagination" class="log-table">
          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn label="查看" size="sm" color="primary" @click="selectLog(props.row.filename)" />
            </q-td>
          </template>
        </q-table>
      </div>
    </div>

    <!-- 日志详情 -->
    <div class="row q-mt-md">
      <div class="col-12">
        <q-card class="log-content-card">
          <!-- 标题 & 切换按钮 -->
          <q-card-section class="row items-center q-pb-none">
            <div class="col-2 text-left">
              <q-btn icon="arrow_left" flat dense @click="previousLog" v-if="logList.length > 1" />
            </div>
            <div class="text-h6 col text-center">{{ selectedLog }}</div>
            <div class="col-2 text-right">
              <q-btn icon="arrow_right" flat dense @click="nextLog" v-if="logList.length > 1" />
            </div>
          </q-card-section>

          <!-- 日志内容区域 -->
          <q-card-section class="log-content-section">
            <q-scroll-area class="full-height" :thumb-style="{ background: '#888', width: '6px' }">
              <div class="log-content">
                <div v-for="(line, index) in formattedLogDetail" :key="index" v-html="line" class="log-line"></div>
              </div>
            </q-scroll-area>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { AgentProxyApi } from 'src/api/agentProxyApi';
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory';
import { formatBytes } from 'src/utils/bytesConverter';
import { formatDate } from 'src/utils/dateFormatter';
import { Notify } from 'quasar';

const logList = ref<any[]>([]);

const logDetail = ref<string>('');
const selectedLog = ref<string>('');
const currentIndex = ref<number>(0);
const loading = ref<boolean>(false);
const pagination = ref({
  page: 1,
  rowsPerPage: 5,
});


// 分页请求处理方法
const onPagination = (paginationData: { pagination: { page: number; rowsPerPage: number } }) => {
  // 更新分页参数
  pagination.value = paginationData.pagination;
  // 重新加载数据
  loadLogList();
};

onMounted(async () => {
  loading.value = true;
  try {
    logList.value = await provideCurrentAgentProxyApi().fetchDeployLogList();
    if (logList.value.length > 0) {
      selectLog(logList.value[0].filename);
    }
  } catch (error) {
    console.error('获取日志列表失败:', error);
  } finally {
    loading.value = false;
  }
});

const columns = [
  { name: 'filename', label: '文件名称', field: 'filename', sortable: true, align: 'left' as const },
  { name: 'filesize', label: '文件大小', field: 'filesize', sortable: true, align: 'left' as const, format: (val: number) => formatBytes(val) },
  { name: 'line_count', label: '行数', field: 'line_count', sortable: true, align: 'left' as const },
  { name: 'created_at', label: '创建时间', field: 'created_at', sortable: true, align: 'left' as const, format: (val: string) => formatDate(val) },
  { name: 'updated_at', label: '最近更新', field: 'updated_at', sortable: true, align: 'left' as const, format: (val: string) => formatDate(val) },
  { name: 'actions', label: '操作', field: 'actions', align: 'left' as const },
];

const loadLogList = async () => {
  try {
    logList.value = await provideCurrentAgentProxyApi().fetchDeployLogList();
  } catch (error) {
    console.error('重新加载日志列表失败:', error);
  }
};

// 选择日志并加载详情
const selectLog = async (filename: string) => {
  selectedLog.value = filename;
  loading.value = true;
  try {
    logDetail.value = await provideCurrentAgentProxyApi().fetchDeployLogContent(filename);
    currentIndex.value = logList.value.findIndex((log) => log.filename === filename);
    await nextTick();
  } catch (error) {
    console.error('获取日志详情失败:', error);
    logDetail.value = '无法加载日志详情，请稍后再试。';
  } finally {
    loading.value = false;
  }
};


// 上一个日志
const previousLog = () => {
  if (currentIndex.value > 0) {
    selectLog(logList.value[currentIndex.value - 1].filename);
  } else {
    Notify.create({ type: 'info', message: '已经是最早的日志' });
  }
};

// 下一个日志
const nextLog = () => {
  if (currentIndex.value < logList.value.length - 1) {
    selectLog(logList.value[currentIndex.value + 1].filename);
  } else {
    Notify.create({ type: 'info', message: '已经是最新日志' });
  }
};

// 精准匹配日志关键字，不影响整行颜色
const formattedLogDetail = computed(() => {
  return logDetail.value.split('\n').map((line: string) => highlightLogLine(line));
});

// 日志颜色高亮
const highlightLogLine = (line: string) => {
  const colorMap: Record<string, string> = {
    success: 'color: #00ff00; font-weight: bold;', // 绿色加粗
    fail: 'color: #ff0000;', // 红色
    error: 'color: #ff0000;', // 红色
    warning: 'color: #ffff00;', // 黄色
    debug: 'color: #488FEF;', // 蓝色
    critical: 'color: #ff00ff;', // 紫色
  };

  Object.keys(colorMap).forEach((keyword: string) => {
    const regex = new RegExp(`\\b(${keyword})\\b`, 'gi');
    line = line.replace(regex, `<span style="${colorMap[keyword]}">$1</span>`);
  });

  return `<span style="color: #00ff00;">${line}</span>`; // 默认绿色
};
</script>

<style scoped>
.log-content-card {
  background-color: #282c34;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 250px);
}

.log-content-section {
  flex-grow: 1;
  /* 让内容区域占据剩余空间 */
  overflow-x: auto;
  white-space: nowrap;
  padding: 10px;
}

.log-content {
  font-size: 14px;
}

.log-line {
  padding: 2px 0;
}

.q-table {
  min-height: 200px;
}
</style>