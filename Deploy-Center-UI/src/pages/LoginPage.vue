<template>
  <div class="login-page">
    <div class="background-image"></div>
    <q-card class="login-card" flat>
      <q-card-section>
        <h2 class="text-h5 text-center">Deploy Center UI</h2>
        <q-form @submit.prevent="handleLogin">
          <q-input filled v-model="userLoginRequestDto.identifier" label="用户名" required />
          <q-input filled v-model="userLoginRequestDto.credential" label="密码" type="password" required />
          <div class="q-mt-md" style="text-align: center">
            <q-btn type="submit" label="登录" color="primary" block />
          </div>
        </q-form>
      </q-card-section>
    </q-card>

    <!--  双因素验证码对话框 -->
    <q-dialog v-model="showTwoFactorCodeDialog" persistent>
      <q-card style="min-width: 300px">
        <q-card-section class="text-h6">
          请输入双因素验证码
        </q-card-section>

        <q-card-section>
          <q-input v-model="userLoginRequestDto.two_factor_code" label="6位验证码" maxlength="6" autofocus />
          <!-- 重新绑定链接 -->
          <div class="text-grey-7 text-caption q-mt-sm" style="cursor: pointer; text-decoration: underline;"
            @click="onRebind">
            重新绑定认证器
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="取消" flat @click="cancel2faCode" />
          <q-btn flat label="提交" color="primary" @click="handleLogin" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- 二维码绑定对话框 -->
    <q-dialog v-model="showTwoFactorBindDialog" persistent>
      <q-card>
        <q-card-section class="text-h6">请使用认证器扫码绑定</q-card-section>
        <q-card-section class="text-center">
          <img :src="twoFactorQRCodeBase64" style="width: 200px;" />
        </q-card-section>
        <q-card-actions align="center">
          <q-btn flat color="primary" label="我已绑定，继续登录" @click="onBindAndContinue" />
        </q-card-actions>
      </q-card>
    </q-dialog>

  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { UserLoginRequestDto } from 'src/types/dto/UserLoginRequestDto';
import { login } from 'src/api/authApi';
import { HttpResult } from 'src/types/HttpResult';
import { Notify } from 'quasar';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'stores/useAuthStore';
import { useLoginUserStore } from 'stores/useLoginUserStore';
import { useAgentStore } from 'src/stores/useAgentStore';
import { getSystemConfig } from 'src/api/systemConfigApi'
import { getTwoFactorStatus, setupTwoFactor } from 'src/api/twoFactorApi';

const router = useRouter();

const userLoginRequestDto = reactive<UserLoginRequestDto>({
  identifier: '',
  credential: '',
  two_factor_code: null
});

const enableTwoFactorSystemConfigLoaded = ref(false)  // 是否已加载“是否开启2FA”的系统配置
const twoFactorEnabled = ref(false)    // 是否开启2FA
const showTwoFactorCodeDialog = ref(false)  // 显示2fa验证码对话框
const showTwoFactorBindDialog = ref(false)  // 显示2fa绑定对话框
const twoFactorQRCodeBase64 = ref('')                // 2fa绑定二维码

const cancel2faCode = () => {
  showTwoFactorCodeDialog.value = false
  userLoginRequestDto.two_factor_code = null
}

const onBindAndContinue = () => {
  showTwoFactorBindDialog.value = false
  showTwoFactorCodeDialog.value = true // 跳转到验证码输入
}

const onRebind = async () => {
  showTwoFactorBindDialog.value = true
  const setupRes = await setupTwoFactor(userLoginRequestDto.identifier)
  twoFactorQRCodeBase64.value = setupRes.data.qr_code_base64
}

const handleLogin = async () => {
  // 加载 2FA 配置（只会执行一次）
  if (!enableTwoFactorSystemConfigLoaded.value) {
    const config = await getSystemConfig("enable_2fa")
    twoFactorEnabled.value = config?.config_value === true
    enableTwoFactorSystemConfigLoaded.value = true
  }

  // 检查是否启用 2FA 且未输入 2FA 验证码
  if (twoFactorEnabled.value && !userLoginRequestDto.two_factor_code) {
    // 查询是否绑定
    const status = await getTwoFactorStatus(userLoginRequestDto.identifier)
    if (!status) {
      // 未绑定：请求二维码并展示绑定弹窗
      const setupRes = await setupTwoFactor(userLoginRequestDto.identifier)
      twoFactorQRCodeBase64.value = setupRes.data.qr_code_base64
      showTwoFactorBindDialog.value = true
      return
    }

    // 已绑定：弹出验证码输入弹窗
    showTwoFactorCodeDialog.value = true
    return
  }

  // 正式开始登录请求，可能携带2FA验证码
  const response: HttpResult<{ user_id: number; token: string }> = await login(userLoginRequestDto)

  if (response.code !== 200) {
    Notify.create({
      type: 'negative',
      position: 'top',
      message: response.msg || '登录失败，请重试',
    })
    return
  }

  // 登录成功
  Notify.create({
    type: 'positive',
    position: 'top',
    message: '登录成功，欢迎回来！',
  })

  // ====== 登录成功后的逻辑 ======
  // 1. 将 token 存储到 Pinia 中
  const authStore = useAuthStore();
  console.log(response.data)
  const { user_id, token } = response.data;

  // 这里会同时更新 Pinia 状态 并将 token 存储在localStorage中
  console.log("token: " + token)
  authStore.setToken(token);

  // 2. 设置当前登录用户
  const loginUserStore = useLoginUserStore()
  await loginUserStore.setLoginUserByUserId(user_id)
  console.log("LoginPage - " + JSON.stringify(loginUserStore.loginUser))

  // 3. 获取agent数据
  const agentStore = useAgentStore();
  // 3.1 获取所有Agent列表
  await agentStore.getAllAgentList();
  // 3.2 获取所有Agent运行时信息
  await agentStore.getAllAgentRuntimeInfo();
  // 3.3 设置当前Agent为第一个
  await agentStore.setCurrentAgentById(agentStore.agentList[0].id);

  // 4. 跳转到主页面
  await router.replace('/dashboard');
}

</script>

<style scoped>
.login-page {
  position: relative;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('src/assets/images/login_page_background.jpg');
  background-size: cover;
  background-position: center;
  z-index: 1;
}

.login-card {
  z-index: 2;
  max-width: 400px;
  width: 100%;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.8);
  /* 半透明背景 */
  border-radius: 10px;
}

.text-h5 {
  margin-bottom: 20px;
}
</style>
