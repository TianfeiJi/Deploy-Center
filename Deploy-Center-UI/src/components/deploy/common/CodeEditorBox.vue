<template>
  <div class="code-editor-box" :class="{ disabled }" :style="boxStyle">
    <div ref="linePanelRef" class="line-number-panel">
      <div
        v-for="n in displayLineCount"
        :key="n"
        class="line-number"
      >
        {{ n }}
      </div>
    </div>

    <textarea
      ref="textareaRef"
      class="code-editor-textarea"
      :value="modelValue"
      :disabled="disabled"
      :style="textareaStyle"
      spellcheck="false"
      @input="handleInput"
      @scroll="syncScroll"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const LINE_HEIGHT = 22
const VERTICAL_PADDING = 24

const props = withDefaults(
  defineProps<{
    modelValue: string
    disabled?: boolean
    minRows?: number
    maxRows?: number
  }>(),
  {
    disabled: false,
    minRows: 12,
    maxRows: 16,
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)
const linePanelRef = ref<HTMLElement | null>(null)

const actualLineCount = computed(() => {
  return (props.modelValue || '').split('\n').length
})

const displayLineCount = computed(() => {
  return Math.max(actualLineCount.value, props.minRows)
})

const clampedRows = computed(() => {
  const rows = Math.max(actualLineCount.value, props.minRows)
  return Math.min(rows, props.maxRows)
})

const editorHeight = computed(() => {
  return clampedRows.value * LINE_HEIGHT + VERTICAL_PADDING
})

const boxStyle = computed(() => {
  return {
    height: `${editorHeight.value}px`,
  }
})

const textareaStyle = computed(() => {
  return {
    height: `${editorHeight.value}px`,
  }
})

function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}

function syncScroll(event: Event) {
  const target = event.target as HTMLTextAreaElement
  if (linePanelRef.value) {
    linePanelRef.value.scrollTop = target.scrollTop
  }
}
</script>

<style scoped>
.code-editor-box {
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr);
  border: 1px solid #dbe4ee;
  border-radius: 14px;
  overflow: hidden;
  background: #0f172a;
}

.code-editor-box.disabled {
  opacity: 0.72;
}

.line-number-panel {
  overflow: hidden;
  padding: 12px 0;
  background: #111827;
  border-right: 1px solid rgba(148, 163, 184, 0.16);
}

.line-number {
  height: 22px;
  line-height: 22px;
  text-align: right;
  padding-right: 12px;
  font-size: 12px;
  color: #64748b;
  font-family: Consolas, Monaco, monospace;
  user-select: none;
}

.code-editor-textarea {
  width: 100%;
  border: none;
  outline: none;
  resize: none;
  padding: 12px 14px;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 13px;
  line-height: 22px;
  font-family: Consolas, Monaco, monospace;
  white-space: pre;
  overflow: auto;
  tab-size: 2;
  box-sizing: border-box;
}
</style>