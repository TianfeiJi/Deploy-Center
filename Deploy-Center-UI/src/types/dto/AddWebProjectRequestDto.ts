export interface AddWebProjectRequestDto {
  project_code: string;
  project_name: string;
  project_group: string;
  git_repository?: string | null;
  host_project_path: string;
  container_project_path: string;
  access_url?: string | null;
}
