import request from '../utils/request';
import { HttpResult } from "src/types/HttpResult";
import { User } from "src/types/User";

// 获取用户列表
export async function getUserList(): Promise<User[]> {
  const response = await request({
    url: '/api/deploy-center/user/list',
    method: 'get',
  });

  return response.data;
}

// 获取用户详情
export function getUser(user_id: number): Promise<HttpResult<User>> {
  return request({
    url: `/api/deploy-center/user/${user_id}`,
    method: 'get',
  });
}

// 创建用户
export function createUser(user_info: Partial<User>): Promise<HttpResult<User>> {
  return request({
    url: `/api/deploy-center/user/create`,
    method: 'post',
    data: user_info,
  });
}

// 更新用户信息
export function updateUser(user_id: number, updated_data: Partial<User>): Promise<HttpResult<User>> {
  return request({
    url: `/api/deploy-center/user/${user_id}`,
    method: 'put',
    data: updated_data,
  });
}

// 删除用户
export function deleteUser(user_id: number): Promise<HttpResult<User>> {
  return request({
    url: `/api/deploy-center/user/${user_id}`,
    method: 'delete',
  });
}