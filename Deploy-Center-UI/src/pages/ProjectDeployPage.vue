<template>
  <q-page class="q-pa-md">
    <!-- 顶部控制区域 -->
    <div class="row items-center q-mb-md" style="margin-bottom: 20px">
      <!-- 项目类型筛选 -->
      <div class="col-auto">
        <q-tabs
          v-model="filterType"
          inline-label
          indicator-color="primary"
          dense
          no-caps
          class="text-grey-8"
        >
          <q-tab name="所有" label="所有" />
          <q-tab name="Web" label="Web" />
          <q-tab name="Java" label="Java" />
          <q-tab name="Python" label="Python" />
        </q-tabs>
      </div>

      <!-- 排序方式 -->
      <div class="col-auto" style="margin-left: 50px">
        <span>排序：</span>
        <el-select
          v-model="sortOrder"
          placeholder="排序方式"
          style="width: 110px"
        >
          <el-option label="类型" value="project_type" />
          <el-option label="名称" value="project_name" />
          <el-option label="创建时间" value="created_at" />
          <el-option label="更新时间" value="updated_at" />
          <el-option label="部署时间" value="last_deployed_at" />
        </el-select>
      </div>

      <!-- 分组 -->
      <div class="col-auto" style="margin-left: 50px">
        <span>分组：</span>
        <el-select
          v-model="selectedGroup"
          placeholder="分组"
          style="width: 110px"
        >
          <el-option
            v-for="group in uniqueGroups"
            :key="group"
            :label="group"
            :value="group"
          />
        </el-select>
      </div>

      <q-space />

      <!-- 搜索框 -->
      <div class="col-auto col-grow">
        <q-input
          v-model="filterKeyword"
          placeholder="搜索项目"
          outlined
          dense
          class="full-width"
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>

      <!-- 添加项目按钮 -->
      <div class="col-auto q-ml-md">
        <q-btn
          color="primary"
          label="添加项目"
          @click="isCreateNewProjectDialogOpen = true"
        />
      </div>
    </div>

    <!-- 项目卡片列表 -->
    <div class="row q-col-gutter-md">
      <div
        v-for="project in filteredProjects"
        :key="project.id"
        class="col-12 col-sm-6 col-md-4 col-lg-3"
      >
        <!-- 动态选择卡片组件 -->
        <WebProjectCard
          v-if="project.project_type === 'Web'"
          :webProject="project"
        />

        <JavaProjectCard
          v-else-if="project.project_type === 'Java'"
          :javaProject="project"
        />

        <PythonProjectCard
          v-else-if="project.project_type === 'Python'"
          :pythonProject="project"
        />
      </div>
    </div>

    <!-- 新增项目对话框 -->
    <el-dialog
      v-model="isCreateNewProjectDialogOpen"
      title="创建项目"
      width="500px"
    >
      <!-- 项目类型选择 -->
      <el-radio-group v-model="selectedProjectType" style="margin-bottom: 20px">
        <el-radio-button label="Web">Web</el-radio-button>
        <el-radio-button label="Java">Java</el-radio-button>
        <el-radio-button label="Python">Python</el-radio-button>
      </el-radio-group>

      <!-- 动态表单 -->
      <el-form
        ref="projectForm"
        :model="currentProject"
        :rules="rules"
        label-width="120px"
      >
        <!-- 公共必填字段 -->
        <el-form-item
          label="项目代号"
          prop="project_code"
          :rules="rules.project_code"
        >
          <el-input v-model="currentProject.project_code" />
        </el-form-item>
        <el-form-item
          label="项目名称"
          prop="project_name"
          :rules="rules.project_name"
        >
          <el-input v-model="currentProject.project_name" />
        </el-form-item>
        <el-form-item label="宿主机路径" prop="host_project_path">
          <el-input v-model="currentProject.host_project_path" />
        </el-form-item>
        <el-form-item label="容器内路径" prop="container_project_path">
          <el-input v-model="currentProject.container_project_path" />
        </el-form-item>
         <el-form-item label="容器名称" prop="container_name">
          <el-input v-model="currentProject.container_name" />
        </el-form-item>
         <!-- Java 独有字段 -->
        <div
          v-if="
            selectedProjectType === 'Java'
          "
        >
          <el-form-item label="JDK版本" prop="jdk_version">
            <el-input v-model="currentProject.jdk_version" />
          </el-form-item>
        </div>
         <!-- Web 独有字段 -->
        <div v-if="selectedProjectType === 'Web'">
          <el-form-item label="访问地址" prop="access_url">
            <el-input v-model="currentProject.access_url" />
          </el-form-item>
        </div>
        <!-- Java 和 Python共同独有字段 -->
        <div
          v-if="
            selectedProjectType === 'Java' || selectedProjectType === 'Python'
          "
        >
          <el-form-item label="Docker 镜像名称" prop="docker_image_name">
            <el-input v-model="currentProject.docker_image_name" />
          </el-form-item>
          <el-form-item label="Docker 镜像标签" prop="docker_image_tag">
            <el-input v-model="currentProject.docker_image_tag" />
          </el-form-item>
          <el-form-item label="外部端口" prop="external_port">
            <el-input v-model="currentProject.external_port" />
          </el-form-item>
          <el-form-item label="内部端口" prop="internal_port">
            <el-input v-model="currentProject.internal_port" />
          </el-form-item>
        </div>

        <!-- 公共非必填字段 -->
        <el-form-item label="项目分组" prop="project_group">
          <el-input v-model="currentProject.project_group" />
        </el-form-item>
        <el-form-item label="Git 仓库" prop="git_repository">
          <el-input v-model="currentProject.git_repository" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="isCreateNewProjectDialogOpen = false"
          >取消</el-button
        >
        <el-button type="primary" @click="handleCreateNewProject"
          >创建</el-button
        >
      </template>
    </el-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { Notify } from 'quasar';
