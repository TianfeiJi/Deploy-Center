<template>
  <q-card class="web-project-card">
    <q-card-section>
      <div class="text-h6">{{ webProject.project_name }}</div>
      <div class="row items-center q-mt-sm">
        <div class="col text-subtitle2">{{ webProject.project_type }}</div>

        <div class="q-ml-sm">
        <q-spinner
          v-if="deploymentStatus === 'Checking'"
          color="grey-5"
          size="16px"
        />
        <el-tag v-else :type="getDeploymentStatusTagType(deploymentStatus)">
          {{ deploymentStatus }}
        </el-tag>
      </div>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section>
      <p>项目代号: {{ webProject.project_code }}</p>
      <p v-if="webProject.access_url">访问地址: <a :href="webProject.access_url" target="_blank">{{ webProject.access_url }}</a></p>
      <p>宿主机路径: {{ webProject.host_project_path }}</p>
      <p>容器内路径: {{ webProject.container_project_path }}</p>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn flat color="primary" label="详情" @click="viewWebProjectDetail" />

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
    <q-card style="width: 500px">
      <q-card-section>
        <div class="text-h6">上传部署文件（{{ webProject.project_name }}）</div>
      </q-card-section>
      <q-card-section>
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
              只能上传.zip文件
            </div>
          </template>
        </el-upload>

        <!-- 进度条和进度百分比 -->
        <el-progress v-if="uploadProgress > 0" color="#67c23a" :percentage="uploadProgress" :text-inside="true"
          :stroke-width="13" status="success" />

        <div v-if="uploadProgress === 100" class="text-positive" style="margin-top: 10px">
          上传完成！
        </div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="取消" v-close-popup />
        <q-btn flat label="开始部署" color="positive" @click="handleUploadDeploy"
          :disabled="!fileList.length || uploadProgress > 0" />
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
import { onMounted, ref } from 'vue';
import { Notify } from 'quasar';
import { formatDate } from 'src/utils/dateFormatter';
import { useAgentStore } from 'src/stores/useAgentStore';
import { AgentCommandApi } from 'src/api/AgentCommandApi';
import { WebProject } from 'src/types/Project.types';
import { UpdateWebProjectRequestDto } from "src/types/dto/UpdateWebProjectRequestDto";

const agentStore = useAgentStore();

// 获取 AgentCommandApi 实例
const getAgentCommandApi = () => {
  if (!agentStore.currentAgent) {
    throw new Error('未选择 Agent');
  }
  return new AgentCommandApi(agentStore.currentAgent.id);
};

const props = defineProps<{
  webProject: WebProject;
}>();

const isViewDetailDialogOpen = ref(false);

const tableData = ref<{ label: string; value: string; key: string, editable: boolean }[]>([]);

// 打开详情对话框
const viewWebProjectDetail = () => {
  tableData.value = [
    { label: '项目Id', key: 'id', value: props.webProject.id, editable: false },
    { label: '项目代号', key: 'project_code', value: props.webProject.project_code, editable: true },
    { label: '项目名称', key: 'project_name', value: props.webProject.project_name, editable: true },
    { label: '项目分组', key: 'project_group', value: props.webProject.project_group, editable: true },
    { label: '宿主机路径', key: 'host_project_path', value: props.webProject.host_project_path, editable: true },
    { label: '容器内路径', key: 'container_project_path', value: props.webProject.container_project_path, editable: true },
    { label: 'Git地址', key: 'git_repository', value: props.webProject.git_repository, editable: true },
    { label: '访问地址', key: 'access_url', value: props.webProject.access_url, editable: true },
    { label: '创建时间', key: 'created_at', value: formatDate(props.webProject.created_at), editable: false },
    { label: '更新时间', key: 'updated_at', value: formatDate(props.webProject.updated_at), editable: false },
    { label: '最近部署时间', key: 'last_deployed_at', value: formatDate(props.webProject.last_deployed_at), editable: false }
  ];
  isViewDetailDialogOpen.value = true;
};

const deploymentStatus = ref<'Deployed' | 'Awaiting Deployment' | 'Checking' | 'Unknown'>('Checking');

onMounted(async () => {
  try {
    const response = await getAgentCommandApi().checkWebProjectDeploymentStatus(props.webProject.id);
    deploymentStatus.value = response.deployment_status;
  } catch (error) {
    deploymentStatus.value = 'Unknown';
  }
});

const getDeploymentStatusTagType = (status: string): string => {
  if (status == "Deployed") return "success"; 
  if (status == "Awaiting Deployment") return "info"; 
  return "default";
};

const isEditing = ref(false);

const startEdit = () => {
  isEditing.value = true;
};

const cancelEdit = () => {
  isEditing.value = false;
};

const saveEdit = async () => {
  const updateData: Partial<UpdateWebProjectRequestDto> = {};

  tableData.value.forEach(item => {
    const skipKeys = ['created_at', 'updated_at', 'last_deployed_at'];

    if (!skipKeys.includes(item.key)) {
      updateData[item.key as keyof UpdateWebProjectRequestDto] = item.value as any;
    }
  });

  // 确保包含 ID
  updateData['id'] = props.webProject.id;

  console.log('[编辑保存] 构造的更新数据：', updateData);

  try {
    await getAgentCommandApi().updateWebProject(updateData as UpdateWebProjectRequestDto);

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
// 云构建部署对话框开关
const isCloudBuildDeployDialogOpen = ref(false);
const openCloudBuildDeployDialog = () => {
  isCloudBuildDeployDialogOpen.value = true;
  Notify.create({
    message: '尚未实现，敬请期待！',
    type: 'warning',
    position: 'top',
  });
};

// 上传部署对话框开关
const isUploadDeployDialogOpen = ref(false);
// 打开文件选择框
const openUploadDeployDialog = async () => {
  isUploadDeployDialogOpen.value = true;
  // 初始化文件列表和进度
  fileList.value = [];
  uploadProgress.value = 0;
};
const uploadProgress = ref(0); // 上传进度
const fileList = ref<any[]>([]); // 文件列表

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
    formData.append('id', props.webProject.id);
    formData.append('file', file);

    // 调用 deployWebProject API
    const response = await getAgentCommandApi().deployWebProject(formData, {
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
const isSecondConfirmDeleteDialogOpen = ref(false);
const confirmText = ref('');
const handleSecondConfirmDelete = async () => {
  if (confirmText.value === '确定删除') {
    try {
      await getAgentCommandApi().deleteWebProject(props.webProject.id)
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
.web-project-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>
