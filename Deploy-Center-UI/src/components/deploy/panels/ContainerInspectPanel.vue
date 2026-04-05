<template>
  <section class="container-inspect-panel">
    <template v-if="projectType === 'web'">
      <div class="empty-state-card">
        <div class="empty-state-title">当前项目无容器 Inspect 信息</div>
        <div class="empty-state-desc">
          Web 项目当前使用站点部署状态，不展示 Docker 容器 inspect 信息。
        </div>
      </div>
    </template>

    <template v-else-if="!containerName">
      <div class="empty-state-card">
        <div class="empty-state-title">未配置容器名称</div>
        <div class="empty-state-desc">
          当前项目未配置 container_name，无法查询容器 Inspect 信息。
        </div>
      </div>
    </template>

    <template v-else-if="loading">
      <div class="loading-state-card">
        <q-spinner color="primary" size="28px" />
        <div class="loading-state-text">加载容器 Inspect 信息中...</div>
      </div>
    </template>

    <template v-else-if="inspectRecord">
      <div class="panel-header">
        <div class="panel-header-left">
          <div class="panel-title">容器 Inspect</div>
          <div class="panel-subtitle">
            支持查看结构化容器配置与原始 docker inspect JSON 数据。
          </div>
        </div>

        <div class="panel-actions">
          <button
            v-if="activeView === 'raw'"
            class="action-btn action-btn-secondary"
            :disabled="loading"
            @click="copyRawJson"
          >
            复制 JSON
          </button>

          <button
            class="action-btn action-btn-secondary"
            :disabled="loading"
            @click="loadInspectInfo"
          >
            刷新
          </button>
        </div>
      </div>

      <div class="inner-tab-bar">
        <button
          class="inner-tab-btn"
          :class="{ active: activeView === 'structured' }"
          @click="activeView = 'structured'"
        >
          结构化视图
        </button>

        <button
          class="inner-tab-btn"
          :class="{ active: activeView === 'raw' }"
          @click="activeView = 'raw'"
        >
          原始 JSON
        </button>
      </div>

      <template v-if="activeView === 'structured'">
        <div class="section-block">
          <div class="section-title">基础信息</div>
          <div class="summary-grid">
            <div
              v-for="item in inspectSummaryItems"
              :key="item.key"
              class="summary-card"
            >
              <div class="summary-label">{{ item.label }}</div>
              <div
                class="summary-value"
                :title="item.value"
                @click="copyValue(item.value)"
              >
                {{ item.value }}
              </div>
            </div>
          </div>
        </div>

        <div class="structured-grid">
          <div class="structured-card">
            <div class="structured-card-title">环境变量</div>

            <template v-if="envItems.length > 0">
              <div class="kv-list">
                <div
                  v-for="item in envItems"
                  :key="item.key"
                  class="kv-item"
                >
                  <div class="kv-key" :title="item.key">{{ item.key }}</div>
                  <div
                    class="kv-value"
                    :title="item.value"
                    @click="copyValue(item.value)"
                  >
                    {{ item.value }}
                  </div>
                </div>
              </div>
            </template>

            <template v-else>
              <div class="empty-inline-text">暂无环境变量</div>
            </template>
          </div>

          <div class="structured-card">
            <div class="structured-card-title">启动配置</div>

            <div class="desc-list">
              <div class="desc-item">
                <div class="desc-label">启动程序</div>
                <div class="desc-value break-all" @click="copyValue(startPath)">
                  {{ startPath }}
                </div>
              </div>

              <div class="desc-item">
                <div class="desc-label">启动参数</div>
                <div class="desc-value break-all" @click="copyValue(startArgsText)">
                  {{ startArgsText }}
                </div>
              </div>

              <div class="desc-item">
                <div class="desc-label">Entrypoint</div>
                <div class="desc-value break-all" @click="copyValue(entrypointText)">
                  {{ entrypointText }}
                </div>
              </div>

              <div class="desc-item">
                <div class="desc-label">Cmd</div>
                <div class="desc-value break-all" @click="copyValue(cmdText)">
                  {{ cmdText }}
                </div>
              </div>

              <div class="desc-item">
                <div class="desc-label">工作目录</div>
                <div class="desc-value break-all" @click="copyValue(workingDirText)">
                  {{ workingDirText }}
                </div>
              </div>
            </div>
          </div>

          <div class="structured-card">
            <div class="structured-card-title">挂载目录</div>

            <template v-if="mountItems.length > 0">
              <div class="mount-list">
                <div
                  v-for="(mount, index) in mountItems"
                  :key="`${mount.source}-${mount.destination}-${index}`"
                  class="mount-item"
                >
                  <div class="mount-row">
                    <span class="mount-label">源路径</span>
                    <span class="mount-value break-all" @click="copyValue(mount.source)">
                      {{ mount.source }}
                    </span>
                  </div>
                  <div class="mount-row">
                    <span class="mount-label">目标路径</span>
                    <span class="mount-value break-all" @click="copyValue(mount.destination)">
                      {{ mount.destination }}
                    </span>
                  </div>
                  <div class="mount-row mount-row-meta">
                    <span class="mount-chip">模式 {{ mount.mode }}</span>
                    <span class="mount-chip">{{ mount.rw }}</span>
                    <span class="mount-chip">{{ mount.type }}</span>
                  </div>
                </div>
              </div>
            </template>

            <template v-else>
              <div class="empty-inline-text">暂无挂载目录</div>
            </template>
          </div>

          <div class="structured-card">
            <div class="structured-card-title">网络配置</div>

            <div class="desc-list">
              <div class="desc-item">
                <div class="desc-label">网络模式</div>
                <div class="desc-value" @click="copyValue(networkModeText)">
                  {{ networkModeText }}
                </div>
              </div>

              <div class="desc-item">
                <div class="desc-label">IP 地址</div>
                <div class="desc-value" @click="copyValue(ipAddressText)">
                  {{ ipAddressText }}
                </div>
              </div>

              <div class="desc-item">
                <div class="desc-label">网络名称</div>
                <div class="desc-value break-all" @click="copyValue(networkNamesText)">
                  {{ networkNamesText }}
                </div>
              </div>

              <div class="desc-item">
                <div class="desc-label">端口映射</div>
                <div class="desc-value break-all" @click="copyValue(portBindingsText)">
                  {{ portBindingsText }}
                </div>
              </div>
            </div>
          </div>

          <div class="structured-card">
            <div class="structured-card-title">重启与运行策略</div>

            <div class="desc-list">
              <div class="desc-item">
                <div class="desc-label">重启策略</div>
                <div class="desc-value" @click="copyValue(restartPolicyText)">
                  {{ restartPolicyText }}
                </div>
              </div>

              <div class="desc-item">
                <div class="desc-label">是否自动移除</div>
                <div class="desc-value" @click="copyValue(autoRemoveText)">
                  {{ autoRemoveText }}
                </div>
              </div>

              <div class="desc-item">
                <div class="desc-label">是否特权模式</div>
                <div class="desc-value" @click="copyValue(privilegedText)">
                  {{ privilegedText }}
                </div>
              </div>

              <div class="desc-item">
                <div class="desc-label">只读根文件系统</div>
                <div class="desc-value" @click="copyValue(readonlyRootfsText)">
                  {{ readonlyRootfsText }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="json-block">
          <div class="json-block-header">
            <div class="json-block-title">原始 docker inspect 数据</div>
          </div>

          <pre class="json-content">{{ formattedInspectJson }}</pre>
        </div>
      </template>
    </template>

    <template v-else>
      <div class="empty-state-card">
        <div class="empty-state-title">暂无容器 Inspect 信息</div>
        <div class="empty-state-desc">
          当前项目未查询到容器 Inspect 信息。
        </div>

        <button
          class="action-btn action-btn-secondary"
          :disabled="loading"
          @click="loadInspectInfo"
        >
          重试
        </button>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Notify, copyToClipboard } from 'quasar'
