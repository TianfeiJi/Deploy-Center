<template>
  <q-card class="java-project-card">
    <q-card-section class="card-header">
      <div class="project-header">
        <div class="project-header-left">
          <div class="project-title" :title="javaProject.project_name || '-'">
            {{ javaProject.project_name || '-' }}
          </div>

          <div class="project-submeta">
            <span class="project-submeta-type">Java</span>
            <span v-if="javaProject.project_group" class="project-submeta-divider">·</span>
            <span v-if="javaProject.project_group" class="project-submeta-group">
              {{ javaProject.project_group }}
            </span>
          </div>
        </div>

        <div class="project-header-right">
          <div class="runtime-status-inline">
            <template v-if="containerStatus === 'Checking'">
              <q-spinner color="grey-5" size="16px" />
            </template>
            <template v-else-if="containerStatus === 'Unknown'">
              <el-tag type="warning" effect="light" round>Status Unknown</el-tag>
            </template>
            <template v-else>
              <el-tag
                :closable="false"
                :type="getContainerStatusTagType(containerStatus)"
                effect="light"
                round
              >
                {{ containerStatus }}
              </el-tag>
            </template>
          </div>

          <div class="project-deploy-text">
            最近部署：{{ getDeployText(javaProject.last_deployed_at) }}
          </div>
        </div>
      </div>

      <div class="info-list q-mt-sm">
        <div class="info-row">
          <div class="info-key">容器名称</div>
          <div
            class="info-main-value hover-copy"
            :title="javaProject.container_name || '-'"
            @click.stop="copyValue(javaProject.container_name)"
          >
            {{ javaProject.container_name || '-' }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">镜像名称</div>
          <div
            class="info-value hover-copy"
            :title="dockerImageText"
            @click.stop="copyValue(dockerImageText)"
          >
            {{ dockerImageText }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">端口映射</div>
          <div class="info-value" :title="portMappingText">
            {{ portMappingText }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">Docker 网络</div>
          <div
            class="info-value hover-copy"
            :title="javaProject.network || '-'"
            @click.stop="copyValue(javaProject.network)"
          >
            {{ javaProject.network || '-' }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">宿主机路径</div>
          <div
            class="info-value hover-copy multi-line-value"
            :title="javaProject.host_project_path || '-'"
            @click.stop="copyValue(javaProject.host_project_path)"
          >
            {{ javaProject.host_project_path || '-' }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">容器内路径</div>
          <div
            class="info-value hover-copy multi-line-value"
            :title="javaProject.container_project_path || '-'"
            @click.stop="copyValue(javaProject.container_project_path)"
          >
            {{ javaProject.container_project_path || '-' }}
          </div>
        </div>
      </div>
    </q-card-section>

    <q-card-actions class="card-actions split-actions">
      <div class="actions-left">
        <q-btn flat dense color="primary" label="详情" @click="viewJavaProjectDetail" />
      </div>

      <div class="actions-right">
        <q-btn flat dense color="positive" label="部署" @click="goToDeployConsole(javaProject.id)" />
      </div>
    </q-card-actions>
  </q-card>

  <q-dialog v-model="isViewDetailDialogOpen">
    <q-card style="width: 100%">
      <q-card-section>
        <q-btn icon="close" flat round dense class="float-right" v-close-popup />
        <div class="text-h6">项目详情</div>
      </q-card-section>
      <q-separator />
      <q-card-section>
        <el-table :data="tableData" border>
          <el-table-column prop="key" label="字段" width="170" />
          <el-table-column prop="label" label="注释" width="130" />
          <el-table-column label="值">
            <template #default="scope">
              <div v-if="!isEditing || !scope.row.editable">{{ scope.row.value }}</div>
              <el-input v-else v-model="scope.row.value" placeholder="请输入内容" clearable />
            </template>
          </el-table-column>
        </el-table>
      </q-card-section>
      <q-separator />
      <q-card-actions>
        <q-btn flat color="negative" label="删除" @click="isSecondConfirmDeleteDialogOpen = true" />
        <q-space />
        <q-btn v-if="isEditing" flat color="negative" label="取消" @click="cancelEdit" />
        <q-btn v-if="isEditing" flat color="positive" label="保存" @click="saveEdit" />
        <q-btn v-else flat color="secondary" label="编辑" @click="startEdit" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog v-model="isSecondConfirmDeleteDialogOpen">
    <q-card style="width: 30%">
      <q-card-section class="text-h6">危险操作</q-card-section>
      <q-card-section>
        <div style="color: red; text-indent: 1rem">请输入“确定删除”以进行删除操作。</div>
        <q-input v-model="confirmText" />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn label="确定" @click="handleSecondConfirmDelete" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { Notify, copyToClipboard } from 'quasar';
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory';
import { formatDate } from 'src/utils/dateFormatter';
import { JavaProject } from 'src/types/Project.types';
import { UpdateJavaProjectRequestDto } from 'src/types/dto/UpdateJavaProjectRequestDto';
import { useRouter } from 'vue-router';

const router = useRouter();

const props = defineProps<{ javaProject: JavaProject }>();

const isViewDetailDialogOpen = ref(false);
const isSecondConfirmDeleteDialogOpen = ref(false);
const confirmText = ref('');
const tableData = ref<{ label: string; value: string; key: string; editable: boolean }[]>([]);
const containerStatus = ref('Checking');
const isEditing = ref(false);

const goToDeployConsole = (id: string) => {
  if (!id) return;
  router.push({
    path: `/project/deploy/${id}`,
  });
};

const dockerImageText = computed(() => {
  return `${props.javaProject.docker_image_name || '-'}:${props.javaProject.docker_image_tag || 'latest'}`;
});

const portMappingText = computed(() => {
  return `${props.javaProject.external_port || '-'} → ${props.javaProject.internal_port || '-'}`;
});

const getDeployText = (time?: any) => {
  if (!time) return '未部署';
  try {
    const now = Date.now();
    const t = new Date(time).getTime();
    if (Number.isNaN(t)) return '-';
    const diff = Math.floor((now - t) / 1000);
    if (diff < 60) return '刚刚';
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
    return `${Math.floor(diff / 86400)}天前`;
  } catch {
    return '未部署';
  }
};

const copyValue = async (text?: string) => {
  const value = text?.trim();
  if (!value || value === '-') return;

  try {
    await copyToClipboard(value);
    Notify.create({
      type: 'positive',
      message: '复制成功',
      position: 'top',
      timeout: 1000,
    });
  } catch {
    Notify.create({
      type: 'negative',
      message: '复制失败',
      position: 'top',
      timeout: 1000,
    });
  }
};

const viewJavaProjectDetail = () => {
  tableData.value = [
    { label: '项目Id', key: 'id', value: props.javaProject.id ?? '', editable: false },
    { label: '项目代号', key: 'project_code', value: props.javaProject.project_code ?? '', editable: true },
    { label: '项目名称', key: 'project_name', value: props.javaProject.project_name ?? '', editable: true },
    { label: '项目分组', key: 'project_group', value: props.javaProject.project_group ?? '', editable: true },
    { label: 'Docker 镜像名称', key: 'docker_image_name', value: props.javaProject.docker_image_name ?? '', editable: true },
    { label: 'Docker 镜像标签', key: 'docker_image_tag', value: props.javaProject.docker_image_tag ?? '', editable: true },
    { label: '容器名称', key: 'container_name', value: props.javaProject.container_name ?? '', editable: true },
    { label: '外部端口', key: 'external_port', value: String(props.javaProject.external_port ?? ''), editable: true },
    { label: '内部端口', key: 'internal_port', value: String(props.javaProject.internal_port ?? ''), editable: true },
    { label: '宿主机路径', key: 'host_project_path', value: props.javaProject.host_project_path ?? '', editable: true },
    { label: '容器内路径', key: 'container_project_path', value: props.javaProject.container_project_path ?? '', editable: true },
    { label: '访问地址', key: 'access_url', value: props.javaProject.access_url ?? '', editable: true },
    { label: 'Git地址', key: 'git_repository', value: props.javaProject.git_repository ?? '', editable: true },
    { label: 'JDK版本', key: 'jdk_version', value: String(props.javaProject.jdk_version ?? ''), editable: false },
    { label: '创建时间', key: 'created_at', value: formatDate(props.javaProject.created_at), editable: false },
    { label: '更新时间', key: 'updated_at', value: formatDate(props.javaProject.updated_at), editable: false },
    { label: '最近部署时间', key: 'last_deployed_at', value: formatDate(props.javaProject.last_deployed_at), editable: false },
  ];
  isEditing.value = false;
  isViewDetailDialogOpen.value = true;
};

const fetchContainerStatus = async () => {
  containerStatus.value = 'Checking';
  try {
    const res = await provideCurrentAgentProxyApi().fetchDockerContainerStatus(
      props.javaProject.container_name || ''
    );
    containerStatus.value = res?.container_status || 'Unknown';
  } catch {
    containerStatus.value = 'Unknown';
  }
};

const getContainerStatusTagType = (status: string) => {
  const s = status.toLowerCase();
  if (s.startsWith('up')) return 'success';
  if (s.startsWith('exited (0)')) return 'info';
  if (s.startsWith('exited')) return 'danger';
  if (s.startsWith('restarting') || s.startsWith('paused')) return 'warning';
  if (s.startsWith('created')) return 'info';
  if (s.startsWith('dead')) return 'danger';
  return 'info';
};

const startEdit = () => {
  isEditing.value = true;
};

const cancelEdit = () => {
  isEditing.value = false;
};

const saveEdit = async () => {
  try {
    await provideCurrentAgentProxyApi().updateJavaProject({
      id: props.javaProject.id,
    } as UpdateJavaProjectRequestDto);
    Notify.create({ type: 'positive', message: '保存成功', position: 'top' });
    isViewDetailDialogOpen.value = false;
    isEditing.value = false;
  } catch {
    Notify.create({ type: 'negative', message: '保存失败', position: 'top' });
  }
};

const handleSecondConfirmDelete = async () => {
  if (confirmText.value !== '确定删除') {
    Notify.create({ type: 'negative', message: '请输入确认文字', position: 'top' });
    return;
  }
  try {
    await provideCurrentAgentProxyApi().deleteJavaProject(props.javaProject.id);
    Notify.create({ type: 'positive', message: '删除成功', position: 'top' });
    isSecondConfirmDeleteDialogOpen.value = false;
    isViewDetailDialogOpen.value = false;
  } catch {
    Notify.create({ type: 'negative', message: '删除失败', position: 'top' });
  }
  confirmText.value = '';
};

onMounted(() => {
  fetchContainerStatus();
});
</script>

<style scoped>
.java-project-card {
  width: 100%;
  min-height: 418px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 20px;
  overflow: visible;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
  transition: all 0.22s ease;
}

.java-project-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 44px rgba(15, 23, 42, 0.1);
}

.card-header {
  padding: 18px 18px 10px;
}

.project-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding-bottom: 4px;
}

.project-header-left {
  flex: 1;
  min-width: 0;
}

.project-header-right {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: flex-start;
  gap: 6px;
  padding-top: 2px;
}

.project-title {
  font-size: 20px;
  font-weight: 800;
  color: #111827;
  line-height: 1.35;
  letter-spacing: -0.01em;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-submeta {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.project-submeta-type,
.project-submeta-group {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
}

.project-submeta-divider {
  font-size: 20px;
  font-weight: 600;
  color: #cbd5e1;
}

.runtime-status-inline {
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
}

.project-deploy-text {
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.2;
  white-space: nowrap;
}

.info-list {
  margin-top: 10px;
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  transition: background 0.18s ease;
}

.info-row + .info-row {
  border-top: 1px dashed #e5e7eb;
}

.info-row:hover {
  background: rgba(248, 250, 252, 0.55);
}

.info-key {
  width: 82px;
  flex-shrink: 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
  white-space: nowrap;
}

.info-main-value,
.info-value {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #334155;
  word-break: break-all;
}

.info-main-value {
  font-weight: 600;
  color: #1f2937;
}

.multi-line-value {
  white-space: normal;
  overflow: visible;
  text-overflow: unset;
}

.hover-copy {
  cursor: pointer;
  position: relative;
  transition: color 0.18s ease;
}

.hover-copy:hover {
  color: #2563eb;
}

.hover-copy::after {
  content: "点此复制";
  position: absolute;
  right: 0;
  top: calc(100% + 6px);
  z-index: 20;
  padding: 6px 8px;
  font-size: 12px;
  line-height: 1;
  color: #f8fafc;
  background: rgba(15, 23, 42, 0.92);
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.18);
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transform: translateY(4px);
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.hover-copy:hover::after {
  opacity: 1;
  transform: translateY(0);
}

.card-actions.split-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px 14px;
  gap: 12px;
}

.actions-left,
.actions-right {
  display: flex;
  align-items: center;
}

:deep(.card-actions .q-btn) {
  border-radius: 12px;
  transition: all 0.18s ease;
}

:deep(.card-actions .q-btn:hover) {
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
}

:deep(.el-tag) {
  border-radius: 999px;
  font-weight: 600;
  border: none;
}

@media (max-width: 640px) {
  .project-header {
    gap: 10px;
  }

  .project-title {
    font-size: 18px;
  }

  .project-header-right {
    gap: 4px;
  }

  .info-key {
    width: 74px;
  }
}
</style>