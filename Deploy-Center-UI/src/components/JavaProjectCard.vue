<template>
  <q-card class="java-project-card">
    <q-card-section>
      <div class="text-h6">
        {{ javaProject.project_name }}
      </div>
      <div class="row items-center q-mt-sm">
        <div class="col text-subtitle2">{{ javaProject.project_type }}</div>

        <div class="col-auto flex items-center justify-end">
          <template v-if="containerStatus === 'Checking'">
            <q-spinner color="grey-5" size="16px" />
          </template>
          <template v-else-if="containerStatus === 'Unkown'">
            <el-tag type="warning" effect="light">Status Unknown</el-tag>
          </template>
          <template v-else>
            <el-tag
              :closable="false"
              :type="getContainerStatusTagType(containerStatus)"
              effect="light"
            >
              {{ containerStatus }}
            </el-tag>
          </template>
        </div>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section>
      <p>项目代号: {{ javaProject.project_code }}</p>
      <p v-if="javaProject.access_url">访问地址: <a :href="javaProject.access_url" target="_blank">{{ javaProject.access_url }}</a></p>
      <p>JDK版本: {{ javaProject.jdk_version }}</p>
      <p>
        Docker 镜像: {{ javaProject.docker_image_name }}:{{
          javaProject.docker_image_tag
        }}
      </p>
      <p>容器名称: {{ javaProject.container_name }}</p>
      <p>外部端口: {{ javaProject.external_port }}</p>
      <p>内部端口: {{ javaProject.internal_port }}</p>
      <p v-if="javaProject.network">Docker网络: {{ javaProject.network }}</p>
      <p>宿主机路径: {{ javaProject.host_project_path }}</p>
      <p>容器内路径: {{ javaProject.container_project_path }}</p>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn flat color="primary" label="详情" @click="viewJavaProjectDetail" />

      <q-btn flat dense color="info" icon="cloud" label="云构建部署" @click="openCloudBuildDeployDialog" />

      <q-btn flat dense color="positive" icon="cloud_upload" label="上传部署" @click="openUploadDeployDialog" />
    </q-card-actions>
  </q-card>

  <!-- 详情对话框 -->
  <q-dialog v-model="isViewDetailDialogOpen">
    <q-card style="width: 100%">
      <q-card-section>
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
        <div class="text-h5">上传部署（{{ javaProject.project_name }}）</div>
      </q-card-section>

      <q-card-section>
        <div class="text-h6">上传Jar包</div>
        <el-upload ref="uploadRef" drag :auto-upload="false" accept=".jar"
          :on-change="handleFileChange" :file-list="fileList" :disabled="uploadProgress > 0">
          <div class="el-upload__text">
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
          </div>
          <template #tip>
            <div class="el-upload__tip" style="text-align: right; color: #909399">
              只能上传.jar文件
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

      <q-card-section>
        <div class="text-h6">设置Dockerfile</div>
        <q-input v-model="dockerfileContent" type="textarea" outlined rows="16"
          style="margin-top: 10px; font-family: Console;" :disable="isDeploying" />
      </q-card-section>

      <q-card-section>
        <div class="text-h6">设置Docker命令</div>
        <q-input v-model="dockerCommand" type="textarea" outlined rows="10"
          style="margin-top: 10px; font-family: Console;" :disable="isDeploying" />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="取消" v-close-popup />
        <q-btn flat label="开始部署" color="positive" @click="handleUploadDeploy"
          :disabled="!fileList.length || uploadProgress > 0" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <!-- 再次确认删除对话框 -->
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
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory';
import { formatDate } from 'src/utils/dateFormatter';
import { JavaProject } from 'src/types/Project.types';
import { UpdateJavaProjectRequestDto } from "src/types/dto/UpdateJavaProjectRequestDto";
import type { AxiosProgressEvent } from 'axios';

const props = defineProps<{
  javaProject: JavaProject;
}>();

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

const viewJavaProjectDetail = () => {
  tableData.value = [
    { label: '项目Id', key: 'id', value: props.javaProject.id, editable: false },
    { label: '项目代号', key: 'project_code', value: props.javaProject.project_code, editable: true },
    { label: '项目名称', key: 'project_name', value: props.javaProject.project_name, editable: true },
    { label: '项目分组', key: 'project_group', value: props.javaProject.project_group, editable: true },
    { label: 'Docker 镜像名称', key: 'docker_image_name', value: props.javaProject.docker_image_name, editable: true },
    { label: 'Docker 镜像标签', key: 'docker_image_tag', value: props.javaProject.docker_image_tag, editable: true },
    { label: '容器名称', key: 'container_name', value: props.javaProject.container_name, editable: true },
    { label: '外部端口', key: 'external_port', value: String(props.javaProject.external_port), editable: true },  // 转字符串
    { label: '内部端口', key: 'internal_port', value: String(props.javaProject.internal_port), editable: true },    // 转字符串
    { label: '宿主机路径', key: 'host_project_path', value: props.javaProject.host_project_path, editable: true },
    { label: '容器内路径', key: 'container_project_path', value: props.javaProject.container_project_path, editable: true },
    { label: '访问地址', key: 'access_url', value: props.javaProject.access_url, editable: true },
    { label: 'Git地址', key: 'git_repository', value: props.javaProject.git_repository, editable: true },
    { label: 'JDK版本', key: 'jdk_version', value: String(props.javaProject.jdk_version), editable: false },
    { label: '创建时间', key: 'created_at', value: formatDate(props.javaProject.created_at), editable: false },
    { label: '更新时间', key: 'updated_at', value: formatDate(props.javaProject.updated_at), editable: false },
    { label: '最近部署时间', key: 'last_deployed_at', value: formatDate(props.javaProject.last_deployed_at), editable: false },
  ];
  isViewDetailDialogOpen.value = true;
};

