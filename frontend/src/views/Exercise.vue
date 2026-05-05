<template>
  <div class="page-container">
    <div class="page-header">
      <h2>运动记录</h2>
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon>记录运动</el-button>
    </div>

    <div class="card-content">
      <el-table :data="list" stripe v-loading="loading">
        <el-table-column prop="exercise_date" label="日期" width="120" />
        <el-table-column prop="exercise_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ typeMap[row.exercise_type] || row.exercise_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长(分钟)" width="100" />
        <el-table-column prop="distance" label="距离(km)" width="100">
          <template #default="{ row }">{{ row.distance || '-' }}</template>
        </el-table-column>
        <el-table-column prop="calories" label="消耗(kcal)" width="100">
          <template #default="{ row }">{{ row.calories || '-' }}</template>
        </el-table-column>
        <el-table-column prop="location" label="地点" min-width="120" />
        <el-table-column prop="remark" label="备注" min-width="150" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference><el-button type="danger" size="small" text>删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </div>

    <el-dialog v-model="showDialog" title="记录运动" width="480px" destroy-on-close>
      <el-form :model="form" label-width="90px">
        <el-form-item label="日期" required>
          <el-date-picker v-model="form.exercise_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="运动类型">
          <el-select v-model="form.exercise_type" style="width: 100%">
            <el-option v-for="(label, key) in typeMap" :key="key" :label="label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="时长(分钟)">
          <el-input-number v-model="form.duration" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="距离(km)">
          <el-input-number v-model="form.distance" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="消耗(kcal)">
          <el-input-number v-model="form.calories" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="地点">
          <el-input v-model="form.location" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
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
import { healthApi } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const typeMap = { running: '跑步', walking: '步行', cycling: '骑行', swimming: '游泳', gym: '健身', yoga: '瑜伽', basketball: '篮球', football: '足球', hiking: '徒步', other: '其他' }
const list = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const page = ref(1)
const total = ref(0)
const form = ref({ exercise_date: dayjs().format('YYYY-MM-DD'), exercise_type: 'running', duration: 30, distance: null, calories: null, location: '', remark: '' })

async function loadData() {
  loading.value = true
  try {
    const res = await healthApi.getExercises({ page: page.value, page_size: 20 })
    list.value = res.items
    total.value = res.total
  } finally { loading.value = false }
}

async function handleSave() {
  saving.value = true
  try {
    await healthApi.createExercise(form.value)
    ElMessage.success('保存成功')
    showDialog.value = false
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(id) {
  await healthApi.deleteExercise(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
