<template>
  <q-dialog>
    <q-card style="min-width: 320px; max-width: 480px;">
      <q-card-section class="row items-center q-pb-none">
        <q-avatar size="64px">
          <img :src="loginUser.avatar" alt="用户头像" />
        </q-avatar>
        <div class="column q-ml-md">
          <div class="text-h6">{{ loginUser.nickname }}</div>
          <div class="text-caption text-grey">@{{ loginUser.username }}</div>
        </div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-separator spaced />

      <q-card-section>
        <q-list separator>
          <q-item>
            <q-item-section avatar>
              <q-icon name="badge" />
            </q-item-section>
            <q-item-section>
              <q-item-label>用户名</q-item-label>
              <q-item-label caption>{{ loginUser.username }}</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section avatar>
              <q-icon name="person" />
            </q-item-section>

            <q-item-section>
              <q-item-label>昵称</q-item-label>
              <q-item-label caption>{{ loginUser.nickname }}</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section avatar>
              <q-icon name="email" />
            </q-item-section>

            <q-item-section>
              <q-item-label>邮箱</q-item-label>
              <q-item-label caption>{{ loginUser.email || '未设置' }}</q-item-label>
            </q-item-section>
          </q-item>

        </q-list>
      </q-card-section>

      <q-separator />

    <!-- 
      <q-card-actions align="right">
        <q-btn flat label="关闭" color="primary" v-close-popup />
      </q-card-actions>
    -->

    </q-card>

  </q-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { User } from 'src/types/User'
import { useLoginUserStore } from 'src/stores/useLoginUserStore';
import { storeToRefs } from 'pinia';

// 从store获取当前登录用户的信息
const loginUserStore = useLoginUserStore();
const { loginUser } = storeToRefs(loginUserStore) as {
  loginUser: Partial<User>
}

</script>

<style scoped>
.text-caption {
  font-size: 0.85rem;
}
</style>
