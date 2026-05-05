<template>
  <div class="page-container">
    <div class="page-header">
      <h2>笔记管理</h2>
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon>新建笔记</el-button>
    </div>

    <div class="filter-bar">
      <el-input v-model="keyword" placeholder="搜索笔记..." clearable style="width: 300px" @clear="loadData" @keyup.enter="loadData" />
      <el-button @click="loadData">搜索</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="note in list" :key="note.id" style="margin-bottom: 16px">
        <el-card shadow="hover" class="note-card" @click="editNote(note)">
          <template #header>
            <div class="note-header">
              <el-icon v-if="note.is_pinned" color="#E6A23C"><Star /></el-icon>
              <span class="note-title">{{ note.title }}</span>
            </div>
          </template>
          <p class="note-content">{{ note.content?.substring(0, 120) || '无内容' }}</p>
          <div class="note-footer">
            <span class="note-date">{{ note.updated_at?.substring(0, 10) }}</span>
            <el-popconfirm title="确定删除？" @confirm.stop="handleDelete(note.id)">
              <template #reference>
                <el-button type="danger" size="small" text @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="total, prev, pager, next" style="justify-content: flex-end" @current-change="loadData" />

    <el-dialog v-model="showDialog" :title="editing ? '编辑笔记' : '新建笔记'" width="600px" destroy-on-close>
      <el-form :model="form" label-width="60px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="10" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tags" placeholder="用逗号分隔" />
        </el-form-item>
        <el-form-item label="置顶">
          <el-switch v-model="form.is_pinned" />
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
import { noteApi } from '@/api'
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
const form = ref({ title: '', content: '', tags: '', is_pinned: false })

async function loadData() {
  loading.value = true
  try {
    const res = await noteApi.getNotes({ page: page.value, page_size: 20, keyword: keyword.value || undefined })
    list.value = res.items
    total.value = res.total
  } finally { loading.value = false }
}

function editNote(note) {
  editing.value = true
  editingId.value = note.id
  form.value = { title: note.title, content: note.content, tags: note.tags, is_pinned: note.is_pinned }
  showDialog.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (editing.value) {
      await noteApi.updateNote(editingId.value, form.value)
    } else {
      await noteApi.createNote(form.value)
    }
    ElMessage.success('保存成功')
    showDialog.value = false
    editing.value = false
    form.value = { title: '', content: '', tags: '', is_pinned: false }
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(id) {
  await noteApi.deleteNote(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.note-card {
  cursor: pointer;
  transition: transform 0.2s;
  &:hover { transform: translateY(-3px); }
}
.note-header {
  display: flex; align-items: center; gap: 6px;
  .note-title { font-weight: 600; font-size: 15px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
}
.note-content { color: #606266; font-size: 13px; line-height: 1.6; min-height: 60px; }
.note-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 12px;
  .note-date { color: #909399; font-size: 12px; }
}
</style>
