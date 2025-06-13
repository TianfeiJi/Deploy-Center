// utils/dateFormatter.ts

/**
 * 将 ISO 格式的日期时间字符串转换为易读的格式
 * @param isoDate ISO 格式的日期时间字符串（如 2025-03-08T21:50:01.897481）
 * @returns 格式化后的日期时间字符串（如 2025-03-08 21:50:01）
 */
export function formatDate(isoDate: string): string {
  if (!isoDate) return '';
  
  const date = new Date(isoDate);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0'); // 月份从 0 开始，需要加 1
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}
