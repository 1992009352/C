<template>
  <div class="page-container">
    <div class="page-header">
      <h2>待办事项</h2>
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon>新建待办</el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="filters.status" placeholder="状态" clearable style="width: 120px" @change="loadData">
        <el-option label="待处理" value="pending" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-select v-model="filters.priority" placeholder="优先级" clearable style="width: 120px" @change="loadData">
        <el-option label="低" value="low" />
        <el-option label="中" value="medium" />
        <el-option label="高" value="high" />
        <el-option label="紧急" value="urgent" />
      </el-select>
      <el-input v-model="filters.keyword" placeholder="搜索标题" clearable style="width: 200px" @clear="loadData" @keyup.enter="loadData" />
    </div>

    <div class="card-content">
      <el-table :data="list" stripe v-loading="loading">
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <el-icon v-if="row.is_pinned" color="#E6A23C" style="margin-right: 4px"><Star /></el-icon>
            <span :style="{ textDecoration: row.status === 'completed' ? 'line-through' : 'none' }">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90">
          <template #default="{ row }">
            <el-tag :type="priorityColors[row.priority]" size="small">{{ priorityMap[row.priority] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusColors[row.status]" size="small">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止日期" width="120">
          <template #default="{ row }">{{ row.due_date || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status !== 'completed'" type="success" size="small" text @click="markComplete(row)">完成</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference><el-button type="danger" size="small" text>删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </div>

    <el-dialog v-model="showDialog" title="新建待办" width="500px" destroy-on-close>
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="form.priority">
            <el-radio-button value="low">低</el-radio-button>
            <el-radio-button value="medium">中</el-radio-button>
            <el-radio-button value="high">高</el-radio-button>
            <el-radio-button value="urgent">紧急</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tags" placeholder="用逗号分隔" />
        </el-form-item>
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
import { todoApi } from '@/api'
import { ElMessage } from 'element-plus'

const priorityMap = { low: '低', medium: '中', high: '高', urgent: '紧急' }
const priorityColors = { low: 'info', medium: 'primary', high: 'warning', urgent: 'danger' }
const statusMap = { pending: '待处理', in_progress: '进行中', completed: '已完成', cancelled: '已取消' }
const statusColors = { pending: 'warning', in_progress: 'primary', completed: 'success', cancelled: 'info' }

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const page = ref(1)
const total = ref(0)
const filters = ref({ status: '', priority: '', keyword: '' })
const form = ref({ title: '', content: '', priority: 'medium', due_date: null, tags: '' })

async function loadData() {
  loading.value = true
  try {
    const res = await todoApi.getTodos({ page: page.value, page_size: 20, ...filters.value })
    list.value = res.items
    total.value = res.total
  } finally { loading.value = false }
}

async function handleSave() {
  saving.value = true
  try {
    await todoApi.createTodo(form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    form.value = { title: '', content: '', priority: 'medium', due_date: null, tags: '' }
    loadData()
  } finally { saving.value = false }
}

async function markComplete(row) {
  await todoApi.updateTodo(row.id, { status: 'completed' })
  ElMessage.success('已完成')
  loadData()
}

async function handleDelete(id) {
  await todoApi.deleteTodo(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