import { provideCurrentAgentProxyApi } from 'src/factory/agentProxyApiFactory'

export type DockerContainerInspectRecord = Record<string, any>

type ProjectLike = {
  id?: string | number
  project_type?: string
  container_name?: string
}

type SummaryItem = {
  key: string
  label: string
  value: string
}

type KvItem = {
  key: string
  value: string
}

type MountItem = {
  source: string
  destination: string
  mode: string
  rw: string
  type: string
}

const props = defineProps<{
  project: ProjectLike
}>()

const loading = ref(false)
const inspectRecord = ref<DockerContainerInspectRecord | null>(null)
const activeView = ref<'structured' | 'raw'>('structured')

const projectType = computed(() => {
  return String(props.project.project_type || '').toLowerCase().trim()
})

const containerName = computed(() => {
  return String(props.project.container_name || '').trim()
})

const formattedInspectJson = computed(() => {
  if (!inspectRecord.value) return ''
  try {
    return JSON.stringify(inspectRecord.value, null, 2)
  } catch {
    return ''
  }
})

function formatDisplayValue(value: unknown): string {
  if (value == null || value === '') return '-'
  if (Array.isArray(value)) {
    if (value.length === 0) return '-'
    return value.map(item => String(item)).join(' ')
  }
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value)
    } catch {
      return String(value)
    }
  }
  return String(value)
}

