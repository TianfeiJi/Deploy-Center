import { DeployHistory } from "src/types/DeployHistory";

export interface DeployHistoryVo extends DeployHistory {
  project_code: string;
  project_name: string;
}
