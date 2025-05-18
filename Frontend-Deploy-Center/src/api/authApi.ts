// api/authApi.ts
import request from '../utils/request';
import {HttpResult} from "src/types/HttpResult";
import {UserLoginRequestDto} from "src/types/dto/UserLoginRequestDto";

// 登录
export function login(userLoginRequestDto: UserLoginRequestDto): Promise<HttpResult<{ user_id: number; token: string }>> {
  return request({
    url: '/api/deploy-center/auth/login',
    method: 'post',
    data: userLoginRequestDto,
  });
}

// 退出登录
export function logout(): Promise<any> {
  return request({
    url: '/api/deploy-center/auth/logout',
    method: 'post'
  });
}
