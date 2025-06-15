<template>
  <q-card class="python-project-card">
    <q-card-section>
      <div class="text-h6">{{ pythonProject.project_name }}</div>
      <div class="row items-center q-mt-sm">
        <div class="col text-subtitle2">{{ pythonProject.project_type }}</div>
        <div class="col-auto flex items-center justify-end">
          <div class="col-auto flex items-center justify-end">
            <template v-if="containerStatus === 'Checking'">
              <q-spinner color="grey-5" size="16px" />
            </template>
            <template v-else-if="containerStatus === 'Unkown'">
              <el-tag type="warning" effect="light">Status Unknown</el-tag>
            </template>
            <template v-else>
              <el-tag :closable="false" :type="getContainerStatusTagType(containerStatus)" effect="light">
                {{ containerStatus }}
              </el-tag>
            </template>
          </div>
        </div>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section>
      <p>项目代号: {{ pythonProject.project_code }}</p>
      <p>Python版本: {{ pythonProject.python_version }}</p>
      <p>框架: {{ pythonProject.framework }}</p>
      <p v-if="pythonProject.network">Docker网络: {{ pythonProject.network }}</p>
      <p>宿主机路径: {{ pythonProject.host_project_path }}</p>
      <p>容器内路径: {{ pythonProject.container_project_path }}</p>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn flat color="primary" label="详情" @click="viewPythonProjectDetail" />

      <q-btn flat dense color="info" icon="cloud" label="云构建部署" @click="openCloudBuildDeployDialog" />

      <q-btn flat dense color="positive" icon="cloud_upload" label="上传部署" @click="openUploadDeployDialog" />
    </q-card-actions>
  </q-card>

  <!-- 详情对话框 -->
  <q-dialog v-model="isViewDetailDialogOpen">
    <q-card style="width: 80%">
      <q-card-section>
        <!-- 右上角关闭按钮 -->
        <q-btn icon="close" flat round dense class="float-right" v-close-popup />
        <div class="text-h6">项目详情</div>
      </q-card-section>
      <q-separator />

      <!-- 数据表格 -->
      <q-card-section>
        <el-table :data="tableData" border>
          <el-table-column prop="key" label="字段" width="170" />
          <el-table-column prop="label" label="注释" width="130" />
          <el-table-column label="值">
            <template v-slot="scope">
              <div v-if="!isEditing || !scope.row.editable">{{ scope.row.value }}</div>
              <el-input v-else v-model="scope.row.value" placeholder="请输入内容" clearable />
            </template>
          </el-table-column>
        </el-table>
      </q-card-section>

      <q-separator />

      <!-- 控制按钮 -->
      <q-card-actions>
        <q-btn flat color="negative" label="删除" @click="isSecondConfirmDeleteDialogOpen = true" />
        <q-space />
        <q-btn v-if="isEditing" flat color="negative" label="取消" @click="cancelEdit" />
        <q-btn v-if="isEditing" flat color="positive" label="保存" @click="saveEdit" />
        <q-btn v-else flat color="secondary" label="编辑" @click="startEdit" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <!-- 上传部署对话框 -->
  <q-dialog v-model="isUploadDeployDialogOpen">
    <q-card style="width: 100%; max-width: 70vw;">
      <q-card-section>
        <div class="text-h5">上传部署</div>
      </q-card-section>

      <!-- 上传文件 -->
      <q-card-section>
        <div class="text-h6">上传 .zip 文件</div>
        <el-upload ref="uploadRef" drag :auto-upload="false" accept=".zip" :before-upload="handleBeforeUpload"
          :on-change="handleFileChange" :file-list="fileList" :disabled="uploadProgress > 0">
          <div class="el-upload__text">
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
          </div>
          <template #tip>
            <div class="el-upload__tip" style="text-align: right; color: #909399">
              只能上传 .zip 文件
            </div>
          </template>
        </el-upload>

        <!-- 上传进度条 -->
        <el-progress v-if="uploadProgress > 0" color="#67c23a" :percentage="uploadProgress" :text-inside="true"
          :stroke-width="13" status="success" class="q-mt-md" />

        <div v-if="uploadProgress === 100" class="text-positive" style="margin-top: 10px">
          上传完成！
        </div>
      </q-card-section>

      <!-- Dockerfile 输入 -->
      <q-card-section>
        <div class="text-h6">Dockerfile 内容（可选）</div>
        <q-input v-model="dockerfileContent" type="textarea" outlined rows="14" style="font-family: monospace"
          :disable="isDeploying" />
      </q-card-section>

      <!-- Docker 启动命令输入 -->
      <q-card-section>
        <div class="text-h6">Docker 命令（可选）</div>
        <q-input v-model="dockerCommand" type="textarea" outlined rows="10" style="font-family: monospace"
          :disable="isDeploying" />
      </q-card-section>

      <!-- 操作按钮 -->
      <q-card-actions align="right">
        <q-btn flat label="取消" v-close-popup />
        <q-btn flat label="开始部署" color="positive" :disable="!fileList.length || uploadProgress > 0"
          @click="handleUploadDeploy" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <!-- 二次确认删除对话框 -->
  <q-dialog v-model="isSecondConfirmDeleteDialogOpen">
    <q-card style="width: 30%">
      <q-card-section class="text-h6"> 危险操作 </q-card-section>

      <q-card-section>
        <div style="color: red; text-indent: 1rem">
          请输入“确定删除”以进行删除操作。
        </div>

        <q-input v-model="confirmText" />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn label="确定" @click="handleSecondConfirmDelete" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Notify } from 'quasar';
