<template>
  <div class="page-container">
    <div class="page-header">
      <h2>人生经历</h2>
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon>记录经历</el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="filters.experience_type" placeholder="类型" clearable style="width: 120px" @change="loadData">
        <el-option v-for="(label, key) in typeMap" :key="key" :label="label" :value="key" />
      </el-select>
      <el-input v-model="filters.keyword" placeholder="搜索..." clearable style="width: 200px" @clear="loadData" @keyup.enter="loadData" />
    </div>

    <div class="timeline-container">
      <el-timeline>
        <el-timeline-item v-for="exp in list" :key="exp.id" :timestamp="exp.experience_date" placement="top" :type="typeColors[exp.experience_type]">
          <el-card shadow="hover">
            <div class="exp-header">
              <h3>{{ exp.title }}</h3>
              <el-tag size="small">{{ typeMap[exp.experience_type] }}</el-tag>
            </div>
            <p class="exp-content">{{ exp.content }}</p>
            <div class="exp-meta">
              <span v-if="exp.location"><el-icon><MapLocation /></el-icon> {{ exp.location }}</span>
              <span v-if="exp.cost">¥{{ Number(exp.cost).toFixed(2) }}</span>
              <span v-if="exp.rating"><el-rate v-model="exp.rating" disabled :size="'small'" /></span>
            </div>
            <div class="exp-actions">
              <el-popconfirm title="确定删除？" @confirm="handleDelete(exp.id)">
                <template #reference><el-button type="danger" size="small" text>删除</el-button></template>
              </el-popconfirm>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
    <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="total, prev, pager, next" style="justify-content: flex-end" @current-change="loadData" />

    <el-dialog v-model="showDialog" title="记录经历" width="550px" destroy-on-close>
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题" required><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.experience_type" style="width: 100%">
            <el-option v-for="(label, key) in typeMap" :key="key" :label="label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" required>
          <el-date-picker v-model="form.experience_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="地点"><el-input v-model="form.location" /></el-form-item>
        <el-form-item label="花费"><el-input-number v-model="form.cost" :min="0" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="评分"><el-rate v-model="form.rating" allow-half /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="标签"><el-input v-model="form.tags" placeholder="用逗号分隔" /></el-form-item>
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
import { experienceApi } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const typeMap = { travel: '旅行', achievement: '成就', milestone: '里程碑', memory: '回忆', event: '事件', other: '其他' }
const typeColors = { travel: 'primary', achievement: 'success', milestone: 'warning', memory: 'info', event: '', other: 'info' }
const list = ref([])
const showDialog = ref(false)
const saving = ref(false)
const page = ref(1)
const total = ref(0)
const filters = ref({ experience_type: '', keyword: '' })
const form = ref({ title: '', experience_type: 'event', experience_date: dayjs().format('YYYY-MM-DD'), location: '', cost: null, rating: null, content: '', tags: '' })

async function loadData() {
  const res = await experienceApi.getExperiences({ page: page.value, page_size: 20, ...filters.value })
  list.value = res.items
  total.value = res.total
}

async function handleSave() {
  saving.value = true
  try {
    await experienceApi.createExperience(form.value)
    ElMessage.success('保存成功')
    showDialog.value = false
    form.value = { title: '', experience_type: 'event', experience_date: dayjs().format('YYYY-MM-DD'), location: '', cost: null, rating: null, content: '', tags: '' }
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(id) {
  await experienceApi.deleteExperience(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.exp-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; h3 { font-size: 16px; } }
.exp-content { color: #606266; font-size: 14px; line-height: 1.6; margin-bottom: 12px; }
.exp-meta { display: flex; gap: 16px; font-size: 13px; color: #909399; align-items: center; }
.exp-actions { text-align: right; margin-top: 8px; }
</style>
