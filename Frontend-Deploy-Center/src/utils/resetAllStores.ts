// src/utils/resetAllStores.ts
import { getActivePinia, Store } from 'pinia'

export function resetAllStores() {
  const activePinia = getActivePinia()
  if (!activePinia) {
    console.warn('[resetAllStores] 未检测到激活的 Pinia 实例')
    return
  }

  const stores = (activePinia as any)._s as Map<string, Store>

  console.group('[resetAllStores] 正在重置所有 store')
  stores.forEach((store) => {
    if (typeof store.$reset === 'function') {
      console.log(`已重置 store：${store.$id}`)
      store.$reset()
    } else {
      console.warn(`store "${store.$id}" 没有实现 $reset()，已跳过`)
    }
  })
  console.groupEnd()
}
