// 定义 Web 项目类型
export interface WebProject {
  id: string;
  project_type: 'Web'; // 项目类型固定为 'Web'
  project_code: string; // 项目代号
  project_name: string; // 项目名称
  project_group: string; // 项目组别
  host_project_path: string; // 宿主机项目路径
  container_project_path: string; // 容器项目路径
  git_repository: string; // Git地址
  access_url: string; // 访问地址
  created_at: string;
  updated_at: string;
  last_deployed_at: string;
}

// 定义 Java 项目类型
export interface JavaProject {
  id: string;
  project_type: 'Java';
  project_code: string; // 项目代号
  project_name: string; // 项目名称
  project_group: string; // 项目组别
  docker_image_name: string; // Docker 镜像名称
  docker_image_tag: string; // Docker 镜像标签
  container_name: string; // 容器名称
  external_port: number; // 外部端口
  internal_port: number; // 内部端口
  network?: string;
  jdk_version?: number;
  host_project_path: string; // 宿主机项目路径
  container_project_path: string; // 容器项目路径
  git_repository: string; // Git地址
  created_at: string;
  updated_at: string;
  last_deployed_at: string;
}

// 定义 Python 项目类型
export interface PythonProject {
  id: string;
  project_type: 'Python'; // 项目类型固定为 'Python'
  project_code: string; // 项目代号
  project_name: string; // 项目名称
  project_group: string; // 项目组别
  docker_image_name: string; // Docker 镜像名称
  docker_image_tag: string; // Docker 镜像标签
  container_name: string; // 容器名称
  external_port: number; // 外部端口
  internal_port: number; // 内部端口
  network: string;
  python_version: string;
  framework: string;
  host_project_path: string; // 宿主机项目路径
  container_project_path: string; // 容器项目路径
  git_repository: string; // Git地址
  created_at: string;
  updated_at: string;
  last_deployed_at: string;
}
