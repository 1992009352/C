<template>
  <div class="page-container">
    <div class="page-header">
      <h2>健康管理</h2>
      <el-button type="primary" @click="showDialog = true">
        <el-icon><Plus /></el-icon>记录健康数据
      </el-button>
    </div>

    <div class="card-content">
      <el-table :data="list" stripe v-loading="loading">
        <el-table-column prop="record_date" label="日期" width="120" />
        <el-table-column prop="weight" label="体重(kg)" width="100" />
        <el-table-column label="血压" width="120">
          <template #default="{ row }">
            {{ row.blood_pressure_sys && row.blood_pressure_dia ? `${row.blood_pressure_sys}/${row.blood_pressure_dia}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="heart_rate" label="心率" width="80" />
        <el-table-column prop="blood_sugar" label="血糖" width="80" />
        <el-table-column prop="body_fat" label="体脂率(%)" width="100" />
        <el-table-column prop="mood" label="心情" width="80">
          <template #default="{ row }">
            {{ ['', '😞', '😐', '🙂', '😊', '🥳'][row.mood] || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" size="small" text>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </div>

    <el-dialog v-model="showDialog" title="记录健康数据" width="520px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-form-item label="日期" required>
          <el-date-picker v-model="form.record_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="体重(kg)">
              <el-input-number v-model="form.weight" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="体脂率(%)">
              <el-input-number v-model="form.body_fat" :min="0" :max="100" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="收缩压">
              <el-input-number v-model="form.blood_pressure_sys" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="舒张压">
              <el-input-number v-model="form.blood_pressure_dia" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="心率">
              <el-input-number v-model="form.heart_rate" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="血糖">
              <el-input-number v-model="form.blood_sugar" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="心情">
          <el-rate v-model="form.mood" :texts="['很差', '较差', '一般', '不错', '很好']" show-text />
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

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const page = ref(1)
const total = ref(0)

const form = ref({ record_date: dayjs().format('YYYY-MM-DD'), weight: null, body_fat: null, blood_pressure_sys: null, blood_pressure_dia: null, heart_rate: null, blood_sugar: null, mood: 3, remark: '' })

async function loadData() {
  loading.value = true
  try {
    const res = await healthApi.getRecords({ page: page.value, page_size: 20 })
    list.value = res.items
    total.value = res.total
  } finally { loading.value = false }
}

async function handleSave() {
  saving.value = true
  try {
    await healthApi.createRecord(form.value)
    ElMessage.success('保存成功')
    showDialog.value = false
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(id) {
  await healthApi.deleteRecord(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