const containerStatus = ref('Checking');

onMounted(async () => {
  try {
    const response = await provideCurrentAgentProxyApi().fetchDockerContainerStatus(`${props.javaProject.container_name}`);
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
  if (s.includes('awaiting deployment')) return 'info';     // 待部署
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
  const updateData: Partial<UpdateJavaProjectRequestDto> = {};

  tableData.value.forEach(item => {
    const skipKeys = ['created_at', 'updated_at', 'last_deployed_at'];

    if (!skipKeys.includes(item.key)) {
      updateData[item.key as keyof UpdateJavaProjectRequestDto] = item.value as any;
    }
  });

  // 确保包含 ID
  updateData['id'] = props.javaProject.id;

  console.log('[编辑保存] 构造的更新数据：', updateData);

  try {
    await provideCurrentAgentProxyApi().updateJavaProject(updateData as UpdateJavaProjectRequestDto);
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
const openUploadDeployDialog = async () => {
  isUploadDeployDialogOpen.value = true;
  fileList.value = [];
  uploadProgress.value = 0;

  const systemConfig1 = await provideCurrentAgentProxyApi().fetchSystemConfig("default_java_dockerfile_template")
  const defaultJavaDockerfileTemplate = systemConfig1.config_value
  dockerfileContent.value = await provideCurrentAgentProxyApi().renderTemplateContent(props.javaProject.id, defaultJavaDockerfileTemplate)

  const systemConfig2 = await provideCurrentAgentProxyApi().fetchSystemConfig("default_java_dockercommand_template")
  const defaultJavaDockercommandTemplate = systemConfig2.config_value
  dockerCommand.value = await provideCurrentAgentProxyApi().renderTemplateContent(props.javaProject.id, defaultJavaDockercommandTemplate)

  // const dockerfileTemplates = await provideCurrentAgentProxyApi().fetchTemplateList("dockerfile");
  // const dockercommandTemplates = await provideCurrentAgentProxyApi().fetchTemplateList("dockercommand");

};

const openCloudBuildDeployDialog = () => {
  isCloudBuildDeployDialogOpen.value = true;
  Notify.create({
    message: '尚未实现，敬请期待！',
    type: 'warning',
    position: 'top',
  });
};

const handleFileChange = (file: any) => {
  fileList.value = [file];
};

const handleUploadDeploy = async () => {
  isDeploying.value = true;
  const file = fileList.value[0]?.raw;
  if (!file) {
    Notify.create({
      type: 'negative',
      message: '请选择一个文件',
      position: 'top',
    });
    return;
  }

  try {
    uploadProgress.value = 0;

    const formData = new FormData();
    formData.append('id', props.javaProject.id);
    formData.append('file', file);
    formData.append('dockerfile_content', dockerfileContent.value);
    formData.append('dockercommand_content', dockerCommand.value);

    const response = await provideCurrentAgentProxyApi().deployJavaProject(formData, {
      onUploadProgress: (event: AxiosProgressEvent) => {
        if (event.total) {
          const percentCompleted = Math.round(
            (event.loaded * 100) / event.total
          );
          uploadProgress.value = percentCompleted;
        }
      },
    });

    if (response.code === 200) {
      uploadProgress.value = 100;
      Notify.create({
        type: 'positive',
        message: '部署成功',
        position: 'top',
      });
      setTimeout(() => {
        isUploadDeployDialogOpen.value = false;
      }, 1000);
    } else {
      Notify.create({
        type: 'negative',
        message: response.message || '部署失败',
        position: 'top',
      });
      uploadProgress.value = 0;
    }
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: '上传失败：' + error,
      position: 'top',
    });
    uploadProgress.value = 0;
  }
};
// ==================== ↑↑↑↑↑ 部署相关↑↑↑↑↑ ====================

const handleSecondConfirmDelete = async () => {
  if (confirmText.value === '确定删除') {
    try {
      await provideCurrentAgentProxyApi().deleteJavaProject(props.javaProject.id)
      Notify.create({
        message: '删除成功',
        type: 'positive',
        position: 'top',
      });
      // 关闭对话框
      isSecondConfirmDeleteDialogOpen.value = false;
      isViewDetailDialogOpen.value = false;
    } catch (error: any) {
      Notify.create({
        message: '删除失败: ' + error.message,
        type: 'negative',
        position: 'top',
      });
    } finally {
      confirmText.value = '';
    }
  } else {
    Notify.create({
      message: '请输入"确定删除"',
      type: 'negative',
      position: 'top',
    });
  }
};
</script>

<style scoped>
.java-project-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>