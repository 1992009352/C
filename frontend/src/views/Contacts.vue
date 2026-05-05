<template>
  <div class="page-container">
    <div class="page-header">
      <h2>联系人</h2>
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon>新增联系人</el-button>
    </div>

    <div class="filter-bar">
      <el-input v-model="keyword" placeholder="搜索联系人..." clearable style="width: 300px" @clear="loadData" @keyup.enter="loadData" />
      <el-button @click="loadData">搜索</el-button>
    </div>

    <div class="card-content">
      <el-table :data="list" stripe v-loading="loading">
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="company" label="公司" width="150" />
        <el-table-column prop="position" label="职位" width="120" />
        <el-table-column prop="birthday" label="生日" width="120">
          <template #default="{ row }">{{ row.birthday || '-' }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text @click="editContact(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference><el-button type="danger" size="small" text>删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </div>

    <el-dialog v-model="showDialog" :title="editing ? '编辑联系人' : '新增联系人'" width="500px" destroy-on-close>
      <el-form :model="form" label-width="60px">
        <el-form-item label="姓名" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="公司"><el-input v-model="form.company" /></el-form-item>
        <el-form-item label="职位"><el-input v-model="form.position" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="生日">
          <el-date-picker v-model="form.birthday" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
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
import { contactApi } from '@/api'
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
const form = ref({ name: '', phone: '', email: '', company: '', position: '', address: '', birthday: null, remark: '' })

async function loadData() {
  loading.value = true
  try {
    const res = await contactApi.getContacts({ page: page.value, page_size: 20, keyword: keyword.value || undefined })
    list.value = res.items
    total.value = res.total
  } finally { loading.value = false }
}

function editContact(c) {
  editing.value = true
  editingId.value = c.id
  form.value = { ...c }
  showDialog.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (editing.value) await contactApi.updateContact(editingId.value, form.value)
    else await contactApi.createContact(form.value)
    ElMessage.success('保存成功')
    showDialog.value = false
    editing.value = false
    form.value = { name: '', phone: '', email: '', company: '', position: '', address: '', birthday: null, remark: '' }
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(id) {
  await contactApi.deleteContact(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
