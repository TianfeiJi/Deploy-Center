export interface AddJavaProjectRequestDto {
  project_code: string;
  project_name: string;
  project_group: string;
  git_repository?: string | null;
  docker_image_name: string;
  docker_image_tag: string;
  external_port: number;
  internal_port: number;
  network: string;
  jdk_version: number;
  host_project_path: string;
  container_project_path: string;
}