import { useAgentStore } from 'src/stores/useAgentStore';
import { AgentCommandApi } from 'src/api/AgentCommandApi';
import { AddWebProjectRequestDto } from 'src/types/dto/AddWebProjectRequestDto';
import { AddJavaProjectRequestDto } from 'src/types/dto/AddJavaProjectRequestDto';
import WebProjectCard from 'src/components/WebProjectCard.vue';
import JavaProjectCard from 'src/components/JavaProjectCard.vue';
import PythonProjectCard from 'src/components/PythonProjectCard.vue';

const agentStore = useAgentStore();

const { currentAgent } = storeToRefs(agentStore);

// 部署中心用于控制当前 Agent 的指挥通道实例
const agentCommandApi = ref<AgentCommandApi | null>(null);

// 当前 Agent 关联的项目列表
const projects = ref<any[]>([]);

// 监听 currentAgent 变化
watch(
  currentAgent,
  async (agent) => {
    if (agent?.id) {
      agentCommandApi.value = new AgentCommandApi(agent.id);
      projects.value = await agentCommandApi.value.fetchProjectList();
      console.log(`Agent 切换到: ${agent.name} (${agent.ip})，已刷新项目列表`);
    } else {
      projects.value = [];
      agentCommandApi.value = null;
    }
  }
);

const filterType = ref<'所有' | 'Web' | 'Java' | 'Python'>('所有');
const filterKeyword = ref<string>('');
const selectedGroup = ref<string>('所有'); // 当前选择的分组，默认选择“所有”，即不进行组别筛选

const sortOrder = ref('project_type');
const sortOptions = ref([
  { label: '类型', value: 'project_type' },
  { label: '名称', value: 'project_name' },
  { label: '创建时间', value: 'created_at' },
  { label: '更新时间', value: 'updated_at' },
  { label: '上次部署时间', value: 'last_deployed_at' },
]);

// ========== ↓↓↓↓↓ 新增项目 ↓↓↓↓↓ ==========
const isCreateNewProjectDialogOpen = ref(false);
const selectedProjectType = ref('Web');
const currentProject = ref({
  project_code: '',
  project_name: '',
  project_group: '',
  git_repository: '',
  docker_image_name: '',
  docker_image_tag: '',
  container_name: '',
  external_port: 18080,
  internal_port: 18080,
  access_url: '',
  network: '',
  jdk_version: 8,
  host_project_path: '',
  container_project_path: '',
});
const projectForm = ref<any>(null);

