import request from 'src/utils/request';
import { HttpResult } from 'src/types/HttpResult';

// 查询用户是否已绑定 2FA
export async function getTwoFactorStatus(username: string): Promise<{ data: boolean }> {
  const response = await request({
    url: `/api/deploy-center/2fa/status/${username}`,
    method: 'get'
  });
  return response.data;
}

// 获取用户绑定二维码（首次绑定时使用）
export function setupTwoFactor(username: string): Promise<HttpResult<any>> {
  return request({
    url: `/api/deploy-center/2fa/setup/${username}`,
    method: 'get'
  });
}

// 验证用户输入的 2FA 验证码是否正确（可用于扫码后测试）
export function verifyTwoFactorCode(username: string, code: string): Promise<HttpResult<boolean>> {
  return request({
    url: '/api/deploy-center/2fa/verify',
    method: 'post',
    data: { username, code }
  });
}
  