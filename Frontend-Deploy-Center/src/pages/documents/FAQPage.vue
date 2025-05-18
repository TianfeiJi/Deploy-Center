<template>
  <q-page class="q-pa-md flex flex-center" style="align-items: flex-start">
    <q-card class="q-pa-xl" style="width: 100%; box-shadow: 0 8px 24px rgba(0,0,0,0.05); border-radius: 12px;">
      <!-- Header -->
      <div class="column items-center q-mb-lg">
        <div class="title">Frequently Asked Questions</div>
        <div class="version">Learn more about Deploy Center’s design and usage</div>
      </div>

      <!-- 语言切换 -->
      <div class="row justify-center q-mb-md">
        <q-btn flat dense label="中文" :color="language === 'zh' ? 'primary' : 'grey-6'" class="q-mr-sm"
          @click="setLanguage('zh')" />
        <q-btn flat dense no-caps label="English" :color="language === 'en' ? 'primary' : 'grey-6'"
          @click="setLanguage('en')" />
      </div>

      <!-- 简介 -->
      <div class="description q-mb-xl">
        {{ language === 'zh'
          ? '以下是关于 Deploy Center 的常见问题解答，内容将根据用户反馈持续补充与完善。'
          : 'Below are frequently asked questions about Deploy Center. This section will be continuously updated and expanded based on user feedback.'
        }}
      </div>

      <!-- FAQ 列表 -->
      <q-list bordered separator>
        <q-item v-for="(qa, i) in faqList" :key="i" class="q-py-md items-start">
          <q-item-section avatar>
            <q-avatar color="grey-3" text-color="grey-9" size="32px">
              Q{{ i + 1 }}
            </q-avatar>
          </q-item-section>

          <q-item-section>
            <q-item-label class="question">{{ qa.question }}</q-item-label>
            <!-- 使用v-md-preview库显示md文本 -->
            <v-md-preview :text="qa.answer" />
          </q-item-section>
        </q-item>
      </q-list>

    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import zhRaw from 'src/assets/docs/zh/faq_zh.md?raw'
import enRaw from 'src/assets/docs/en/faq_en.md?raw'

type QA = { question: string; answer: string }

const language = ref<'zh' | 'en'>('en')
const faqList = ref<QA[]>([])

function parseMarkdownFaq(raw: string): { question: string; answer: string }[] {
  const pattern = /^##\s+Q\d+:\s*(.+)$/gm
  const matches: RegExpExecArray[] = []

  let match
  while ((match = pattern.exec(raw)) !== null) {
    matches.push(match)
  }

  const result: { question: string; answer: string }[] = []

  for (let i = 0; i < matches.length; i++) {
    const question = matches[i][1].trim()
    const start = matches[i].index + matches[i][0].length
    const end = i + 1 < matches.length ? matches[i + 1].index : raw.length
    const answer = raw.slice(start, end).trim()
    result.push({ question, answer })
  }

  return result
}


const setLanguage = (lang: 'zh' | 'en') => {
  language.value = lang
}

watch(language, (lang) => {
  const raw = lang === 'zh' ? zhRaw : enRaw
  faqList.value = parseMarkdownFaq(raw)
})

onMounted(() => {
  faqList.value = parseMarkdownFaq(enRaw)
})
</script>

<style scoped>
.title {
  font-size: 2rem;
  font-weight: 700;
  color: #222;
}

.version {
  font-size: 1rem;
  color: #666;
  margin-top: 4px;
}

.description {
  font-size: 1.05rem;
  line-height: 1.8;
  text-align: center;
  color: #444;
}

.question {
  font-size: 1.1rem;
  font-weight: 600;
  color: #222;
}

.answer {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
}

.highlight-code {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  color: #333;
  display: inline-block;
}
</style>
