// src/types/Agent.ts
export interface Agent {
  id: number;
  name: string;
  ip: string;
  port: number;
  service_url: string;
  os: string;
  type: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}