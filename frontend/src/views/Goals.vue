<template>
  <div class="page-container">
    <div class="page-header">
      <h2>目标管理</h2>
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon>新建目标</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8" v-for="goal in goals" :key="goal.id" style="margin-bottom: 16px">
        <div class="stat-card">
          <div class="goal-header">
            <h3>{{ goal.title }}</h3>
            <el-tag :type="statusColors[goal.status]" size="small">{{ statusMap[goal.status] }}</el-tag>
          </div>
          <p class="goal-desc">{{ goal.description || '无描述' }}</p>
          <div class="goal-progress">
            <el-progress :percentage="Math.min(100, Math.round(goal.current_value / goal.target_value * 100))" :stroke-width="12" />
            <span class="progress-text">{{ goal.current_value }}/{{ goal.target_value }} {{ goal.unit }}</span>
          </div>
          <div class="goal-meta">
            <span>开始：{{ goal.start_date }}</span>
            <span v-if="goal.end_date">截止：{{ goal.end_date }}</span>
          </div>
          <div class="goal-actions">
            <el-button size="small" text type="primary" @click="updateProgress(goal)">更新进度</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(goal.id)">
              <template #reference><el-button type="danger" size="small" text>删除</el-button></template>
            </el-popconfirm>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="showDialog" title="新建目标" width="500px" destroy-on-close>
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题" required><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="form.category" placeholder="健康/学习/财务/..." /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="目标值"><el-input-number v-model="form.target_value" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位"><el-input v-model="form.unit" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="开始日期" required>
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showProgressDialog" title="更新进度" width="400px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="当前进度">
          <el-input-number v-model="progressValue" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProgressDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProgress">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { goalApi } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const statusMap = { not_started: '未开始', in_progress: '进行中', completed: '已完成', abandoned: '已放弃' }
const statusColors = { not_started: 'info', in_progress: 'primary', completed: 'success', abandoned: 'warning' }
const goals = ref([])
const showDialog = ref(false)
const showProgressDialog = ref(false)
const saving = ref(false)
const currentGoalId = ref(null)
const progressValue = ref(0)
const form = ref({ title: '', description: '', category: '', target_value: 100, unit: '%', start_date: dayjs().format('YYYY-MM-DD'), end_date: null })

async function loadData() {
  goals.value = await goalApi.getGoals({})
}

async function handleSave() {
  saving.value = true
  try {
    await goalApi.createGoal(form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    form.value = { title: '', description: '', category: '', target_value: 100, unit: '%', start_date: dayjs().format('YYYY-MM-DD'), end_date: null }
    loadData()
  } finally { saving.value = false }
}

function updateProgress(goal) {
  currentGoalId.value = goal.id
  progressValue.value = Number(goal.current_value)
  showProgressDialog.value = true
}

async function saveProgress() {
  await goalApi.updateGoal(currentGoalId.value, { current_value: progressValue.value, status: 'in_progress' })
  ElMessage.success('进度已更新')
  showProgressDialog.value = false
  loadData()
}

async function handleDelete(id) {
  await goalApi.deleteGoal(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.goal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; h3 { font-size: 16px; font-weight: 600; } }
.goal-desc { color: #606266; font-size: 13px; margin-bottom: 12px; }
.goal-progress { margin-bottom: 12px; .progress-text { font-size: 12px; color: #909399; } }
.goal-meta { display: flex; gap: 16px; font-size: 12px; color: #909399; margin-bottom: 8px; }
.goal-actions { display: flex; justify-content: flex-end; gap: 4px; }
</style>
