// utils/dateFormatter.ts

/**
 * 格式化时间：2025-03-08T21:50:01 → 2025-03-08 21:50:01
 */
export function formatDate(isoDate?: string | null): string {
  if (!isoDate) return '-'

  const date = new Date(isoDate)
  if (isNaN(date.getTime())) return '-'

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 相对时间：xx秒 / xx分钟 / xx小时 / xx天
 */
export function formatTimeAgo(isoDate?: string | null): string {
  if (!isoDate) return '-'

  const now = new Date()
  const past = new Date(isoDate)

  const diff = now.getTime() - past.getTime()
  if (isNaN(diff) || diff < 0) return '-'

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days > 0) return `${days}天`

  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  if (hours > 0) return `${hours}小时`

  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  if (minutes > 0) return `${minutes}分钟`

  const seconds = Math.floor((diff % (1000 * 60)) / 1000)
  return `${seconds}秒`
}