const inspectSummaryItems = computed<SummaryItem[]>(() => {
  const inspect = inspectRecord.value
  if (!inspect) return []

  return [
    { key: 'Id', label: '容器 ID', value: formatDisplayValue(inspect.Id) },
    { key: 'Name', label: '容器名称', value: formatDisplayValue(inspect.Name) },
    { key: 'Created', label: '创建时间', value: formatDisplayValue(inspect.Created) },
    { key: 'Image', label: '镜像 ID', value: formatDisplayValue(inspect.Image) },
    {
      key: 'Config.Image',
      label: '镜像名称',
      value: formatDisplayValue(inspect.Config?.Image),
    },
    {
      key: 'State.Status',
      label: '状态',
      value: formatDisplayValue(inspect.State?.Status),
    },
    {
      key: 'State.Running',
      label: '是否运行中',
      value: inspect.State?.Running == null ? '-' : String(inspect.State.Running),
    },
    {
      key: 'State.ExitCode',
      label: '退出码',
      value: inspect.State?.ExitCode == null ? '-' : String(inspect.State.ExitCode),
    },
    {
      key: 'RestartCount',
      label: '重启次数',
      value: inspect.RestartCount == null ? '-' : String(inspect.RestartCount),
    },
    {
      key: 'Path',
      label: '启动程序',
      value: formatDisplayValue(inspect.Path),
    },
    {
      key: 'HostConfig.NetworkMode',
      label: '网络模式',
      value: formatDisplayValue(inspect.HostConfig?.NetworkMode),
    },
    {
      key: 'NetworkSettings.IPAddress',
      label: 'IP 地址',
      value: formatDisplayValue(inspect.NetworkSettings?.IPAddress),
    },
    {
      key: 'Mounts',
      label: '挂载数量',
      value: Array.isArray(inspect.Mounts) ? String(inspect.Mounts.length) : '-',
    },
  ]
})

const envItems = computed<KvItem[]>(() => {
  const envList = inspectRecord.value?.Config?.Env
  if (!Array.isArray(envList)) return []

  return envList.map((item: string) => {
    const index = item.indexOf('=')
    if (index === -1) {
      return { key: item, value: '-' }
    }
    return {
      key: item.slice(0, index),
      value: item.slice(index + 1) || '-',
    }
  })
})

const mountItems = computed<MountItem[]>(() => {
  const mounts = inspectRecord.value?.Mounts
  if (!Array.isArray(mounts)) return []

  return mounts.map((mount: Record<string, any>) => ({
    source: formatDisplayValue(mount.Source),
    destination: formatDisplayValue(mount.Destination),
    mode: formatDisplayValue(mount.Mode),
    rw: mount.RW == null ? '-' : mount.RW ? '读写' : '只读',
    type: formatDisplayValue(mount.Type),
  }))
})

const startPath = computed(() => {
  return formatDisplayValue(inspectRecord.value?.Path)
})

const startArgsText = computed(() => {
  return formatDisplayValue(inspectRecord.value?.Args)
})

const entrypointText = computed(() => {
  return formatDisplayValue(inspectRecord.value?.Config?.Entrypoint)
})

const cmdText = computed(() => {
  return formatDisplayValue(inspectRecord.value?.Config?.Cmd)
})

const workingDirText = computed(() => {
  return formatDisplayValue(inspectRecord.value?.Config?.WorkingDir)
})

const networkModeText = computed(() => {
  return formatDisplayValue(inspectRecord.value?.HostConfig?.NetworkMode)
})

