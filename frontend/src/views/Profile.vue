<template>
  <div class="page-container">
    <div class="page-header">
      <h2>个人设置</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <div class="card-content">
          <h3 style="margin-bottom: 20px">基本信息</h3>
          <el-form :model="form" label-width="80px">
            <el-form-item label="用户名">
              <el-input :model-value="userStore.user?.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="form.email" />
            </el-form-item>
            <el-form-item label="手机">
              <el-input v-model="form.phone" />
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input v-model="form.bio" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="card-content">
          <h3 style="margin-bottom: 20px">修改密码</h3>
          <el-form :model="pwdForm" label-width="80px">
            <el-form-item label="原密码">
              <el-input v-model="pwdForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="pwdForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" :loading="changingPwd" @click="handleChangePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const saving = ref(false)
const changingPwd = ref(false)

const form = ref({
  nickname: userStore.user?.nickname || '',
  email: userStore.user?.email || '',
  phone: userStore.user?.phone || '',
  bio: userStore.user?.bio || '',
})

const pwdForm = ref({ old_password: '', new_password: '' })

async function handleSave() {
  saving.value = true
  try {
    await authApi.updateMe(form.value)
    await userStore.fetchUser()
    ElMessage.success('保存成功')
  } finally { saving.value = false }
}

async function handleChangePassword() {
  changingPwd.value = true
  try {
    await authApi.changePassword(pwdForm.value)
    ElMessage.success('密码修改成功')
    pwdForm.value = { old_password: '', new_password: '' }
  } finally { changingPwd.value = false }
}
</script>
