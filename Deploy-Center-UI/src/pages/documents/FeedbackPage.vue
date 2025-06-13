<template>
  <q-page class="q-pa-md flex flex-center" style="align-items: flex-start">
    <q-card
      class="q-pa-xl"
      style="
        max-width: 720px;
        width: 100%;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
        border-radius: 12px;
      "
    >
      <!-- Header -->
      <div class="column items-center q-mb-lg">
        <div class="title">意见反馈</div>
        <div class="version">期待您的宝贵建议</div>
      </div>

      <!-- 说明 -->
      <div class="description q-mb-xl">
        如果您在使用 Deploy Center
        的过程中遇到问题，或有改进建议，欢迎填写下方反馈内容。亦可前往Git仓库提交Issue。
      </div>

      <!-- 反馈表单 -->
      <q-form @submit.prevent="handleSubmitFeedback">
        <div class="row q-mb-md">
          <div class="col-12 col-sm-6 q-pr-sm">
            <q-input
              v-model="form.email"
              label="邮箱（可选）"
              :rules="[
                (val) =>
                  !val || /^\S+@\S+\.\S+$/.test(val) || '请输入有效的邮箱地址',
              ]"
            />
          </div>
          <div class="col-12 col-sm-6 q-pl-sm">
            <q-input
              v-model="form.phone"
              label="手机号（可选）"
              :rules="[
                (val) =>
                  !val || /^1[3-9]\d{9}$/.test(val) || '请输入有效的手机号码',
              ]"
            />
          </div>
        </div>

        <q-input
          v-model="form.message"
          label="反馈内容"
          type="textarea"
          outlined
          rows="10"
          :rules="[(val) => !!val || '请输入反馈内容']"
          class="q-mb-xl"
        />
        <div class="row justify-center">
          <q-btn label="提交反馈" color="primary" unelevated type="submit" />
        </div>
      </q-form>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Notify } from 'quasar';
import { submitFeedback } from 'src/api/feedbackApi';
import { storeToRefs } from 'pinia';
import { useLoginUserStore } from 'src/stores/useLoginUserStore';

// 获取 loginUserStore
const loginUserStore = useLoginUserStore();
const { loginUser } = storeToRefs(loginUserStore);

const form = ref({
  email: loginUser.value?.email || '',
  phone: '',
  message: '',
});

async function handleSubmitFeedback() {
  try {
    // 调用后端接口提交反馈
    await submitFeedback(form.value);
    Notify.create({
      message: '反馈已提交，谢谢支持！',
      color: 'positive',
    });
    form.value = { email: '', phone: '', message: '' };
  } catch (error) {
    Notify.create({
      message: '提交反馈失败，请稍后再试！',
      color: 'negative',
    });
  }
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
</style>