const ipAddressText = computed(() => {
  const inspect = inspectRecord.value
  if (!inspect) return '-'

  const directIp = inspect.NetworkSettings?.IPAddress
  if (directIp) return String(directIp)

  const networks = inspect.NetworkSettings?.Networks
  if (networks && typeof networks === 'object') {
    const ips = Object.values(networks)
      .map((item: any) => item?.IPAddress)
      .filter(Boolean)

    if (ips.length > 0) {
      return ips.join(', ')
    }
  }

  return '-'
})

const networkNamesText = computed(() => {
  const networks = inspectRecord.value?.NetworkSettings?.Networks
  if (!networks || typeof networks !== 'object') return '-'

  const names = Object.keys(networks)
  return names.length > 0 ? names.join(', ') : '-'
})

const portBindingsText = computed(() => {
  const ports = inspectRecord.value?.NetworkSettings?.Ports
  if (!ports || typeof ports !== 'object') return '-'

  const result: string[] = []

  Object.entries(ports).forEach(([containerPort, bindings]) => {
    if (!bindings) {
      result.push(`${containerPort} -> 未映射`)
      return
    }

    if (Array.isArray(bindings) && bindings.length > 0) {
      bindings.forEach((binding: any) => {
        const hostIp = binding?.HostIp || '0.0.0.0'
        const hostPort = binding?.HostPort || '-'
        result.push(`${containerPort} -> ${hostIp}:${hostPort}`)
      })
    } else {
      result.push(`${containerPort} -> 未映射`)
    }
  })

  return result.length > 0 ? result.join('；') : '-'
})

const restartPolicyText = computed(() => {
  const restartPolicy = inspectRecord.value?.HostConfig?.RestartPolicy
  if (!restartPolicy) return '-'

  const name = restartPolicy.Name || '-'
  const maxRetryCount = restartPolicy.MaximumRetryCount

  if (name === 'on-failure' && maxRetryCount != null) {
    return `${name} (${maxRetryCount})`
  }

  return String(name)
})

const autoRemoveText = computed(() => {
  const value = inspectRecord.value?.HostConfig?.AutoRemove
  if (value == null) return '-'
  return value ? '是' : '否'
})

const privilegedText = computed(() => {
  const value = inspectRecord.value?.HostConfig?.Privileged
  if (value == null) return '-'
  return value ? '是' : '否'
})

const readonlyRootfsText = computed(() => {
  const value = inspectRecord.value?.HostConfig?.ReadonlyRootfs
  if (value == null) return '-'
  return value ? '是' : '否'
})

async function copyValue(value?: string) {
  const text = String(value || '').trim()
  if (!text || text === '-') return

  try {
    await copyToClipboard(text)
    Notify.create({
      type: 'positive',
      message: '已复制',
      position: 'top',
      timeout: 1000,
    })
  } catch {
    Notify.create({
      type: 'negative',
      message: '复制失败',
      position: 'top',
      timeout: 1000,
    })
  }
}

async function copyRawJson() {
  if (!formattedInspectJson.value) return

  try {
    await copyToClipboard(formattedInspectJson.value)
    Notify.create({
      type: 'positive',
      message: 'Inspect JSON 已复制',
      position: 'top',
      timeout: 1200,
    })
  } catch {
    Notify.create({
      type: 'negative',
      message: '复制 JSON 失败',
      position: 'top',
      timeout: 1200,
    })
  }
}

async function loadInspectInfo() {
  if (projectType.value === 'web') {
    inspectRecord.value = null
    return
  }

  const currentContainerName = containerName.value
  if (!currentContainerName) {
    inspectRecord.value = null
    return
  }

  loading.value = true
  try {
    const res = await provideCurrentAgentProxyApi().fetchDockerContainerInspect(currentContainerName)
    inspectRecord.value = res || null
  } catch (error) {
    console.error('loadInspectInfo error:', error)
    inspectRecord.value = null
    Notify.create({
      type: 'negative',
      message: '加载容器 Inspect 信息失败',
      position: 'top',
    })
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.project.id, props.project.project_type, props.project.container_name],
  async () => {
    activeView.value = 'structured'
    await loadInspectInfo()
  },
  { immediate: true }
)
</script>

<style scoped>
.container-inspect-panel {
  min-height: 320px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 14px;
}

.panel-header-left {
  min-width: 0;
  flex: 1;
}

.panel-title {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
}

.panel-subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.action-btn {
  border: none;
  border-radius: 12px;
  height: 36px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s ease;
}

