<template>
  <div class="page-container">
    <div class="page-header">
      <h2>习惯追踪</h2>
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon>新建习惯</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8" v-for="habit in habits" :key="habit.id" style="margin-bottom: 16px">
        <div class="stat-card" :style="{ borderLeft: `4px solid ${habit.color}` }">
          <div class="habit-header">
            <h3>{{ habit.name }}</h3>
            <el-button type="primary" size="small" round @click="checkin(habit)">
              <el-icon><Check /></el-icon>打卡
            </el-button>
          </div>
          <p class="habit-desc">{{ habit.description || '无描述' }}</p>
          <div class="habit-meta">
            <span>频率：{{ freqMap[habit.frequency] }}</span>
            <span>目标：{{ habit.target_count }}{{ habit.unit }}/{{ freqMap[habit.frequency] }}</span>
          </div>
          <div class="habit-actions">
            <el-button size="small" text type="danger" @click="handleDelete(habit.id)">删除</el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="showDialog" title="新建习惯" width="480px" destroy-on-close>
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="频率">
          <el-select v-model="form.frequency" style="width: 100%">
            <el-option label="每日" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="目标次数">
              <el-input-number v-model="form.target_count" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="form.unit" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.color" />
        </el-form-item>
        <el-form-item label="开始日期" required>
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
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
import { habitApi } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const freqMap = { daily: '每天', weekly: '每周', monthly: '每月' }
const habits = ref([])
const showDialog = ref(false)
const saving = ref(false)
const form = ref({ name: '', description: '', frequency: 'daily', target_count: 1, unit: '次', color: '#67C23A', start_date: dayjs().format('YYYY-MM-DD') })

async function loadData() {
  habits.value = await habitApi.getHabits({ is_active: true })
}

async function handleSave() {
  saving.value = true
  try {
    await habitApi.createHabit(form.value)
    ElMessage.success('创建成功')
    showDialog.value = false
    form.value = { name: '', description: '', frequency: 'daily', target_count: 1, unit: '次', color: '#67C23A', start_date: dayjs().format('YYYY-MM-DD') }
    loadData()
  } finally { saving.value = false }
}

async function checkin(habit) {
  await habitApi.createRecord({ habit_id: habit.id, record_date: dayjs().format('YYYY-MM-DD') })
  ElMessage.success(`${habit.name} 打卡成功！`)
}

async function handleDelete(id) {
  await habitApi.deleteHabit(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.habit-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
  h3 { font-size: 16px; font-weight: 600; }
}
.habit-desc { color: #606266; font-size: 13px; margin-bottom: 12px; }
.habit-meta { display: flex; gap: 16px; font-size: 12px; color: #909399; margin-bottom: 8px; }
.habit-actions { text-align: right; }
</style>