import { formatDate } from 'src/utils/dateFormatter';
import { useAgentStore } from 'src/stores/useAgentStore';
import { AgentCommandApi } from 'src/api/AgentCommandApi';
import { PythonProject } from 'src/types/Project.types';
import { UpdatePythonProjectRequestDto } from "src/types/dto/UpdatePythonProjectRequestDto";

const props = defineProps<{
  pythonProject: PythonProject;
}>();

const agentStore = useAgentStore();

// 获取 AgentCommandApi 实例
const getAgentCommandApi = () => {
  if (!agentStore.currentAgent) {
    throw new Error('未选择 Agent');
  }
  return new AgentCommandApi(agentStore.currentAgent.id);
};

const isViewDetailDialogOpen = ref(false);
const isUploadDeployDialogOpen = ref(false);
const isCloudBuildDeployDialogOpen = ref(false);
const isSecondConfirmDeleteDialogOpen = ref(false);

const dockerfileContent = ref('');
const dockerCommand = ref('');

const confirmText = ref('');
const uploadProgress = ref(0);
const fileList = ref<any[]>([]);

const tableData = ref<{ label: string; value: string; key: string, editable: boolean }[]>([]);

const viewPythonProjectDetail = () => {
  tableData.value = [
    { label: '项目Id', key: 'id', value: props.pythonProject.id, editable: false },
    { label: '项目代号', key: 'project_code', value: props.pythonProject.project_code, editable: true },
    { label: '项目名称', key: 'project_name', value: props.pythonProject.project_name, editable: true },
    { label: '项目分组', key: 'project_group', value: props.pythonProject.project_group, editable: true },
    { label: 'Docker 镜像名称', key: 'docker_image_name', value: props.pythonProject.docker_image_name, editable: true },
    { label: 'Docker 镜像标签', key: 'docker_image_tag', value: props.pythonProject.docker_image_tag, editable: true },
    { label: '外部端口', key: 'external_port', value: String(props.pythonProject.external_port), editable: true },  // 转字符串
    { label: '内部端口', key: 'internal_port', value: String(props.pythonProject.internal_port), editable: true },    // 转字符串
    { label: 'Docker 网络', key: 'network', value: props.pythonProject.network, editable: false },
    { label: 'Python版本', key: 'python_version', value: props.pythonProject.python_version, editable: false },
    { label: '宿主机路径', key: 'host_project_path', value: props.pythonProject.host_project_path, editable: true },
    { label: '容器内路径', key: 'container_project_path', value: props.pythonProject.container_project_path, editable: true },
    { label: 'Git地址', key: 'git_repository', value: props.pythonProject.git_repository, editable: true },
    { label: '创建时间', key: 'created_at', value: formatDate(props.pythonProject.created_at), editable: false },
    { label: '更新时间', key: 'updated_at', value: formatDate(props.pythonProject.updated_at), editable: false },
    { label: '最近部署时间', key: 'last_deployed_at', value: formatDate(props.pythonProject.last_deployed_at), editable: false },
  ];
  isViewDetailDialogOpen.value = true;
};

const containerStatus = ref('Checking');

onMounted(async () => {
  try {
    const response = await getAgentCommandApi().fetchDockerContainerStatus(`${props.pythonProject.docker_image_name}:${props.pythonProject.docker_image_tag}`);
    containerStatus.value = response.container_status;
  } catch (error) {
    containerStatus.value = 'Unknown';
  }
});

const getContainerStatusTagType = (status: string): string => {
  const s = status.toLowerCase();

  if (s.startsWith("up")) return "success";                 // 容器正在运行
  if (s.startsWith("exited (0)")) return "info";            // 正常退出
  if (s.startsWith("exited")) return "danger";              // 非正常退出
  if (s.startsWith("restarting")) return "warning";         // 正在重启
  if (s.startsWith("paused")) return "warning";             // 已暂停
  if (s.startsWith("created")) return "default";            // 刚创建未启动
  if (s.startsWith("dead")) return "danger";                // 崩溃状态
  if (s.includes("not found")) return "danger";            // 容器不存在
  if (s.includes('awaiting deployment')) return 'info';    // 待部署
  return "default";                                          // 兜底
};

const isEditing = ref(false);

const startEdit = () => {
  isEditing.value = true;
};

const cancelEdit = () => {
  isEditing.value = false;
};


