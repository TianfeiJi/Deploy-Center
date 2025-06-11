// utils/bytesConverter.ts

/**
 * 将字节转换为合适的单位（KB、MB、GB）
 * @param bytes 字节数
 * @returns 转换后的字符串，例如 "1.23 KB" 或 "2.34 MB"
 */
export function formatBytes(bytes: number): string {
  if (bytes === null || bytes === undefined || isNaN(bytes)) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let unitIndex = 0;

  // 自动选择合适的单位
  while (bytes >= 1024 && unitIndex < units.length - 1) {
    bytes /= 1024;
    unitIndex++;
  }

  return `${bytes.toFixed(2)} ${units[unitIndex]}`; // 保留两位小数
}

/**
 * 将字节转换为 KB
 * @param bytes 字节数
 * @returns 转换后的 KB 值，格式为字符串
 */
export function bytesToKB(bytes: number): string {
  if (bytes === null || bytes === undefined || isNaN(bytes)) return '0 KB';
  const kb = bytes / 1024;
  return `${kb.toFixed(2)} KB`;
}

/**
 * 将字节转换为 MB
 * @param bytes 字节数
 * @returns 转换后的 MB 值，格式为字符串
 */
export function bytesToMB(bytes: number): string {
  if (bytes === null || bytes === undefined || isNaN(bytes)) return '0 MB';
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(2)} MB`;
}

/**
 * 将字节转换为 GB
 * @param bytes 字节数
 * @returns 转换后的 GB 值，格式为字符串
 */
export function bytesToGB(bytes: number): string {
  if (bytes === null || bytes === undefined || isNaN(bytes)) return '0 GB';
  const gb = bytes / (1024 * 1024 * 1024);
  return `${gb.toFixed(2)} GB`;
}
