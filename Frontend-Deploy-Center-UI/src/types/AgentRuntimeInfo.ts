// Agent 运行时信息
export interface AgentRuntimeInfo {
  health: string;
  agent_version: string;
  product_name?: string;
  sys_vendor?: string;
  hostname?: string;
  os?: string;
  arch?: string;
  docker_version?: string;
  python_version?: string;
  fetched_at?: string;
}