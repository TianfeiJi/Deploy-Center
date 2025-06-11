// src/types/UpdatePythonProjectRequestDto.ts
export interface UpdatePythonProjectRequestDto {
  id: string; // 项目的唯一标识符
  project_code?: string;
  project_name?: string;
  project_group?: string;
  docker_image_name?: string;
  docker_image_tag?: string;
  external_port?: number;
  internal_port?: number;
  network?: string;
  host_project_path?: string; // 宿主机项目路径
  container_project_path?: string; // 容器项目路径
  git_repository?: string; // Git地址
  status?: string; // 项目状态
  // 其他需要更新的字段
}
