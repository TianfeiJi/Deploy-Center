<template>
  <q-page class="q-pa-md flex flex-center" style="align-items: flex-start">
    <q-card class="q-pa-xl" style="width: 100%">
      <div class="row items-center justify-between q-mb-xl">
        <div class="title">用户管理</div>
        <el-button type="primary" @click="showAddDialog = true"
          >新增用户</el-button
        >
      </div>

      <el-table
        :data="userList"
        style="width: 100%"
        border
        stripe
        highlight-current-row
        row-key="id"
      >
        <el-table-column label="ID" prop="id" width="60" />

        <el-table-column label="用户名" min-width="70">
          <template #default="{ row }">{{ row.username }}</template>
        </el-table-column>

        <el-table-column label="用户昵称" min-width="70">
          <template #default="{ row }">{{ row.nickname }}</template>
        </el-table-column>

        <el-table-column label="用户角色" min-width="70">
          <template #default="{ row }">{{ row.role }}</template>
        </el-table-column>

        <el-table-column label="用户权限" min-width="160">
          <template #default="{ row }">{{ row.permissions }}</template>
        </el-table-column>

        <el-table-column label="状态" min-width="30">
          <template #default="{ row }">
            <el-tag
              :closable="false"
              :type="row.status === 'ENABLED' ? 'success' : 'info'"
              effect="light"
            >
              {{ row.status === 'ENABLED' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="onEditUser(row)"
              >修改</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </q-card>

    <el-dialog v-model="showEditDialog" title="编辑用户" width="500px">
      <el-form :model="editUser" label-width="80px">
        <el-form-item label="用户名"
          ><el-input v-model="editUser.username"
        /></el-form-item>

        <el-form-item label="昵称"
          ><el-input v-model="editUser.nickname"
        /></el-form-item>

        <el-form-item label="密码">
          <el-input
            :type="showPassword ? 'text' : 'text'"
            :model-value="showPassword ? editUser.password : '**********'"
            readonly
          >
            <template #append>
              <q-icon
                :name="showPassword ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="showPassword = !showPassword"
              />
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="角色"
          ><el-input v-model="editUser.role"
        /></el-form-item>

        <el-form-item label="权限"
          ><el-input v-model="editUser.permissions"
        /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="onUpdateUser">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新增用户对话框 -->
    <el-dialog v-model="showAddDialog" title="新增用户" width="500px">
      <el-form :model="newUser" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="newUser.username" />
        </el-form-item>

        <el-form-item label="昵称">
          <el-input v-model="newUser.nickname" />
        </el-form-item>

        <el-form-item label="密码">
          <el-input v-model="newUser.password" type="password" />
        </el-form-item>

        <el-form-item label="角色">
          <el-input v-model="newUser.role" />
        </el-form-item>

        <el-form-item label="权限" v-if="newUser.role !== 'superadmin'">
          <el-input v-model="newUser.permissions" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="onAddUser">确认</el-button>
      </template>
    </el-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Notify } from 'quasar';
import { getUserList, updateUser, createUser } from 'src/api/userApi';
import type { User } from 'src/types/User';

const userList = ref<User[]>([]);

const fetchUsers = async () => {
  userList.value = await getUserList();
};

const showPassword = ref(false);
const showEditDialog = ref(false);
const editUser = ref<User>({} as User);

const onEditUser = (user: User) => {
  editUser.value = { ...user };
  showEditDialog.value = true;
};

const onUpdateUser = async () => {
  try {
    await updateUser(editUser.value.id, editUser.value);
    Notify.create({ type: 'positive', message: '更新成功' });
    showEditDialog.value = false;
    await fetchUsers();
  } catch (e) {
    Notify.create({ type: 'negative', message: '更新失败' });
  }
};

const onSave = async (user: User) => {
  try {
    const updated: Partial<User> = {
      username: user.username,
      nickname: user.nickname,
      permissions: user.permissions,
      status: user.status,
    };
    await updateUser(user.id, updated);
    Notify.create({ type: 'positive', message: '保存成功' });
  } catch (error) {
    Notify.create({ type: 'negative', message: '保存失败' });
  }
};

const formatDate = (date: string | Date | null | undefined) => {
  if (!date) return '-';
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString();
};

// 新增用户弹窗控制
const showAddDialog = ref(false);
const newUser = ref<Partial<User>>({
  username: '',
  nickname: '',
  password: '',
  role: 'user',
  permissions: null,
});

const onAddUser = async () => {
  try {
    await createUser(newUser.value);
    Notify.create({ type: 'positive', message: '新增成功' });
    showAddDialog.value = false;
    await fetchUsers();
  } catch (err) {
    Notify.create({ type: 'negative', message: '新增失败' });
  }
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #222;
}

.rounded {
  border-radius: 6px;
}
.text-grey {
  color: #888;
}
</style>