const rules = {
  project_code: [
    { required: true, message: '项目代号不能为空', trigger: 'blur' },
  ],
  project_name: [
    { required: true, message: '项目名称不能为空', trigger: 'blur' },
  ],
  jdk_version: [
    { required: true, message: 'JDK版本不能为空', trigger: 'blur' },
  ],
  host_project_path: [
    { required: true, message: '宿主机路径不能为空', trigger: 'blur' },
  ],
  container_project_path: [
    { required: true, message: '容器内路径不能为空', trigger: 'blur' },
  ],
};

const handleCreateNewProject = async () => {
  const isValid =
    currentProject.value.project_code && currentProject.value.project_name;
  if (!isValid) {
    Notify.create({
      position: 'top',
      type: 'negative',
      message: '项目代号和项目名称不能为空',
    });
    return;
  }

  switch (selectedProjectType.value) {
    case 'Web':
      const addWebProjectRequestDto: AddWebProjectRequestDto = {
        project_code: currentProject.value.project_code,
        project_name: currentProject.value.project_name,
        project_group: currentProject.value.project_group,
        git_repository: currentProject.value.git_repository,
        host_project_path: currentProject.value.host_project_path,
        container_project_path: currentProject.value.container_project_path,
        access_url: currentProject.value.access_url,
      };

      await agentCommandApi.value!.addWebProject(addWebProjectRequestDto);
      break;
    case 'Java':
      const addJavaProjectRequestDto: AddJavaProjectRequestDto = {
        project_code: currentProject.value.project_code,
        project_name: currentProject.value.project_name,
        project_group: currentProject.value.project_group,
        git_repository: currentProject.value.git_repository,
        docker_image_name: currentProject.value.docker_image_name,
        docker_image_tag: currentProject.value.docker_image_tag,
        container_name: currentProject.value.container_name,
        external_port: currentProject.value.external_port,
        internal_port: currentProject.value.internal_port,
        network: currentProject.value.network,
        jdk_version: currentProject.value.jdk_version,
        host_project_path: currentProject.value.host_project_path,
        container_project_path: currentProject.value.container_project_path
      };

      await agentCommandApi.value!.addJavaProject(addJavaProjectRequestDto);
      break;
    default:
      Notify.create({
        position: 'top',
        type: 'negative',
        message: '暂未实现',
      });
      return;
  }

  Notify.create({
    position: 'top',
    type: 'positive',
    message: '添加项目成功',
  });
  isCreateNewProjectDialogOpen.value = false;
  // 刷新项目列表
  projects.value = await agentCommandApi.value!.fetchProjectList();
};
// ========== ↑↑↑↑↑ 新增项目 ↑↑↑↑↑ ==========

onMounted(async () => {
  agentCommandApi.value = new AgentCommandApi(currentAgent.value!.id)
  projects.value = await agentCommandApi.value.fetchProjectList();
});

// 提取所有唯一的分组值，并过滤掉空值
const uniqueGroups = computed(() => {
  const groups = new Set(
    projects.value
      .map((project) => project.project_group) // 提取 group 字段
      .filter((group) => group) // 过滤掉空值（null、undefined、空字符串）
  );
  return ['所有', ...Array.from(groups)]; // 添加“所有”选项，并将其放在最前面
});

const filteredProjects = computed(() => {
  return projects.value
    .filter((project) => {
      const matchesType =
        filterType.value === '所有' ||
        project.project_type === filterType.value; // 匹配项目类型
      const matchesKeyword = project.project_name
        .toLowerCase()
        .includes(filterKeyword.value.toLowerCase()); // 匹配搜索词
      const matchesGroup =
        selectedGroup.value === '所有' ||
        project.project_group === selectedGroup.value; // 匹配分组
      return matchesType && matchesKeyword && matchesGroup;
    })
    .sort((a, b) => {
      const sortField = sortOrder.value;
      if (sortField === 'project_name') {
        return a.project_name.localeCompare(b.project_name);
      } else if (sortField === 'created_at') {
        return (
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
      } else if (sortField === 'updated_at') {
        return (
          new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime()
        );
      } else if (sortField === 'last_deployed_at') {
        return (
          new Date(a.last_deployed_at).getTime() -
          new Date(b.last_deployed_at).getTime()
        );
      } else if (sortField === 'project_type') {
        return a.project_type.localeCompare(b.project_type);
      }
      return 0;
    });
});
</script>

<style scoped>
.my-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>