<template>
  <q-page class="deploy-task-page q-pa-md">
    <div class="page-shell">
      <section class="hero-panel">
        <div class="hero-left">
          <div class="hero-kicker">Deploy Tasks</div>
          <div class="hero-title">部署任务</div>
          <div class="hero-subtitle">
            按项目分组查看部署任务，快速定位正在执行、失败与最近部署记录
          </div>
        </div>

        <div class="hero-right">
          <div class="hero-stat-group">
            <div class="hero-stat-card">
              <div class="hero-stat-label">正在执行</div>
              <div class="hero-stat-value">{{ runningTaskCount }}</div>
            </div>

            <div class="hero-stat-card">
              <div class="hero-stat-label">总任务数</div>
              <div class="hero-stat-value">{{ filteredTasks.length }}</div>
            </div>
          </div>

          <q-btn
            unelevated
            class="refresh-btn"
            icon="refresh"
            label="刷新"
            :loading="loading"
            @click="loadDeployTasks"
          />
        </div>
      </section>

      <section class="toolbar-panel">
        <div class="toolbar-left">
          <q-input
            v-model="keyword"
            dense
            outlined
            clearable
            class="toolbar-search"
            placeholder="搜索项目代号 / 项目名称 / 操作人"
          >
            <template #prepend>
              <q-icon name="search" />
            </template>
          </q-input>

          <q-select
            v-model="statusFilter"
            dense
            outlined
            emit-value
            map-options
            :options="statusOptions"
            label="状态"
            class="toolbar-select"
          />

          <q-select
            v-model="mechanismFilter"
            dense
            outlined
            emit-value
            map-options
            :options="mechanismOptions"
            label="部署方式"
            class="toolbar-select"
          />
        </div>

        <div class="toolbar-right">
          <div class="toolbar-summary">
            共 <span>{{ filteredTasks.length }}</span> 条任务，
            <span>{{ groupedTasks.length }}</span> 个项目分组
          </div>
        </div>
      </section>

      <section class="content-panel">
        <template v-if="loading">
          <div class="state-panel">
            <q-spinner size="34px" color="primary" />
            <div class="state-title">正在加载部署任务</div>
            <div class="state-desc">请稍候，正在同步当前 Agent 的任务数据</div>
          </div>
        </template>

        <template v-else-if="!currentAgent?.id">
          <div class="state-panel">
            <q-icon name="dns" size="42px" class="state-icon" />
            <div class="state-title">未选择 Agent</div>
            <div class="state-desc">请先选择一个 Agent，再查看部署任务</div>
          </div>
        </template>

        <template v-else-if="groupedTasks.length === 0">
          <div class="state-panel">
            <q-icon name="inbox" size="42px" class="state-icon" />
            <div class="state-title">暂无部署任务</div>
            <div class="state-desc">当前没有符合条件的部署任务记录</div>
          </div>
        </template>

        <template v-else>
          <div class="project-group-list">
            <section
              v-for="group in groupedTasks"
              :key="group.groupKey"
              class="project-group-card"
            >
              <div class="project-group-header">
                <div class="project-group-title-row">
                  <div class="project-group-title">
                    {{ group.project_name || '未命名项目' }}
                  </div>

                  <div
                    v-if="group.runningCount > 0"
                    class="project-running-pill"
                  >
                    运行中 {{ group.runningCount }}
                  </div>
                </div>

                <div class="project-group-meta">
                  <span class="project-code-chip">
                    {{ group.project_code || group.project_id || '-' }}
                  </span>
                  <span class="project-meta-separator">•</span>
                  <span>任务 {{ group.taskCount }}</span>
                  <span class="project-meta-separator">•</span>
                  <span>最近 {{ formatDate(group.latestCreatedAt) }}</span>
                </div>
              </div>

              <div class="task-mini-list">
                <article
                  v-for="task in group.tasks"
                  :key="task.id"
                  class="task-mini-card"
                  @click="openDetail(task)"
                >
                  <div class="task-mini-top">
                    <span
                      class="task-status-pill"
                      :class="`is-${(task.status || '').toLowerCase()}`"
                    >
                      {{ getStatusText(task.status) }}
                    </span>

                    <span class="task-mini-duration">
                      {{ formatDuration(task.duration_ms) }}
                    </span>
                  </div>

                  <div class="task-mini-body">
                    <div class="task-mini-line">
                      <span class="task-mini-label">操作人</span>
                      <span class="task-mini-value">{{ task.operator_name || '-' }}</span>
                    </div>

                    <div class="task-mini-line">
                      <span class="task-mini-label">触发方式</span>
                      <span class="task-mini-value">{{ getTriggerText(task.trigger_type) }}</span>
                    </div>

                    <div class="task-mini-line">
                      <span class="task-mini-label">创建时间</span>
                      <span class="task-mini-value">
                        {{ formatDate(task.created_at) }}
                        <span class="task-mini-sub">（{{ timeAgo(task.created_at) }}前）</span>
                      </span>
                    </div>
                  </div>

                  <div v-if="task.failed_reason" class="task-mini-error ellipsis-2">
                    {{ task.failed_reason }}
                  </div>

                  <div class="task-mini-footer">
                    <span class="task-mini-link">查看详情</span>
                  </div>
                </article>
              </div>
            </section>
          </div>
        </template>
      </section>
    </div>

    <q-dialog v-model="detailDialog">
      <q-card class="detail-dialog-card">
        <q-card-section class="dialog-header">
          <div class="dialog-header-left">
            <div class="dialog-overline">Deploy Task Detail</div>
            <div class="dialog-title">部署任务详情</div>
            <div class="dialog-subtitle">{{ selectedTask?.project_name || '-' }}</div>
          </div>

          <q-btn flat round dense icon="close" v-close-popup />
        </q-card-section>

        <q-separator />

        <q-card-section v-if="selectedTask" class="dialog-body">
          <div class="detail-panel-grid">
            <div class="detail-panel-item">
              <div class="detail-panel-label">项目代号</div>
              <div class="detail-panel-value">{{ selectedTask.project_code || '-' }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">项目名称</div>
              <div class="detail-panel-value">{{ selectedTask.project_name || '-' }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">状态</div>
              <div class="detail-panel-value">
                <span
                  class="task-status-pill"
                  :class="`is-${(selectedTask.status || '').toLowerCase()}`"
                >
                  {{ getStatusText(selectedTask.status) }}
                </span>
              </div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">触发方式</div>
              <div class="detail-panel-value">{{ getTriggerText(selectedTask.trigger_type) }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">部署方式</div>
              <div class="detail-panel-value">{{ getMechanismText(selectedTask.deploy_mechanism) }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">操作人</div>
              <div class="detail-panel-value">{{ selectedTask.operator_name || '-' }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">耗时</div>
              <div class="detail-panel-value">{{ formatDuration(selectedTask.duration_ms) }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">创建时间</div>
              <div class="detail-panel-value">{{ formatDate(selectedTask.created_at) }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">开始时间</div>
              <div class="detail-panel-value">{{ formatDate(selectedTask.started_at) }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">完成时间</div>
              <div class="detail-panel-value">{{ formatDate(selectedTask.finished_at) }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">上传文件</div>
              <div class="detail-panel-value break-all">{{ selectedTask.upload_file_name || '-' }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">镜像名称</div>
              <div class="detail-panel-value break-all">{{ selectedTask.build_image_name || '-' }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">镜像标签</div>
              <div class="detail-panel-value">{{ selectedTask.build_image_tag || '-' }}</div>
            </div>
            <div class="detail-panel-item">
              <div class="detail-panel-label">容器名称</div>
              <div class="detail-panel-value break-all">{{ selectedTask.container_name || '-' }}</div>
            </div>
          </div>

          <div v-if="selectedTask.failed_reason" class="detail-block">
            <div class="detail-block-title">失败原因</div>
            <div class="detail-alert error">{{ selectedTask.failed_reason }}</div>
          </div>

          <div v-if="selectedTask.dockercommand_content" class="detail-block">
            <div class="detail-block-title">Docker 命令</div>
            <pre class="detail-code-block">{{ selectedTask.dockercommand_content }}</pre>
          </div>

          <div v-if="selectedTask.dockerfile_content" class="detail-block">
            <div class="detail-block-title">Dockerfile 内容</div>
            <pre class="detail-code-block">{{ selectedTask.dockerfile_content }}</pre>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useAgentStore } from 'src/stores/useAgentStore';
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory';
import { formatDate } from 'src/utils/dateFormatter';
import type { DeployTask } from 'src/types/DeployTask';

type DeployTaskWithProject = DeployTask & {
  project_code?: string;
  project_name?: string;
};

type DeployTaskGroup = {
  groupKey: string;
  project_id?: string;
  project_code?: string;
  project_name?: string;
  taskCount: number;
  runningCount: number;
  latestCreatedAt?: string;
  tasks: DeployTaskWithProject[];
};

const agentStore = useAgentStore();
const { currentAgent } = storeToRefs(agentStore);

const loading = ref(false);
const keyword = ref('');
const statusFilter = ref<string>('ALL');
const mechanismFilter = ref<string>('ALL');
const deployTasks = ref<DeployTaskWithProject[]>([]);

const detailDialog = ref(false);
const selectedTask = ref<DeployTaskWithProject | null>(null);

const statusOptions = [
  { label: '全部状态', value: 'ALL' },
  { label: '等待中', value: 'PENDING' },
  { label: '部署中', value: 'RUNNING' },
  { label: '成功', value: 'SUCCESS' },
  { label: '失败', value: 'FAILED' },
  { label: '已取消', value: 'CANCELLED' },
];

const mechanismOptions = [
  { label: '全部方式', value: 'ALL' },
  { label: '上传部署', value: 'UPLOAD' },
  { label: '云构建部署', value: 'CLOUD_BUILD' },
];

const filteredTasks = computed(() => {
  const kw = keyword.value.trim().toLowerCase();

  return deployTasks.value.filter((task) => {
    const matchKeyword =
      !kw ||
      task.project_code?.toLowerCase().includes(kw) ||
      task.project_name?.toLowerCase().includes(kw) ||
      task.operator_name?.toLowerCase().includes(kw);

    const matchStatus =
      statusFilter.value === 'ALL' || task.status === statusFilter.value;

    const matchMechanism =
      mechanismFilter.value === 'ALL' || task.deploy_mechanism === mechanismFilter.value;

    return matchKeyword && matchStatus && matchMechanism;
  });
});

const groupedTasks = computed<DeployTaskGroup[]>(() => {
  const map = new Map<string, DeployTaskWithProject[]>();

  for (const task of filteredTasks.value) {
    const key = task.project_code || task.project_id || 'UNKNOWN';
    if (!map.has(key)) {
      map.set(key, []);
    }
    map.get(key)!.push(task);
  }

  return Array.from(map.entries())
    .map(([groupKey, tasks]) => {
      const sortedTasks = [...tasks].sort((a, b) => {
        const aTime = new Date(a.created_at || '').getTime();
        const bTime = new Date(b.created_at || '').getTime();
        return bTime - aTime;
      });

      const first = sortedTasks[0];

      return {
        groupKey,
        project_id: first?.project_id,
        project_code: first?.project_code,
        project_name: first?.project_name,
        taskCount: sortedTasks.length,
        runningCount: sortedTasks.filter((task) =>
          ['RUNNING'].includes(task.status || '')
        ).length,
        latestCreatedAt: first?.created_at,
        tasks: sortedTasks,
      };
    })
    .sort((a, b) => {
      const aTime = new Date(a.latestCreatedAt || '').getTime();
      const bTime = new Date(b.latestCreatedAt || '').getTime();
      return bTime - aTime;
    });
});

const runningTaskCount = computed(() => {
  return filteredTasks.value.filter((task) =>
    ['RUNNING'].includes(task.status || '')
  ).length;
});

watch(
  currentAgent,
  async (agent) => {
    if (agent?.id) {
      await loadDeployTasks();
    } else {
      deployTasks.value = [];
    }
  },
  { immediate: true }
);

async function loadDeployTasks() {
  loading.value = true;
  try {
    deployTasks.value = await provideCurrentAgentProxyApi().fetchDeployTaskList() || [];
  } finally {
    loading.value = false;
  }
}

function openDetail(task: DeployTaskWithProject) {
  selectedTask.value = task;
  detailDialog.value = true;
}

function getStatusText(status?: string) {
  switch (status) {
    case 'PENDING':
      return '等待中';
    case 'RUNNING':
      return '部署中';
    case 'SUCCESS':
      return '成功';
    case 'FAILED':
      return '失败';
    case 'CANCELLED':
      return '已取消';
    default:
      return status || '-';
  }
}

function getMechanismText(value?: string) {
  switch (value) {
    case 'UPLOAD':
      return '上传部署';
    case 'CLOUD_BUILD':
      return '云构建部署';
    default:
      return value || '-';
  }
}

function getTriggerText(value?: string) {
  switch (value) {
    case 'MANUAL':
      return '手动触发';
    case 'SCHEDULED':
      return '定时触发';
    default:
      return value || '-';
  }
}

function formatDuration(durationMs?: number) {
  if (durationMs == null) {
    return '-';
  }

  if (durationMs < 1000) {
    return `${durationMs} ms`;
  }

  const seconds = durationMs / 1000;
  if (seconds < 60) {
    return `${seconds.toFixed(1)} s`;
  }

  const minutes = Math.floor(seconds / 60);
  const remainSeconds = Math.floor(seconds % 60);
  return `${minutes} 分 ${remainSeconds} 秒`;
}

function timeAgo(timestampString?: string) {
  if (!timestampString) {
    return '-';
  }

  const now = new Date();
  const past = new Date(timestampString);
  const diff = now.getTime() - past.getTime();

  if (Number.isNaN(diff) || diff < 0) {
    return '-';
  }

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  if (days > 0) {
    return `${days}天`;
  }

  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  if (hours > 0) {
    return `${hours}小时`;
  }

  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  if (minutes > 0) {
    return `${minutes}分钟`;
  }

  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  return `${seconds}秒`;
}
</script>

<style scoped>
.deploy-task-page {
  min-height: 100%;
  background: #f3f5f8;
}

.page-shell {
  max-width: 1440px;
  margin: 0 auto;
}

.hero-panel {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 18px;
  padding: 22px 24px;
  margin-bottom: 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfcfd 100%);
  border: 1px solid #e5e7eb;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.hero-left {
  min-width: 0;
}

.hero-kicker {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #6b7280;
}

.hero-title {
  margin-top: 6px;
  font-size: 28px;
  line-height: 1.15;
  font-weight: 800;
  color: #111827;
}

.hero-subtitle {
  margin-top: 10px;
  max-width: 620px;
  font-size: 14px;
  line-height: 1.7;
  color: #6b7280;
}

.hero-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}

.hero-stat-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hero-stat-card {
  min-width: 128px;
  padding: 14px 16px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
}

.hero-stat-label {
  font-size: 12px;
  color: #6b7280;
}

.hero-stat-value {
  margin-top: 6px;
  font-size: 24px;
  font-weight: 800;
  color: #111827;
}

.refresh-btn {
  height: 42px;
  padding: 0 18px;
  border-radius: 12px;
  background: #111827 !important;
  color: #ffffff !important;
  box-shadow: none;
}

.toolbar-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 16px 18px;
  margin-bottom: 14px;
  border-radius: 16px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.03);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-search {
  min-width: 340px;
}

.toolbar-select {
  width: 160px;
}

.toolbar-summary {
  font-size: 13px;
  color: #6b7280;
}

.toolbar-summary span {
  font-weight: 800;
  color: #111827;
}

.content-panel {
  padding: 12px;
  border-radius: 18px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.03);
}

.state-panel {
  min-height: 340px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #64748b;
}

.state-icon {
  color: #cbd5e1;
}

.state-title {
  margin-top: 14px;
  font-size: 17px;
  font-weight: 700;
  color: #334155;
}

.state-desc {
  margin-top: 8px;
  font-size: 14px;
  color: #94a3b8;
}

.project-group-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  align-items: start;
}

.project-group-card {
  border-radius: 16px;
  background: #fbfcfd;
  border: 1px solid #e5e7eb;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.03);
  overflow: hidden;
}

.project-group-header {
  padding: 16px 16px 14px;
  border-bottom: 1px solid #edf0f2;
  background: #ffffff;
}

.project-group-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.project-group-title {
  font-size: 17px;
  line-height: 1.3;
  font-weight: 800;
  color: #111827;
}

.project-running-pill {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  color: #92400e;
  background: #fff7ed;
  border: 1px solid #fed7aa;
}

.project-group-meta {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 12px;
  color: #6b7280;
}

.project-code-chip {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 9px;
  border-radius: 999px;
  background: #f3f4f6;
  color: #374151;
  font-weight: 700;
}

.project-meta-separator {
  color: #cbd5e1;
}

.task-mini-list {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 430px;
  overflow-y: auto;
}

.task-mini-list::-webkit-scrollbar {
  width: 8px;
}

.task-mini-list::-webkit-scrollbar-track {
  background: transparent;
}

.task-mini-list::-webkit-scrollbar-thumb {
  background: rgba(107, 114, 128, 0.24);
  border-radius: 999px;
}

.task-mini-list::-webkit-scrollbar-thumb:hover {
  background: rgba(107, 114, 128, 0.38);
}

.task-mini-card {
  border-radius: 14px;
  background: #ffffff;
  border: 1px solid #e7eaee;
  padding: 12px 12px 10px;
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
}

.task-mini-card:hover {
  transform: translateY(-1px);
  border-color: #cfd6de;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}

.task-mini-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.task-status-pill {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 11px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid transparent;
}

.task-status-pill.is-pending {
  color: #475569;
  background: #f1f5f9;
  border-color: #e2e8f0;
}

.task-status-pill.is-running {
  color: #92400e;
  background: #fff7ed;
  border-color: #fed7aa;
}

.task-status-pill.is-success {
  color: #166534;
  background: #ecfdf3;
  border-color: #bbf7d0;
}

.task-status-pill.is-failed {
  color: #b42318;
  background: #fff1f3;
  border-color: #fecdd3;
}

.task-status-pill.is-cancelled {
  color: #374151;
  background: #f3f4f6;
  border-color: #e5e7eb;
}

.task-mini-duration {
  font-size: 12px;
  font-weight: 700;
  color: #111827;
  white-space: nowrap;
}

.task-mini-body {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-mini-line {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-mini-label {
  font-size: 11px;
  color: #9ca3af;
}

.task-mini-value {
  font-size: 12px;
  color: #111827;
  font-weight: 600;
  line-height: 1.5;
  word-break: break-word;
}

.task-mini-sub {
  color: #6b7280;
  font-size: 11px;
  font-weight: 400;
}

.task-mini-error {
  margin-top: 10px;
  padding: 8px 10px;
  border-radius: 12px;
  background: #fff5f5;
  border: 1px solid #ffe0e6;
  color: #7f1d1d;
  font-size: 11px;
  line-height: 1.45;
}

.task-mini-footer {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.task-mini-link {
  font-size: 11px;
  font-weight: 700;
  color: #111827;
  white-space: nowrap;
}

.ellipsis-2 {
  overflow: hidden;
  display: -webkit-box;
}

.detail-dialog-card {
  width: 920px;
  max-width: 92vw;
  border-radius: 20px;
  background: #ffffff;
}

.dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 22px 18px;
}

.dialog-overline {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #6b7280;
}

.dialog-title {
  margin-top: 6px;
  font-size: 22px;
  font-weight: 800;
  color: #111827;
}

.dialog-subtitle {
  margin-top: 6px;
  color: #6b7280;
  font-size: 14px;
}

.dialog-body {
  max-height: 72vh;
  overflow-y: auto;
  padding: 20px 22px 24px;
}

.detail-panel-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 16px;
}

.detail-panel-item {
  min-width: 0;
  padding: 14px 16px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
}

.detail-panel-label {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 6px;
}

.detail-panel-value {
  font-size: 14px;
  color: #111827;
  line-height: 1.6;
  font-weight: 600;
  word-break: break-word;
}

.detail-block {
  margin-top: 18px;
}

.detail-block-title {
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 800;
  color: #374151;
}

.detail-alert {
  border-radius: 14px;
  padding: 14px 16px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-alert.error {
  background: #fff5f5;
  border: 1px solid #ffe0e6;
  color: #7f1d1d;
}

.detail-code-block {
  margin: 0;
  padding: 16px;
  border-radius: 14px;
  background: #111827;
  color: #e5e7eb;
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
}

.break-all {
  word-break: break-all;
}

:deep(.q-field--outlined .q-field__control) {
  border-radius: 12px;
  background: #fff;
}

:deep(.q-field__native),
:deep(.q-field__input) {
  font-size: 14px;
}

:deep(.q-dialog__inner > div) {
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.16);
}

@media (max-width: 1360px) {
  .project-group-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1100px) {
  .hero-panel,
  .toolbar-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-right {
    justify-content: space-between;
  }

  .detail-panel-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .deploy-task-page {
    padding: 12px !important;
  }

  .hero-panel,
  .toolbar-panel,
  .content-panel {
    border-radius: 16px;
  }

  .hero-title {
    font-size: 24px;
  }

  .hero-right,
  .hero-stat-group {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-search,
  .toolbar-select {
    width: 100%;
    min-width: 0;
  }

  .toolbar-left {
    width: 100%;
  }

  .project-group-list,
  .detail-panel-grid {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }

  .dialog-body,
  .dialog-header {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>