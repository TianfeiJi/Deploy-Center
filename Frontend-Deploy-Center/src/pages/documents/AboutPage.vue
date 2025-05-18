<template>
  <q-page class="q-pa-md flex flex-center" style="align-items: flex-start">
    <q-card class="q-pa-xl"
      style="width: 100%; max-width: 760px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); border-radius: 12px;">

      <!-- Header -->
      <div class="column items-center q-mb-lg">
        <div class="title">Deploy Center</div>
        <div class="version">v{{ version }}</div>
      </div>

      <!-- 语言切换 -->
      <div class="row justify-center q-mt-md">
        <q-btn flat dense label="中文" :color="language === 'zh' ? 'primary' : 'grey-6'" class="q-mr-sm"
          @click="setLanguage('zh')" />
        <q-btn flat dense no-caps label="English" :color="language === 'en' ? 'primary' : 'grey-6'"
          @click="setLanguage('en')" />
      </div>

      <!-- 项目简介 -->
      <div class="description q-mb-xl">
        {{ language === 'zh' ? zhIntro : enIntro }}
      </div>

      <!-- GitHub 按钮 -->
      <div class="row justify-center q-gutter-sm q-mb-xl">
        <button class="custom-btn" @click="goToGithub">
          <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub"
            class="github-icon" />
          <span>{{ language === 'zh' ? '源码' : 'Source Code' }}</span>
        </button>
        <button class="custom-btn light" @click="goToGithub">
          <q-icon name="star" size="16px" class="q-mr-xs" />
          <span>{{ starLabel }}</span>
        </button>
      </div>

      <!-- 作者信息 -->
      <div class="author q-mb-md">
        {{ language === 'zh' ? '作者' : 'Author' }}：
        <span class="author-name">Tianfei Ji (纪田飞)</span><br />
        {{ language === 'zh' ? '个人网站' : 'Website' }}：
        <a href="http://jitianfei.com" target="_blank">jitianfei.com</a>
      </div>

      <q-separator class="q-my-md" />

      <!-- 支持与捐赠 -->
      <q-expansion-item icon="fa-solid fa-hand-holding-heart" :label="language === 'zh' ? '支持与捐赠' : 'Support & Donate'">
        <div class="donate-text q-mb-md">
          {{ language === 'zh' ? zhDonateIntro : enDonateIntro }}
        </div>

        <div class="row justify-center q-gutter-xl q-mb-xl">
          <div class="column items-center">
            <img src="images/wechat_donate.jpg" alt="微信收款码" class="pay-code" />
            <div class="pay-label">{{ language === 'zh' ? '微信支付' : 'WeChat Pay' }}</div>
          </div>
          <div class="column items-center">
            <img src="images/alipay_donate.jpg" alt="支付宝收款码" class="pay-code" />
            <div class="pay-label">{{ language === 'zh' ? '支付宝支付' : 'Alipay' }}</div>
          </div>
        </div>

        <div class="thanks">
          {{ language === 'zh' ? zhThanks : enThanks }}
        </div>
      </q-expansion-item>

    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { version } from '../../../package.json'

const githubUrl = 'https://github.com/TianfeiJi/deploy-center'
const starLabel = ref('Star')

const goToGithub = () => {
  window.open(githubUrl, '_blank')
}

onMounted(async () => {
  try {
    const res = await fetch('https://api.github.com/repos/TianfeiJi/deploy-center')
    const data = await res.json()
    starLabel.value = `Star ${data.stargazers_count}`
  } catch {
    starLabel.value = 'Star'
  }
})

const language = ref<'zh' | 'en'>('zh')

const zhIntro = '一个轻量化的项目部署平台，支持前端项目与任何容器化服务（如 Java、Python 等）的自动化部署。'
const enIntro = 'A lightweight deployment platform supporting frontend projects and any containerized services like Java, Python, etc.'

const zhDonateIntro = `Deploy Center 最初是一个简化部署操作的小工具，后来发现还能勉强见人，于是就放出来了  \uD83D\uDE48
功能不多，界面不丑，代码能跑，希望你用得上 \uD83D\uDCBB
如果它帮你少敲几行 docker 命令，不用手动登录服务器进行项目部署，那就不白写了 \uD83E\uDDD8
当然，愿意打赏我一杯咖啡，那更不白写了 \u2615\uFE0F\uD83D\uDE0C`

const enDonateIntro = `Deploy Center started as a small tool to simplify deployment tasks.
Later I realized it looked just decent enough to share, so here it is \uD83D\uDE48
It doesn't do much, doesn't look too bad, and the code mostly runs — hopefully you'll find it useful \uD83D\uDCBB
If it saves you from typing a few Docker commands or manually logging into a server, then it wasn’t written in vain \uD83E\uDDD8
And if you're feeling generous and want to buy me a coffee — well, that's even better \u2615\uFE0F\uD83D\uDE0C`

const zhThanks = '你的支持不仅是对这个项目的认可，也是对我个人的巨大鼓励。'
const enThanks = 'Your support means a lot to both this project and myself.'

const setLanguage = (lang: 'zh' | 'en') => {
  language.value = lang
}
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

.custom-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 6px;
  border: 1px solid #ccc;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.custom-btn:hover {
  background-color: #f3f3f3;
}

.custom-btn.light {
  border: none;
  background-color: transparent;
  color: #666;
}

.github-icon {
  width: 18px;
  height: 18px;
}

.author {
  font-size: 0.85rem;
  text-align: center;
  color: #777;
}

.author-name {
  color: #1976d2;
  font-weight: 500;
}

.author a {
  color: #1976d2;
  text-decoration: none;
}

.author a:hover {
  text-decoration: underline;
}

/* 
  穿透 Quasar 内部结构，修正 q-item__section--avatar 默认右侧 16px padding：
  - 将 padding-right 缩小到 8px，使 label 区域与右侧展开箭头更紧凑
  - 将 min-width 设为 auto，避免右侧留白过大
*/
.q-expansion-item ::v-deep(.q-item__section--avatar) {
  padding-right: 8px !important;
  min-width: auto;
}

/* 穿透 q-item__section--side 内的展开箭头图标，缩小尺寸 */
.q-expansion-item ::v-deep(.q-item__section--side > .q-icon) {
  font-size: 1.1rem;
}

.pay-code {
  width: 180px;
  height: 180px;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.pay-label {
  margin-top: 8px;
  font-size: 0.9rem;
  color: #555;
}

.donate-text {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #444;
  white-space: pre-line;
  margin-bottom: 1rem;
}

.thanks {
  font-size: 0.9rem;
  text-align: center;
  color: #777;
  margin-top: 12px;
}
</style>