.action-btn-secondary {
  background: #fff;
  color: #334155;
  border: 1px solid #dbe4ee;
}

.action-btn-secondary:hover:not(:disabled) {
  border-color: #bfd2ff;
  color: #2563eb;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.08);
}

.action-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.inner-tab-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  margin-bottom: 14px;
  border-radius: 16px;
  background: rgba(248, 250, 252, 0.9);
  border: 1px solid #e5e7eb;
  overflow-x: auto;
}

.inner-tab-btn {
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
  padding: 10px 14px;
  border-radius: 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.18s ease;
}

.inner-tab-btn:hover {
  color: #0284c7;
  background: rgba(14, 165, 233, 0.06);
}

.inner-tab-btn.active {
  color: #0284c7;
  background: #ffffff;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
}

.section-block + .section-block {
  margin-top: 16px;
}

.section-title {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 800;
  color: #0f172a;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}

.summary-card,
.structured-card {
  border-radius: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e5e7eb;
  padding: 14px 16px;
  min-width: 0;
  transition: box-shadow 0.18s ease, border-color 0.18s ease;
}

.summary-card:hover,
.structured-card:hover {
  border-color: #dbeafe;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
}

.summary-label {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 13px;
  line-height: 1.7;
  color: #334155;
  word-break: break-all;
  cursor: pointer;
  transition: color 0.18s ease;
}

.summary-value:hover,
.desc-value:hover,
.kv-value:hover,
.mount-value:hover {
  color: #2563eb;
}

.structured-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.structured-card-title {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 800;
  color: #0f172a;
}

.desc-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.desc-item {
  min-width: 0;
}

.desc-label {
  margin-bottom: 6px;
  font-size: 12px;
  color: #94a3b8;
}

.desc-value {
  font-size: 13px;
  line-height: 1.7;
  color: #334155;
  word-break: break-word;
  cursor: pointer;
}

.kv-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 420px;
  overflow-y: auto;
  padding-right: 2px;
}

.kv-item {
  border-radius: 12px;
  background: rgba(248, 250, 252, 0.72);
  border: 1px solid #eef2f7;
  padding: 10px 12px;
}

.kv-key {
  font-size: 12px;
  color: #64748b;
  font-weight: 700;
  line-height: 1.5;
  word-break: break-all;
}

.kv-value {
  margin-top: 4px;
  font-size: 12px;
  color: #334155;
  line-height: 1.7;
  word-break: break-all;
  cursor: pointer;
}

.mount-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mount-item {
  border-radius: 12px;
  background: rgba(248, 250, 252, 0.72);
  border: 1px solid #eef2f7;
  padding: 12px;
}

.mount-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mount-row + .mount-row {
  margin-top: 8px;
}

.mount-label {
  font-size: 12px;
  color: #94a3b8;
}

.mount-value {
  font-size: 12px;
  line-height: 1.7;
  color: #334155;
  cursor: pointer;
}

.mount-row-meta {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 8px;
}

.mount-chip {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid #dbeafe;
}

.empty-inline-text {
  font-size: 13px;
  color: #94a3b8;
  line-height: 1.7;
}

.json-block {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: #0f172a;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.json-block-header {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.08);
  background: rgba(255, 255, 255, 0.03);
}

.json-block-title {
  font-size: 13px;
  font-weight: 700;
  color: #cbd5e1;
}

.json-content {
  margin: 0;
  padding: 16px;
  font-size: 12px;
  line-height: 1.7;
  color: #e2e8f0;
  overflow: auto;
  max-height: 70vh;
  white-space: pre-wrap;
  word-break: break-word;
}

.break-all {
  word-break: break-all;
}

.empty-state-card,
.loading-state-card {
  min-height: 280px;
  border-radius: 20px;
  border: 1px dashed #cbd5e1;
  background: rgba(255, 255, 255, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #64748b;
  gap: 10px;
  text-align: center;
  padding: 24px;
}

.empty-state-title {
  font-size: 18px;
  font-weight: 700;
  color: #334155;
}

.empty-state-desc,
.loading-state-text {
  font-size: 14px;
  color: #64748b;
  line-height: 1.7;
  max-width: 560px;
}

@media (max-width: 960px) {
  .structured-grid,
  .summary-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    align-items: stretch;
  }

  .panel-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .json-content {
    max-height: 56vh;
  }

  .inner-tab-bar {
    padding: 6px;
  }
}
</style>