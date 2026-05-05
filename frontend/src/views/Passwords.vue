<template>
  <div class="page-container">
    <div class="page-header">
      <h2>密码管理</h2>
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon>新增密码</el-button>
    </div>

    <div class="filter-bar">
      <el-input v-model="keyword" placeholder="搜索..." clearable style="width: 300px" @clear="loadData" @keyup.enter="loadData" />
      <el-button @click="loadData">搜索</el-button>
    </div>

    <div class="card-content">
      <el-table :data="list" stripe v-loading="loading">
        <el-table-column prop="title" label="名称" min-width="150" />
        <el-table-column prop="url" label="网址" min-width="200">
          <template #default="{ row }">
            <a v-if="row.url" :href="row.url" target="_blank" style="color: #409EFF">{{ row.url }}</a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column label="密码" width="200">
          <template #default="{ row }">
            <span v-if="!row._showPwd">••••••••</span>
            <span v-else>{{ row.password }}</span>
            <el-button size="small" text @click="row._showPwd = !row._showPwd" style="margin-left: 8px">
              <el-icon><View v-if="!row._showPwd" /><Hide v-else /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text @click="editEntry(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference><el-button type="danger" size="small" text>删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </div>

    <el-dialog v-model="showDialog" :title="editing ? '编辑密码' : '新增密码'" width="480px" destroy-on-close>
      <el-form :model="form" label-width="70px">
        <el-form-item label="名称" required><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="网址"><el-input v-model="form.url" /></el-form-item>
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { passwordApi } from '@/api'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editing = ref(false)
const editingId = ref(null)
const page = ref(1)
const total = ref(0)
const keyword = ref('')
const form = ref({ title: '', url: '', username: '', password: '', remark: '' })

async function loadData() {
  loading.value = true
  try {
    const res = await passwordApi.getPasswords({ page: page.value, page_size: 20, keyword: keyword.value || undefined })
    list.value = res.items.map(i => ({ ...i, _showPwd: false }))
    total.value = res.total
  } finally { loading.value = false }
}

function editEntry(entry) {
  editing.value = true
  editingId.value = entry.id
  form.value = { title: entry.title, url: entry.url, username: entry.username, password: entry.password, remark: entry.remark }
  showDialog.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (editing.value) await passwordApi.updatePassword(editingId.value, form.value)
    else await passwordApi.createPassword(form.value)
    ElMessage.success('保存成功')
    showDialog.value = false
    editing.value = false
    form.value = { title: '', url: '', username: '', password: '', remark: '' }
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(id) {
  await passwordApi.deletePassword(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
