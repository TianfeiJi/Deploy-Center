import { SystemConfig } from 'src/types/SystemConfig';
import request from '../utils/request';
import { HttpResult } from "src/types/HttpResult";

// 获取所有系统配置列表
export async function getSystemConfigList(): Promise<any> {
  const response = await request({
    url: '/api/deploy-center/system-config/list',
    method: 'get',
  });
  return response.data
}

// 获取系统配置详情
export async function getSystemConfig(key: string): Promise<SystemConfig> {
  const response = await request({
    url: `/api/deploy-center/system-config/${key}`,
    method: 'get',
  });
  return response.data
}

// 更新配置项
export async function updateSystemConfig(key: string,  updatedData: Partial<SystemConfig>): Promise<HttpResult<null>> {
  const response = await request({
    url: `/api/deploy-center/system-config/${key}`,
    method: 'put',
    data: updatedData,
  });
  return response.data
}

// 删除配置项
export async function deleteSystemConfig(key: string): Promise<HttpResult<null>> {
  const response = await request({
    url: `/api/deploy-center/system-config/${key}`,
    method: 'delete',
  });
  return response.data
}