const saveEdit = async () => {
  const updateData: Partial<UpdatePythonProjectRequestDto> = {};

  tableData.value.forEach(item => {
    if (item.key === 'created_at' || item.key === 'updated_at' || item.key === 'last_deployed_at') {
      // 这些时间时间不需要修改
    } else {
      updateData[item.key as keyof UpdatePythonProjectRequestDto] = item.value as any;
    }
  });

  // 确保包含 ID
  updateData['id'] = props.pythonProject.id;

  console.log(updateData)

  try {
    await getAgentCommandApi().updatePythonProject(updateData as UpdatePythonProjectRequestDto);
    Notify.create({
      type: 'positive',
      message: '保存成功',
    });
    isEditing.value = false;
    isViewDetailDialogOpen.value = false;
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: '保存失败',
    });
  }
};

// ==================== ↓↓↓↓↓ 部署相关 ↓↓↓↓↓ ====================
const isDeploying = ref(false)
// 打开文件选择框
const openUploadDeployDialog = async () => {
  isUploadDeployDialogOpen.value = true;
  // 初始化文件列表和进度
  fileList.value = [];
  uploadProgress.value = 0;


  const systemConfig1 = await getAgentCommandApi().fetchSystemConfig("default_python_dockerfile_template")
  const defaultPythonDockerfileTemplate = systemConfig1.config_value
  dockerfileContent.value = await getAgentCommandApi().renderTemplateContent(props.pythonProject.id, defaultPythonDockerfileTemplate)

  const systemConfig2 = await getAgentCommandApi().fetchSystemConfig("default_python_dockercommand_template")
  const defaultPythonDockercommandTemplate = systemConfig2.config_value
  dockerCommand.value = await getAgentCommandApi().renderTemplateContent(props.pythonProject.id, defaultPythonDockercommandTemplate)
};

const openCloudBuildDeployDialog = () => {
  isCloudBuildDeployDialogOpen.value = true;
  Notify.create({
    message: '尚未实现，敬请期待！',
    type: 'warning',
    position: 'top',
  });
};

const handleBeforeUpload = (file: File): boolean => {
  const isZip = file.type === 'application/zip' || file.name.endsWith('.zip');
  if (!isZip) {
    Notify.create({
      type: 'negative',
      message: '只能上传.zip文件',
      position: 'top',
    });
    return false;
  }
  return true;
};

const handleFileChange = (file: any) => {
  fileList.value = [file]; // 限制只能上传一个文件
};

const handleUploadDeploy = async () => {
  const file = fileList.value[0]?.raw; // 获取文件对象
  if (!file) {
    Notify.create({
      type: 'negative',
      message: '请选择一个文件',
      position: 'top',
    });
    return;
  }

  try {
    uploadProgress.value = 0; // 初始化进度

    const formData = new FormData();
    formData.append('id', props.pythonProject.id);
    formData.append('file', file);
    formData.append('dockerfile_content', dockerfileContent.value);
    formData.append('dockercommand_content', dockerCommand.value);

    // 调用 deployPythonProject API
    const response = await getAgentCommandApi().deployPythonProject(formData, {
      onUploadProgress: (event) => {
        if (event.total) {
          const percentCompleted = Math.round(
            (event.loaded * 100) / event.total
          );
          uploadProgress.value = percentCompleted;
        }
      },
    });

    if (response.code === 200) {
      uploadProgress.value = 100; // 标记上传完成
      Notify.create({
        type: 'positive',
        message: '部署成功',
        position: 'top',
      });

      // 部署成功后 延迟关闭对话框
      setTimeout(() => {
        isUploadDeployDialogOpen.value = false; // 延迟关闭对话框
      }, 1000);
    } else {
      Notify.create({
        type: 'negative',
        message: '部署失败：' + response.msg,
        position: 'top',
      });
      uploadProgress.value = 0; // 重置进度
    }
  } catch (error) {
    console.error('Upload error:', error);
    Notify.create({
      type: 'negative',
      message: '上传失败：' + error,
      position: 'top',
    });
    uploadProgress.value = 0; // 重置进度
  }
};
// ==================== ↑↑↑↑↑ 部署相关↑↑↑↑↑ ====================
const handleSecondConfirmDelete = async () => {
  if (confirmText.value === '确定删除') {
    try {
      await getAgentCommandApi().deletePythonProject(props.pythonProject.id)

      Notify.create({
        message: '删除成功',
        type: 'positive',
        position: 'top',
      });

      isSecondConfirmDeleteDialogOpen.value = false; // 关闭删除确认对话框
      isViewDetailDialogOpen.value = false; // 关闭详情对话框
    } catch (error: any) {
      Notify.create({
        message: '删除失败: ' + error.message,
        type: 'negative',
        position: 'top',
      });
    } finally {
      confirmText.value = ''; // 清空输入框
    }
  } else {
    Notify.create({
      message: '请输入"确定删除"',
      type: 'negative',
      position: 'top',
    });
  }
}
</script>

<style scoped>
.python-project-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>
