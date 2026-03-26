<template>
  <main class="workspace">
    <div class="workspace-card">
      <div class="workspace-header">
        <div>
          <div class="workspace-title">项目部署控制台</div>
          <div class="workspace-subtitle">
            {{ projectName }}<span class="dot">·</span>{{ projectGroup }}
          </div>
        </div>
        <button class="ui-btn ui-btn-secondary" @click="$emit('refresh')">
          刷新
        </button>
      </div>

      <div class="tab-bar">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active:activeTab === tab.key }"
          @click="$emit('update:active', tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="workspace-body">
        <slot />
      </div>
    </div>
  </main>
</template>

<script setup>
defineProps({
  projectName: String,
  projectGroup: String,
  activeTab: String,
  tabs: { type: Array, required: true },
})
defineEmits(['update:active', 'refresh'])
</script>

<style scoped>
.workspace { min-width:0; }
.workspace-card { height:100%; display:flex; flex-direction:column; border-radius:24px; background:rgba(255,255,255,0.92); border:1px solid rgba(15,23,42,0.08); box-shadow:0 14px 36px rgba(15,23,42,0.06); overflow:hidden; }
.workspace-header { display:flex; align-items:center; justify-content:space-between; gap:16px; padding:18px 20px 12px; border-bottom:1px solid rgba(226,232,240,0.8); }
.workspace-title { font-size:22px; font-weight:800; color:#0f172a; line-height:1.2; }
.workspace-subtitle { margin-top:6px; font-size:13px; color:#64748b; }
.dot { margin:0 8px; font-size:28px; line-height:1; vertical-align:middle; }
.tab-bar { display:flex; gap:8px; padding:12px 16px 0; border-bottom:1px solid rgba(226,232,240,0.72); overflow-x:auto; }
.tab-btn { position:relative; border:none; background:transparent; color:#64748b; font-size:14px; font-weight:700; padding:10px 14px 12px; border-radius:12px 12px 0 0; cursor:pointer; white-space:nowrap; }
.tab-btn.active { color:#0284c7; background:rgba(14,165,233,0.06); }
.tab-btn.active::after { content:''; position:absolute; left:12px; right:12px; bottom:0; height:2px; border-radius:999px; background:#0ea5e9; }
.workspace-body { flex:1; min-height:0; padding:16px; }

.ui-btn { border:none; border-radius:12px; height:38px; padding:0 14px; font-size:13px; font-weight:700; }
.ui-btn-secondary { background:#fff; color:#334155; border:1px solid #dbe4ee; }
</style>