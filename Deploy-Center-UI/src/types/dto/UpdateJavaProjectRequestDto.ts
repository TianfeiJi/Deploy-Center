// src/types/UpdateJavaProjectRequestDto.ts
export interface UpdateJavaProjectRequestDto {
  id: string; // 项目的唯一标识符
  project_code?: string;
  project_name?: string;
  project_group?: string;
  docker_image_name?: string;
  docker_image_tag?: string;
  container_name?: string;
  external_port?: number;
  internal_port?: number;
  network?: string;
  jdk_version?: number;
  host_project_path?: string; // 宿主机项目路径
  container_project_path?: string; // 容器项目路径
  git_repository?: string; // Git地址
  // 其他需要更新的字段
}
