<template>
  <div class="page-container">
    <div class="page-header">
      <h2>阅读管理</h2>
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon>添加图书</el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="filters.status" placeholder="状态" clearable style="width: 120px" @change="loadData">
        <el-option label="想读" value="wish" />
        <el-option label="在读" value="reading" />
        <el-option label="已读" value="finished" />
        <el-option label="弃读" value="abandoned" />
      </el-select>
      <el-input v-model="filters.keyword" placeholder="搜索书名" clearable style="width: 200px" @clear="loadData" @keyup.enter="loadData" />
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="book in list" :key="book.id" style="margin-bottom: 16px">
        <el-card shadow="hover" class="book-card">
          <div class="book-info">
            <h3>{{ book.title }}</h3>
            <p class="book-author">{{ book.author || '未知作者' }}</p>
            <el-tag :type="statusColors[book.status]" size="small">{{ statusMap[book.status] }}</el-tag>
            <div class="book-progress" v-if="book.total_pages > 0">
              <el-progress :percentage="Math.round(book.current_page / book.total_pages * 100)" :stroke-width="8" />
              <span class="progress-text">{{ book.current_page }}/{{ book.total_pages }}页</span>
            </div>
            <div class="book-rating" v-if="book.rating">
              <el-rate v-model="book.rating" disabled />
            </div>
          </div>
          <div class="book-actions">
            <el-button size="small" text @click="editBook(book)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(book.id)">
              <template #reference><el-button type="danger" size="small" text>删除</el-button></template>
            </el-popconfirm>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showDialog" :title="editing ? '编辑图书' : '添加图书'" width="500px" destroy-on-close>
      <el-form :model="form" label-width="80px">
        <el-form-item label="书名" required><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="作者"><el-input v-model="form.author" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="总页数"><el-input-number v-model="form.total_pages" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="当前页数" v-if="editing"><el-input-number v-model="form.current_page" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="想读" value="wish" /><el-option label="在读" value="reading" />
            <el-option label="已读" value="finished" /><el-option label="弃读" value="abandoned" />
          </el-select>
        </el-form-item>
        <el-form-item label="评分" v-if="editing"><el-rate v-model="form.rating" allow-half /></el-form-item>
        <el-form-item label="书评" v-if="editing"><el-input v-model="form.review" type="textarea" :rows="3" /></el-form-item>
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
import { readingApi } from '@/api'
import { ElMessage } from 'element-plus'

const statusMap = { wish: '想读', reading: '在读', finished: '已读', abandoned: '弃读' }
const statusColors = { wish: 'info', reading: 'primary', finished: 'success', abandoned: 'warning' }
const list = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editing = ref(false)
const editingId = ref(null)
const filters = ref({ status: '', keyword: '' })
const form = ref({ title: '', author: '', category: '', total_pages: 0, status: 'wish' })

async function loadData() {
  loading.value = true
  try {
    const res = await readingApi.getBooks({ page: 1, page_size: 50, ...filters.value })
    list.value = res.items
  } finally { loading.value = false }
}

function editBook(book) {
  editing.value = true
  editingId.value = book.id
  form.value = { ...book }
  showDialog.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (editing.value) {
      await readingApi.updateBook(editingId.value, form.value)
    } else {
      await readingApi.createBook(form.value)
    }
    ElMessage.success('保存成功')
    showDialog.value = false
    editing.value = false
    form.value = { title: '', author: '', category: '', total_pages: 0, status: 'wish' }
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(id) {
  await readingApi.deleteBook(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.book-card { .book-info { h3 { font-size: 15px; margin-bottom: 4px; } .book-author { color: #909399; font-size: 13px; margin-bottom: 8px; } .book-progress { margin-top: 12px; .progress-text { font-size: 12px; color: #909399; } } .book-rating { margin-top: 8px; } } .book-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; } }
</style>
