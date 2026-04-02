// utils/displayFormatter.ts

/**
 * 格式化耗时（毫秒）为可读文本
 *
 * 示例：
 * - 320 -> 320 ms
 * - 1200 -> 1.2秒
 * - 65000 -> 1分5秒
 * - 3660000 -> 1小时1分
 * - 90061000 -> 1天1小时
 */
export function formatDuration(durationMs?: number | null): string {
  if (durationMs == null || Number.isNaN(durationMs) || durationMs < 0) {
    return '-'
  }

  if (durationMs < 1000) {
    return `${Math.floor(durationMs)} ms`
  }

  const totalSeconds = durationMs / 1000

  if (totalSeconds < 60) {
    return `${totalSeconds.toFixed(1)} 秒`
  }

  const totalMinutes = Math.floor(totalSeconds / 60)
  const seconds = Math.floor(totalSeconds % 60)

  if (totalMinutes < 60) {
    if (seconds === 0) {
      return `${totalMinutes} 分`
    }
    return `${totalMinutes} 分 ${seconds} 秒`
  }

  const totalHours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60

  if (totalHours < 24) {
    if (minutes === 0) {
      return `${totalHours} 小时`
    }
    return `${totalHours} 小时 ${minutes} 分`
  }

  const days = Math.floor(totalHours / 24)
  const hours = totalHours % 24

  if (hours === 0) {
    return `${days} 天`
  }
  return `${days} 天 ${hours} 小时`
}