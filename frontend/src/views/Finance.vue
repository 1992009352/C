<template>
  <div class="page-container">
    <div class="page-header">
      <h2>财务管理</h2>
      <el-button type="primary" @click="showDialog = true">
        <el-icon><Plus /></el-icon>记一笔
      </el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="filters.type" placeholder="类型" clearable style="width: 120px" @change="loadData">
        <el-option label="收入" value="income" />
        <el-option label="支出" value="expense" />
      </el-select>
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="onDateChange" />
      <el-input v-model="filters.keyword" placeholder="搜索描述" clearable style="width: 200px" @clear="loadData" @keyup.enter="loadData" />
      <el-button @click="loadData">查询</el-button>
    </div>

    <div class="card-content">
      <el-table :data="list" stripe v-loading="loading">
        <el-table-column prop="occur_date" label="日期" width="120" />
        <el-table-column prop="type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'" size="small">
              {{ row.type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.type === 'income' ? '#67C23A' : '#F56C6C', fontWeight: 600 }">
              {{ row.type === 'income' ? '+' : '-' }}¥{{ Number(row.amount).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="account" label="账户" width="100" />
        <el-table-column prop="tags" label="标签" width="120" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确定删除吗？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" size="small" text>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page" v-model:page-size="pageSize"
        :total="total" :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next" style="margin-top: 16px; justify-content: flex-end"
        @current-change="loadData" @size-change="loadData"
      />
    </div>

    <el-dialog v-model="showDialog" title="新增记录" width="500px" destroy-on-close>
      <el-form :model="form" label-width="80px">
        <el-form-item label="类型">
          <el-radio-group v-model="form.type">
            <el-radio-button value="expense">支出</el-radio-button>
            <el-radio-button value="income">收入</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="日期" required>
          <el-date-picker v-model="form.occur_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" />
        </el-form-item>
        <el-form-item label="账户">
          <el-input v-model="form.account" placeholder="现金/支付宝/微信/银行卡" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tags" placeholder="用逗号分隔" />
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
import { financeApi } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dateRange = ref(null)
const filters = ref({ type: '', keyword: '' })

const form = ref({
  type: 'expense', amount: 0, occur_date: dayjs().format('YYYY-MM-DD'),
  description: '', account: '', tags: '', remark: '',
})

function onDateChange(val) {
  if (val) {
    filters.value.start_date = val[0]
    filters.value.end_date = val[1]
  } else {
    filters.value.start_date = undefined
    filters.value.end_date = undefined
  }
  loadData()
}

async function loadData() {
  loading.value = true
  try {
    const res = await financeApi.getTransactions({ page: page.value, page_size: pageSize.value, ...filters.value })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    await financeApi.createTransaction(form.value)
    ElMessage.success('保存成功')
    showDialog.value = false
    form.value = { type: 'expense', amount: 0, occur_date: dayjs().format('YYYY-MM-DD'), description: '', account: '', tags: '', remark: '' }
    loadData()
  } finally {
    saving.value = false
  }
}

async function handleDelete(id) {
  await financeApi.deleteTransaction(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
