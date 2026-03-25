<template>
  <q-card class="python-project-card">
    <q-card-section class="card-header">
      <div class="project-header">
        <div class="project-header-left">
          <div class="project-title" :title="pythonProject.project_name || '-'">
            {{ pythonProject.project_name || '-' }}
          </div>

          <div class="project-submeta">
            <span class="project-submeta-type">Python</span>
          </div>
        </div>

        <div class="project-header-right">
          <div class="runtime-status-inline">
            <template v-if="isCheckingStatus">
              <q-spinner color="grey-5" size="16px" />
            </template>
            <template v-else>
              <el-tag :type="statusMeta.tagType" effect="light" round>
                {{ statusMeta.label }}
              </el-tag>
            </template>
          </div>

          <div class="project-deploy-text">
            最近部署：{{ getDeployText(pythonProject.last_deployed_at) }}
          </div>
        </div>
      </div>

      <div class="info-list q-mt-sm">
        <div class="info-row" @click="copyValue(pythonProject.container_name)">
          <div class="info-key">容器名称</div>
          <div class="info-main-value hover-copy" :title="pythonProject.container_name || '-'">
            {{ pythonProject.container_name || '-' }}
          </div>
        </div>

        <div class="info-row" @click="copyValue(dockerImageText)">
          <div class="info-key">镜像名称</div>
          <div class="info-value hover-copy" :title="dockerImageText">
            {{ dockerImageText }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-key">端口映射</div>
          <div class="info-value" :title="portMappingText">
            {{ portMappingText }}
          </div>
        </div>

        <div class="info-row" @click="copyValue(pythonProject.network)">
          <div class="info-key">Docker 网络</div>
          <div class="info-value hover-copy" :title="pythonProject.network || '-'">
            {{ pythonProject.network || '-' }}
          </div>
        </div>

        <div
          v-if="pythonProject.access_url"
          class="info-row info-row-link"
          @click="openAccessUrl(pythonProject.access_url)"
        >
          <div class="info-key">访问地址</div>
          <div class="info-value access-url-link" :title="pythonProject.access_url">
            {{ pythonProject.access_url }}
          </div>
        </div>

        <div class="info-row" @click="copyValue(pythonProject.host_project_path)">
          <div class="info-key">宿主机路径</div>
          <div class="info-value hover-copy multi-line-value" :title="pythonProject.host_project_path || '-'">
            {{ pythonProject.host_project_path || '-' }}
          </div>
        </div>

        <div class="info-row" @click="copyValue(pythonProject.container_project_path)">
          <div class="info-key">容器内路径</div>
          <div class="info-value hover-copy multi-line-value" :title="pythonProject.container_project_path || '-'">
            {{ pythonProject.container_project_path || '-' }}
          </div>
        </div>
      </div>
    </q-card-section>

    <q-card-actions align="right" class="card-actions">
      <q-btn flat color="primary" label="详情" @click="viewPythonProjectDetail" />

      <q-btn
        flat
        dense
        color="info"
        icon="cloud"
        label="云构建部署"
        @click="openCloudBuildDeployDialog"
      />

      <q-btn
        flat
        dense
        color="positive"
        icon="cloud_upload"
        label="上传部署"
        :loading="isPreparingDeploy"
        @click="openUploadDeployDialog"
      />
    </q-card-actions>
  </q-card>

  <!-- 详情对话框 -->
  <q-dialog v-model="isViewDetailDialogOpen">
    <q-card class="detail-dialog-card">
      <q-card-section class="row items-center">
        <div class="text-h6">项目详情</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-separator />

      <q-card-section class="detail-table-section">
        <el-table
          :data="tableData"
          border
          stripe
          style="width: 100%"
          max-height="60vh"
        >
          <el-table-column prop="key" label="字段" width="180" />
          <el-table-column prop="label" label="说明" width="140" />
          <el-table-column label="值" min-width="240">
            <template #default="scope">
              <div v-if="!isEditing || !scope.row.editable" class="table-cell-value">
                {{ scope.row.value || '-' }}
              </div>

              <el-input
                v-else
                v-model="scope.row.value"
                placeholder="请输入内容"
                clearable
              />
            </template>
          </el-table-column>
        </el-table>
      </q-card-section>

      <q-separator />

      <q-card-actions class="q-px-md q-py-sm">
        <q-btn
          flat
          color="negative"
          label="删除"
          @click="isSecondConfirmDeleteDialogOpen = true"
        />

        <q-space />

        <q-btn
          v-if="isEditing"
          flat
          color="grey-7"
          label="取消"
          :disable="isSaving"
          @click="cancelEdit"
        />

        <q-btn
          v-if="isEditing"
          unelevated
          color="positive"
          label="保存"
          icon="save"
          :loading="isSaving"
          @click="saveEdit"
        />

        <q-btn
          v-else
          flat
          color="secondary"
          label="编辑"
          @click="startEdit"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <!-- 上传部署对话框 -->
  <q-dialog v-model="isUploadDeployDialogOpen">
    <q-card class="deploy-dialog-card">
      <q-card-section class="row items-center">
        <div class="text-h5">上传部署</div>
        <q-space />
        <q-btn icon="close" flat round dense :disable="isDeploying" v-close-popup />
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="deploy-project-name">
          {{ pythonProject.project_name }}
        </div>
      </q-card-section>

      <q-card-section>
        <div class="section-title">上传 ZIP 文件</div>

        <el-upload
          ref="uploadRef"
          drag
          :auto-upload="false"
          accept=".zip"
          :before-upload="handleBeforeUpload"
          :on-change="handleFileChange"
          :file-list="fileList"
          :limit="1"
          :disabled="isDeploying"
        >
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>

          <template #tip>
            <div class="el-upload__tip upload-tip">
              只能上传 .zip 文件，且一次仅允许一个文件
            </div>
          </template>
        </el-upload>

        <div class="q-mt-md">
          <el-progress
            v-if="uploadProgress > 0"
            :percentage="uploadProgress"
            :text-inside="true"
            :stroke-width="14"
            status="success"
          />
        </div>

        <div
          v-if="uploadProgress === 100 && !isDeploying"
          class="deploy-success-tip"
        >
          上传完成
        </div>
      </q-card-section>

      <q-card-section>
        <div class="section-title">Dockerfile 内容（可选）</div>
        <q-input
          v-model="dockerfileContent"
          type="textarea"
          outlined
          rows="12"
          class="mono-input"
          :disable="isDeploying"
        />
      </q-card-section>

      <q-card-section>
        <div class="section-title">Docker 命令（可选）</div>
        <q-input
          v-model="dockerCommand"
          type="textarea"
          outlined
          rows="8"
          class="mono-input"
          :disable="isDeploying"
        />
      </q-card-section>

      <q-card-actions align="right" class="q-px-md q-pb-md">
        <q-btn
          flat
          label="取消"
          :disable="isDeploying"
          v-close-popup
        />
        <q-btn
          flat
          label="开始部署"
          color="positive"
          :disable="!fileList.length"
          :loading="isDeploying"
          @click="handleUploadDeploy"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <!-- 二次确认删除对话框 -->
  <q-dialog v-model="isSecondConfirmDeleteDialogOpen" persistent>
    <q-card class="delete-dialog-card">
      <q-card-section class="text-h6 text-negative">
        危险操作
      </q-card-section>

      <q-card-section>
        <div class="delete-warning-text">
          你正在删除项目：
          <strong>{{ pythonProject.project_name || '-' }}</strong>
        </div>
        <div class="delete-warning-subtext q-mt-sm">
          请输入“确定删除”以继续操作。
        </div>

        <q-input
          v-model="confirmText"
          outlined
          class="q-mt-md"
          placeholder="请输入：确定删除"
          :disable="isDeleting"
        />
      </q-card-section>

      <q-card-actions align="right" class="q-px-md q-pb-md">
        <q-btn
          flat
          label="取消"
          :disable="isDeleting"
          v-close-popup
        />
        <q-btn
          unelevated
          color="negative"
          label="确定删除"
          icon="delete_forever"
          :loading="isDeleting"
          @click="handleSecondConfirmDelete"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import type { AxiosProgressEvent } from 'axios';
import { Notify, copyToClipboard } from 'quasar';
import { formatDate } from 'src/utils/dateFormatter';
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory';
import type { PythonProject } from 'src/types/Project.types';
import type { UpdatePythonProjectRequestDto } from 'src/types/dto/UpdatePythonProjectRequestDto';

type DetailRow = {
  label: string;
  value: string;
  key: string;
  editable: boolean;
};

const props = defineProps<{
  pythonProject: PythonProject;
}>();

const agentProxyApi = provideCurrentAgentProxyApi();

const isViewDetailDialogOpen = ref(false);
const isUploadDeployDialogOpen = ref(false);
const isCloudBuildDeployDialogOpen = ref(false);
const isSecondConfirmDeleteDialogOpen = ref(false);

const isCheckingStatus = ref(true);
const isEditing = ref(false);
const isSaving = ref(false);
const isDeleting = ref(false);
const isPreparingDeploy = ref(false);
const isDeploying = ref(false);

const dockerfileContent = ref('');
const dockerCommand = ref('');
const confirmText = ref('');
const uploadProgress = ref(0);
const fileList = ref<any[]>([]);

const containerStatus = ref('Unknown');
const tableData = ref<DetailRow[]>([]);
const originalTableDataSnapshot = ref<DetailRow[]>([]);

const dockerImageText = computed(() => {
  return `${props.pythonProject.docker_image_name || '-'}:${props.pythonProject.docker_image_tag || 'latest'}`;
});

const portMappingText = computed(() => {
  return `${props.pythonProject.external_port || '-'} → ${props.pythonProject.internal_port || '-'}`;
});

const formatDateSafe = (value: any): string => {
  if (!value) return '-';
  try {
    return formatDate(value);
  } catch {
    return String(value);
  }
};

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
    if (diff < 86400 * 7) return `${Math.floor(diff / 86400)}天前`;

    return formatDate(time);
  } catch {
    return '-';
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

const openAccessUrl = (url?: string) => {
  const value = url?.trim();
  if (!value || value === '-') return;
  window.open(value, '_blank', 'noopener,noreferrer');
};

const buildDetailTableData = (): DetailRow[] => {
  return [
    { label: '项目ID', key: 'id', value: String(props.pythonProject.id ?? ''), editable: false },
    { label: '项目代号', key: 'project_code', value: String(props.pythonProject.project_code ?? ''), editable: true },
    { label: '项目名称', key: 'project_name', value: String(props.pythonProject.project_name ?? ''), editable: true },
    { label: '项目分组', key: 'project_group', value: String(props.pythonProject.project_group ?? ''), editable: true },
    { label: '项目类型', key: 'project_type', value: String(props.pythonProject.project_type ?? ''), editable: false },
    { label: '镜像名称', key: 'docker_image_name', value: String(props.pythonProject.docker_image_name ?? ''), editable: true },
    { label: '镜像标签', key: 'docker_image_tag', value: String(props.pythonProject.docker_image_tag ?? ''), editable: true },
    { label: '容器名称', key: 'container_name', value: String(props.pythonProject.container_name ?? ''), editable: true },
    { label: '外部端口', key: 'external_port', value: String(props.pythonProject.external_port ?? ''), editable: true },
    { label: '内部端口', key: 'internal_port', value: String(props.pythonProject.internal_port ?? ''), editable: true },
    { label: 'Docker网络', key: 'network', value: String(props.pythonProject.network ?? ''), editable: false },
    { label: 'Python版本', key: 'python_version', value: String(props.pythonProject.python_version ?? ''), editable: false },
    { label: '宿主机路径', key: 'host_project_path', value: String(props.pythonProject.host_project_path ?? ''), editable: true },
    { label: '容器内路径', key: 'container_project_path', value: String(props.pythonProject.container_project_path ?? ''), editable: true },
    { label: '访问地址', key: 'access_url', value: String(props.pythonProject.access_url ?? ''), editable: true },
    { label: 'Git地址', key: 'git_repository', value: String(props.pythonProject.git_repository ?? ''), editable: true },
    { label: '创建时间', key: 'created_at', value: formatDateSafe(props.pythonProject.created_at), editable: false },
    { label: '更新时间', key: 'updated_at', value: formatDateSafe(props.pythonProject.updated_at), editable: false },
    { label: '最近部署', key: 'last_deployed_at', value: formatDateSafe(props.pythonProject.last_deployed_at), editable: false },
  ];
};

const statusMeta = computed(() => {
  const raw = String(containerStatus.value || '').toLowerCase();

  if (!raw || raw === 'unknown') {
    return {
      label: 'Status Unknown',
      tagType: 'warning',
    };
  }

  if (raw.startsWith('up')) {
    return {
      label: containerStatus.value,
      tagType: 'success',
    };
  }

  if (raw.startsWith('exited (0)')) {
    return {
      label: containerStatus.value,
      tagType: 'info',
    };
  }

  if (raw.startsWith('exited')) {
    return {
      label: containerStatus.value,
      tagType: 'danger',
    };
  }

  if (raw.startsWith('restarting')) {
    return {
      label: containerStatus.value,
      tagType: 'warning',
    };
  }

  if (raw.startsWith('paused')) {
    return {
      label: containerStatus.value,
      tagType: 'warning',
    };
  }

  if (raw.startsWith('created')) {
    return {
      label: containerStatus.value,
      tagType: 'info',
    };
  }

  if (raw.startsWith('dead')) {
    return {
      label: containerStatus.value,
      tagType: 'danger',
    };
  }

  if (raw.includes('not found')) {
    return {
      label: 'Container Not Found',
      tagType: 'danger',
    };
  }

  if (raw.includes('awaiting deployment')) {
    return {
      label: 'Awaiting Deployment',
      tagType: 'info',
    };
  }

  return {
    label: containerStatus.value,
    tagType: 'info',
  };
});

const fetchContainerStatus = async () => {
  if (!props.pythonProject.container_name) {
    containerStatus.value = 'Unknown';
    isCheckingStatus.value = false;
    return;
  }

  isCheckingStatus.value = true;

  try {
    const response = await agentProxyApi.fetchDockerContainerStatus(
      String(props.pythonProject.container_name)
    );
    containerStatus.value = response?.container_status || 'Unknown';
  } catch {
    containerStatus.value = 'Unknown';
  } finally {
    isCheckingStatus.value = false;
  }
};

const viewPythonProjectDetail = () => {
  const rows = buildDetailTableData();
  tableData.value = rows;
  originalTableDataSnapshot.value = JSON.parse(JSON.stringify(rows));
  isEditing.value = false;
  isViewDetailDialogOpen.value = true;
};

const startEdit = () => {
  originalTableDataSnapshot.value = JSON.parse(JSON.stringify(tableData.value));
  isEditing.value = true;
};

const cancelEdit = () => {
  tableData.value = JSON.parse(JSON.stringify(originalTableDataSnapshot.value));
  isEditing.value = false;
};

const saveEdit = async () => {
  isSaving.value = true;

  try {
    const updateData: Partial<UpdatePythonProjectRequestDto> = {
      id: props.pythonProject.id,
    };

    const skipKeys = ['created_at', 'updated_at', 'last_deployed_at', 'project_type'];
    const numberFields = ['external_port', 'internal_port'];

    tableData.value.forEach((item) => {
      if (skipKeys.includes(item.key)) return;

      const rawValue = item.value ?? '';

      if (numberFields.includes(item.key)) {
        updateData[item.key as keyof UpdatePythonProjectRequestDto] =
          rawValue === '' ? undefined as any : Number(rawValue) as any;
      } else {
        updateData[item.key as keyof UpdatePythonProjectRequestDto] = rawValue as any;
      }
    });

    await agentProxyApi.updatePythonProject(updateData as UpdatePythonProjectRequestDto);

    Notify.create({
      type: 'positive',
      message: '保存成功',
      position: 'top',
    });

    isEditing.value = false;
    isViewDetailDialogOpen.value = false;
  } catch (error: any) {
    Notify.create({
      type: 'negative',
      message: `保存失败${error?.message ? '：' + error.message : ''}`,
      position: 'top',
    });
  } finally {
    isSaving.value = false;
  }
};

const resetDeployDialogState = () => {
  fileList.value = [];
  uploadProgress.value = 0;
  dockerfileContent.value = '';
  dockerCommand.value = '';
  isDeploying.value = false;
};

const openUploadDeployDialog = async () => {
  isPreparingDeploy.value = true;
  resetDeployDialogState();

  try {
    isUploadDeployDialogOpen.value = true;

    const [dockerfileConfig, dockerCommandConfig] = await Promise.all([
      agentProxyApi.fetchSystemConfig('default_python_dockerfile_template'),
      agentProxyApi.fetchSystemConfig('default_python_dockercommand_template'),
    ]);

    const [renderedDockerfile, renderedDockerCommand] = await Promise.all([
      agentProxyApi.renderTemplateContent(
        props.pythonProject.id,
        dockerfileConfig.config_value
      ),
      agentProxyApi.renderTemplateContent(
        props.pythonProject.id,
        dockerCommandConfig.config_value
      ),
    ]);

    dockerfileContent.value = renderedDockerfile || '';
    dockerCommand.value = renderedDockerCommand || '';
  } catch (error: any) {
    Notify.create({
      type: 'negative',
      message: `初始化部署信息失败${error?.message ? '：' + error.message : ''}`,
      position: 'top',
    });
  } finally {
    isPreparingDeploy.value = false;
  }
};

const openCloudBuildDeployDialog = () => {
  isCloudBuildDeployDialogOpen.value = true;
  Notify.create({
    message: '尚未实现，敬请期待',
    type: 'warning',
    position: 'top',
  });
};

const handleBeforeUpload = (file: File): boolean => {
  const isZip = file.type === 'application/zip' || file.name.toLowerCase().endsWith('.zip');

  if (!isZip) {
    Notify.create({
      type: 'negative',
      message: '只能上传 .zip 文件',
      position: 'top',
    });
    return false;
  }

  return true;
};

const handleFileChange = (file: any, files: any[]) => {
  if (files?.length) {
    fileList.value = [files[files.length - 1]];
  } else if (file) {
    fileList.value = [file];
  } else {
    fileList.value = [];
  }
};

const handleUploadDeploy = async () => {
  const file = fileList.value[0]?.raw;

  if (!file) {
    Notify.create({
      type: 'negative',
      message: '请选择一个 ZIP 文件',
      position: 'top',
    });
    return;
  }

  isDeploying.value = true;
  uploadProgress.value = 0;

  try {
    const formData = new FormData();
    formData.append('id', String(props.pythonProject.id));
    formData.append('file', file);
    formData.append('dockerfile_content', dockerfileContent.value || '');
    formData.append('dockercommand_content', dockerCommand.value || '');

    const response = await agentProxyApi.deployPythonProject(formData, {
      onUploadProgress: (event: AxiosProgressEvent) => {
        if (event.total) {
          uploadProgress.value = Math.round((event.loaded * 100) / event.total);
        }
      },
    });

    if (response?.code === 200) {
      uploadProgress.value = 100;

      Notify.create({
        type: 'positive',
        message: '部署成功',
        position: 'top',
      });

      isUploadDeployDialogOpen.value = false;
      await fetchContainerStatus();
    } else {
      uploadProgress.value = 0;
      Notify.create({
        type: 'negative',
        message: `部署失败：${response?.msg || '未知错误'}`,
        position: 'top',
      });
    }
  } catch (error: any) {
    uploadProgress.value = 0;
    Notify.create({
      type: 'negative',
      message: `上传失败${error?.message ? '：' + error.message : ''}`,
      position: 'top',
    });
  } finally {
    isDeploying.value = false;
  }
};

const handleSecondConfirmDelete = async () => {
  if (confirmText.value !== '确定删除') {
    Notify.create({
      message: '请输入“确定删除”',
      type: 'negative',
      position: 'top',
    });
    return;
  }

  isDeleting.value = true;

  try {
    await agentProxyApi.deletePythonProject(props.pythonProject.id);

    Notify.create({
      message: '删除成功',
      type: 'positive',
      position: 'top',
    });

    isSecondConfirmDeleteDialogOpen.value = false;
    isViewDetailDialogOpen.value = false;
    confirmText.value = '';
  } catch (error: any) {
    Notify.create({
      message: `删除失败${error?.message ? ': ' + error.message : ''}`,
      type: 'negative',
      position: 'top',
    });
  } finally {
    isDeleting.value = false;
  }
};

watch(isUploadDeployDialogOpen, (val) => {
  if (!val) {
    resetDeployDialogState();
  }
});

watch(isSecondConfirmDeleteDialogOpen, (val) => {
  if (!val) {
    confirmText.value = '';
  }
});

watch(
  () => props.pythonProject.container_name,
  () => {
    fetchContainerStatus();
  }
);

onMounted(() => {
  fetchContainerStatus();
});
</script>

<style scoped>
.python-project-card {
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

.python-project-card:hover {
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

.project-submeta-type {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
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
  cursor: pointer;
}

.info-row + .info-row {
  border-top: 1px dashed #e5e7eb;
}

.info-row:hover {
  background: rgba(248, 250, 252, 0.55);
}

.info-row-link:hover .access-url-link {
  color: #1d4ed8;
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

.access-url-link {
  color: #2563eb;
  font-weight: 600;
}

.multi-line-value {
  white-space: normal;
  overflow: visible;
  text-overflow: unset;
}

.single-line {
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
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

.card-actions {
  padding: 10px 14px 14px;
}

.detail-dialog-card {
  width: 88vw;
  max-width: 1100px;
  border-radius: 18px;
}

.detail-table-section {
  padding-top: 16px;
  padding-bottom: 16px;
}

.table-cell-value {
  white-space: pre-wrap;
  word-break: break-word;
  color: #334155;
}

.deploy-dialog-card {
  width: 92vw;
  max-width: 1100px;
  border-radius: 18px;
}

.deploy-project-name {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 10px;
}

.upload-tip {
  text-align: right;
  color: #909399;
}

.deploy-success-tip {
  color: #16a34a;
  font-size: 13px;
  margin-top: 10px;
}

.delete-dialog-card {
  width: 420px;
  max-width: 92vw;
  border-radius: 18px;
}

.delete-warning-text {
  color: #1f2937;
  line-height: 1.7;
}

.delete-warning-subtext {
  color: #dc2626;
  font-size: 14px;
}

:deep(.mono-input textarea) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

:deep(.q-card__section--vert) {
  word-break: break-word;
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