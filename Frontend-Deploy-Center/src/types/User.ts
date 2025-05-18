// src/types/User.ts
export interface User {
  id: number; // 用户ID
  username: string; // 用户名
  password: string; // 密码（通常存储为哈希值）
  nickname: string; // 昵称
  avatar: string; // 头像URL
  email: string; // 邮箱
  role: string; // 用户角色
  permissions: string[] | null; // 用户权限列表
  two_factor_secret: string | null; // 2FA的Secret
  status: string; // 用户状态
  created_at?: Date | null; // 创建时间
  updated_at?: Date | null; // 更新时间
}
