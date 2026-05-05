<template>
  <div class="page-container">
    <div class="page-header">
      <h2>饮食管理</h2>
      <el-button type="primary" @click="showDialog = true"><el-icon><Plus /></el-icon>记录饮食</el-button>
    </div>

    <div class="card-content">
      <el-table :data="list" stripe v-loading="loading">
        <el-table-column prop="diet_date" label="日期" width="120" />
        <el-table-column prop="meal_type" label="餐类" width="80">
          <template #default="{ row }">
            <el-tag :type="mealColors[row.meal_type]" size="small">{{ mealMap[row.meal_type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="food_name" label="食物" min-width="150" />
        <el-table-column label="用量" width="100">
          <template #default="{ row }">{{ row.amount }}{{ row.unit }}</template>
        </el-table-column>
        <el-table-column prop="calories" label="热量(kcal)" width="100">
          <template #default="{ row }">{{ row.calories || '-' }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" />
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

    <el-dialog v-model="showDialog" title="记录饮食" width="480px" destroy-on-close>
      <el-form :model="form" label-width="80px">
        <el-form-item label="日期" required>
          <el-date-picker v-model="form.diet_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="餐类">
          <el-radio-group v-model="form.meal_type">
            <el-radio-button value="breakfast">早餐</el-radio-button>
            <el-radio-button value="lunch">午餐</el-radio-button>
            <el-radio-button value="dinner">晚餐</el-radio-button>
            <el-radio-button value="snack">加餐</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="食物名" required>
          <el-input v-model="form.food_name" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="用量">
              <el-input-number v-model="form.amount" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="form.unit" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="热量(kcal)">
          <el-input-number v-model="form.calories" :min="0" style="width: 100%" />
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
import { dietApi } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const mealMap = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '加餐' }
const mealColors = { breakfast: 'warning', lunch: 'primary', dinner: 'success', snack: 'info' }
const list = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const page = ref(1)
const total = ref(0)
const form = ref({ diet_date: dayjs().format('YYYY-MM-DD'), meal_type: 'lunch', food_name: '', amount: 100, unit: 'g', calories: null, remark: '' })

async function loadData() {
  loading.value = true
  try {
    const res = await dietApi.getRecords({ page: page.value, page_size: 20 })
    list.value = res.items
    total.value = res.total
  } finally { loading.value = false }
}

async function handleSave() {
  saving.value = true
  try {
    await dietApi.createRecord(form.value)
    ElMessage.success('保存成功')
    showDialog.value = false
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(id) {
  await dietApi.deleteRecord(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
