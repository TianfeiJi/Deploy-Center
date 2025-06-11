/**
 * Center对于Agent数据的CRUD
 */

import request from '../utils/request';
import { HttpResult } from 'src/types/HttpResult';
import { Agent } from 'src/types/Agent';
import { AxiosProgressEvent } from 'axios';

// 获取 Agent 列表
export function getAgentList(): Promise<HttpResult<Agent[]>> {
  return request({
    url: '/api/deploy-center/agent/list',
    method: 'get',
  });
}

// 获取 Agent 详情
export function getAgent(agentId: number): Promise<HttpResult<Agent>> {
  return request({
    url: `/api/deploy-center/agent/${agentId}`,
    method: 'get',
  });
}

// 注册 Agent
export function createAgent(agentData: any): Promise<HttpResult<Agent>> {
  return request({
    url: '/api/deploy-center/agent/register',
    method: 'post',
    data: agentData,
  });
}

// 更新 Agent 信息
export function updateAgent(
  agentId: number,
  updatedData: Partial<Agent>
): Promise<HttpResult<void>> {
  return request({
    url: `/api/deploy-center/agent/${agentId}`,
    method: 'put',
    data: updatedData,
  });
}

// 删除 Agent
export function deleteAgent(agentId: number): Promise<HttpResult<void>> {
  return request({
    url: `/api/deploy-center/agent/${agentId}`,
    method: 'delete',
  });
}

export async function callAgentApi(
  agentId: number,
  apiPath: string,
  method: string,
  jsonData?: any,
  formData?: FormData,
  config?: { onUploadProgress?: (event: AxiosProgressEvent) => void }
): Promise<HttpResult<any>> {
  const url = `/api/deploy-center/agent/${agentId}/call-api?api_path=${apiPath}&method=${method.toUpperCase()}`;

  let data: any;
  let headers: any = {};

  // 根据是否有 formData 或 jsonData 来决定如何构造请求体
  if (formData) {
    data = formData;
    headers['Content-Type'] = 'multipart/form-data';
  } else if (jsonData) {
    // 如果没有 FormData，但有 jsonData，直接使用 jsonData
    data = jsonData;
  } else {
    // 如果两者都没有，构造一个空对象
    data = {};
  }

  return request({
    url,
    method: 'POST',
    data,
    headers,
    ...config,
  });
}
