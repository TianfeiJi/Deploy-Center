export type DeployTaskStatus =
  | "PENDING"
  | "UPLOADING"
  | "BUILDING"
  | "DEPLOYING"
  | "SUCCESS"
  | "FAILED"
  | "CANCELLED";

export type DeployTriggerType = "MANUAL" | "SCHEDULED";

export type DeployMechanism = "UPLOAD" | "CLOUD_BUILD";

export interface DeployTask {
  id: string;
  project_id: string;

  task_name?: string;

  status: DeployTaskStatus;

  trigger_type: DeployTriggerType;
  deploy_mechanism: DeployMechanism;

  upload_file_name?: string;
  upload_file_path?: string;

  build_image_name?: string;
  build_image_tag?: string;
  container_name?: string;

  dockerfile_content?: string;
  dockercommand_content?: string;

  started_at?: string;   // ISO datetime string
  finished_at?: string;  // ISO datetime string
  duration_ms?: number;

  failed_reason?: string;

  operator_name?: string;
  operator_id?: number;

  created_at?: string;   // ISO datetime string
  updated_at?: string;   // ISO datetime string
}