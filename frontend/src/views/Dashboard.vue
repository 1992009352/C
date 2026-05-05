<template>
  <div class="page-container">
    <div class="page-header">
      <h2>仪表盘</h2>
      <span class="today">{{ today }}</span>
    </div>

    <el-row :gutter="16" class="stat-row">
      <el-col :xs="12" :sm="8" :md="6" :lg="4" v-for="card in statCards" :key="card.label">
        <div class="stat-card" :style="{ borderTop: `3px solid ${card.color}` }">
          <div class="stat-icon" :style="{ background: card.color + '20', color: card.color }">
            <el-icon :size="24"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 20px">
      <el-col :span="16">
        <div class="card-content">
          <h3 style="margin-bottom: 16px">收支趋势</h3>
          <div ref="chartRef" style="height: 350px"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="card-content" style="margin-bottom: 16px">
          <h3 style="margin-bottom: 16px">本月概览</h3>
          <div class="overview-item">
            <span>本月收入</span>
            <span class="income">+¥{{ stats.month_income?.toFixed(2) || '0.00' }}</span>
          </div>
          <div class="overview-item">
            <span>本月支出</span>
            <span class="expense">-¥{{ stats.month_expense?.toFixed(2) || '0.00' }}</span>
          </div>
          <div class="overview-item">
            <span>本月结余</span>
            <span :class="(stats.month_income - stats.month_expense) >= 0 ? 'income' : 'expense'">
              ¥{{ ((stats.month_income || 0) - (stats.month_expense || 0)).toFixed(2) }}
            </span>
          </div>
          <el-divider />
          <div class="overview-item">
            <span>运动时长（本月）</span>
            <span>{{ stats.month_exercise_duration || 0 }} 分钟</span>
          </div>
          <div class="overview-item">
            <span>待办完成率</span>
            <span>{{ stats.total_todos > 0 ? (((stats.total_todos - stats.pending_todos) / stats.total_todos) * 100).toFixed(0) : 0 }}%</span>
          </div>
          <div class="overview-item">
            <span>今日习惯打卡</span>
            <span>{{ stats.today_habit_completed || 0 }} / {{ stats.active_habits || 0 }}</span>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { dashboardApi } from '@/api'
import dayjs from 'dayjs'
import * as echarts from 'echarts'

const stats = ref({})
const trend = ref([])
const chartRef = ref(null)
const today = dayjs().format('YYYY年MM月DD日 dddd')

const statCards = computed(() => [
  { label: '总交易数', value: stats.value.total_transactions || 0, icon: 'Wallet', color: '#409EFF' },
  { label: '待办事项', value: stats.value.pending_todos || 0, icon: 'Finished', color: '#E6A23C' },
  { label: '运动次数', value: stats.value.total_exercises || 0, icon: 'Trophy', color: '#67C23A' },
  { label: '在读图书', value: stats.value.reading_books || 0, icon: 'Reading', color: '#909399' },
  { label: '活跃习惯', value: stats.value.active_habits || 0, icon: 'AlarmClock', color: '#F56C6C' },
  { label: '进行中目标', value: stats.value.active_goals || 0, icon: 'Flag', color: '#8B5CF6' },
])

onMounted(async () => {
  try {
    const [s, t] = await Promise.all([
      dashboardApi.getStats(),
      dashboardApi.getFinanceTrend(new Date().getFullYear()),
    ])
    stats.value = s
    trend.value = t
    renderChart()
  } catch (e) {
    console.error(e)
  }
})

function renderChart() {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['收入', '支出'] },
    grid: { left: 60, right: 30, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: trend.value.map(i => i.month) },
    yAxis: { type: 'value', axisLabel: { formatter: '¥{value}' } },
    series: [
      { name: '收入', type: 'bar', data: trend.value.map(i => i.income), itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: '支出', type: 'bar', data: trend.value.map(i => i.expense), itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] } },
    ],
  })
  window.addEventListener('resize', () => chart.resize())
}
</script>

<style scoped lang="scss">
.today {
  color: #909399;
  font-size: 14px;
}

.stat-row {
  .el-col {
    margin-bottom: 16px;
  }
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  text-align: center;
  transition: transform 0.2s;

  &:hover { transform: translateY(-3px); }

  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 700;
    color: #303133;
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 13px;
    color: #909399;
  }
}

.overview-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  font-size: 14px;
  color: #606266;
  border-bottom: 1px solid #f5f5f5;

  &:last-child { border-bottom: none; }

  .income { color: #67C23A; font-weight: 600; }
  .expense { color: #F56C6C; font-weight: 600; }
}
</style>
