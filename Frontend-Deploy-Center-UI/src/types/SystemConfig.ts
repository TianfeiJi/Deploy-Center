export interface SystemConfig {
    id: number
    config_name: string
    config_key: string
    config_value: string | number | boolean
    config_remark: string
    config_group: string
    created_at?: Date | null; // 创建时间
    updated_at?: Date | null; // 更新时间
  }