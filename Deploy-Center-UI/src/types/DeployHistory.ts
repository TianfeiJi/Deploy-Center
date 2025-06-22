export interface DeployHistory {
  id: number;
  project_id: string;
  status: string;
  failed_reason?: string;
  operator_name: string;
  created_at: string;
  created_by: string;
  updated_at?: string;
  updated_by?: string;
}