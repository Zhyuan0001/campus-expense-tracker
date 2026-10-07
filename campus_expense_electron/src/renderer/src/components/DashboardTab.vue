<template>
  <div ref="dashboardRef" class="dashboard-tab" v-loading="loading">
    <div class="stat-cards">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-card-inner">
          <div class="stat-icon" style="background: var(--el-color-primary-light-9)">
            <el-icon :size="28" color="var(--el-color-primary)"><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">本月支出</div>
            <div class="stat-value primary">¥{{ monthlyTotal.toFixed(2) }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-card-inner">
          <div class="stat-icon" style="background: var(--el-color-success-light-9)">
            <el-icon :size="28" color="var(--el-color-success)"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">剩余预算</div>
            <div class="stat-value" :style="{ color: remainingColor }">
              {{ hasBudget ? `¥${budgetRemaining.toFixed(2)}` : '未设置' }}
            </div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-card-inner">
          <div class="stat-icon" style="background: var(--el-color-warning-light-9)">
            <el-icon :size="28" color="var(--el-color-warning)"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">本月笔数</div>
            <div class="stat-value">{{ recordCount }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-card-inner">
          <div class="stat-icon" style="background: var(--el-color-danger-light-9)">
            <el-icon :size="28" color="var(--el-color-danger)"><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">日均消费</div>
            <div class="stat-value">¥{{ dailyAvg.toFixed(2) }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon :size="18"><PieChart /></el-icon>
            <span>分类占比</span>
          </div>
        </template>
        <div ref="pieChartRef" class="chart" v-if="categoryData.length > 0"></div>
        <el-empty v-else description="本月暂无数据" :image-size="80" />
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon :size="18"><TrendCharts /></el-icon>
            <span>近6月趋势</span>
          </div>
        </template>
        <div ref="lineChartRef" class="chart" v-if="trendData.length > 0"></div>
        <el-empty v-else description="暂无趋势数据" :image-size="80" />
      </el-card>
    </div>

    <el-card class="recent-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="18"><List /></el-icon>
          <span>最近记录</span>
        </div>
      </template>
      <el-table :data="recentExpenses" stripe v-if="recentExpenses.length > 0">
        <el-table-column prop="date" label="日期" width="110" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ getCategoryIcon(row.category) }} {{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="amount" label="金额" width="110" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount.toFixed(2) }}</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无记录" :image-size="60" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Wallet, TrendCharts, Document, DataLine, PieChart, List } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { api, type Expense, type CategoryStat } from '@/api'
import { CATEGORY_COLORS, getCategoryIcon, getChartTextColor, getChartBorderColor } from '@/utils/constants'

const loading = ref(false)
const monthlyTotal = ref(0)
const budgetRemaining = ref(0)
const budgetPercentage = ref(0)
const hasBudget = ref(false)
const recordCount = ref(0)
const categoryData = ref<CategoryStat[]>([])
const trendData = ref<{ month: string; total: number }[]>([])
const recentExpenses = ref<Expense[]>([])

const dashboardRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
const lineChartRef = ref<HTMLElement>()
let pieChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const dailyAvg = computed(() => {
  const day = new Date().getDate()
  return day > 0 ? monthlyTotal.value / day : 0
})

// 与预算页共用同一套阈值：<80% 绿、80%-100% 黄、>100% 红
const remainingColor = computed(() => {
  if (!hasBudget.value) return 'var(--el-text-color-secondary)'
  if (budgetPercentage.value > 100) return 'var(--el-color-danger)'
  if (budgetPercentage.value >= 80) return 'var(--el-color-warning)'
  return 'var(--el-color-success)'
})

const renderPieChart = (): void => {
  if (!pieChartRef.value || categoryData.value.length === 0) return
  if (!pieChart) pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    series: [
      {
        type: 'pie',
        radius: ['45%', '72%'],
        center: ['50%', '55%'],
        itemStyle: { borderRadius: 6, borderColor: getChartBorderColor(), borderWidth: 2 },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold', color: getChartTextColor() },
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.15)' }
        },
        data: categoryData.value.map((item, i) => ({
          value: item.total,
          name: item.category,
          itemStyle: { color: CATEGORY_COLORS[i % CATEGORY_COLORS.length] }
        }))
      }
    ]
  })
}

const renderLineChart = (): void => {
  if (!lineChartRef.value || trendData.value.length === 0) return
  if (!lineChart) lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>支出: ¥{c}' },
    grid: { left: '10%', right: '5%', top: '10%', bottom: '15%' },
    xAxis: {
      type: 'category',
      data: trendData.value.map((d) => d.month),
      axisLabel: { fontSize: 11, color: getChartTextColor() }
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '¥{value}', fontSize: 11, color: getChartTextColor() }
    },
    series: [
      {
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.12 },
        lineStyle: { width: 3, color: '#6366F1' },
        itemStyle: { color: '#6366F1' },
        data: trendData.value.map((d) => d.total)
      }
    ]
  })
}

const loadData = async (): Promise<void> => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1

  loading.value = true
  try {
    const [statsRes, budgetRes, expensesRes] = await Promise.all([
      api.getStatistics(year, month),
      api.getBudget(),
      api.getExpenses(year, month)
    ])

    monthlyTotal.value = statsRes.data.total
    categoryData.value = statsRes.data.categories
    budgetRemaining.value = budgetRes.data.remaining
    budgetPercentage.value = budgetRes.data.percentage
    hasBudget.value = budgetRes.data.monthly_budget !== null
    recordCount.value = expensesRes.data.length
    recentExpenses.value = expensesRes.data.slice(0, 5)
  } catch {
    ElMessage.error('加载首页数据失败')
  }

  try {
    const months: { d: Date; label: string }[] = []
    for (let i = 5; i >= 0; i--) {
      const d = new Date(year, month - 1 - i, 1)
      months.push({ d, label: `${d.getMonth() + 1}月` })
    }
    const results = await Promise.all(
      months.map((m) => api.getStatistics(m.d.getFullYear(), m.d.getMonth() + 1))
    )
    trendData.value = months.map((m, i) => ({
      month: m.label,
      total: results[i].data.total
    }))
  } catch {
    ElMessage.error('加载趋势数据失败')
  }

  loading.value = false
  await nextTick()
  renderPieChart()
  renderLineChart()
}

onMounted(() => {
  loadData()
  // 用 ResizeObserver 跟"容器"走：窗口缩放、侧栏折叠都会改变内容区宽度，
  // 而 window.resize 在侧栏折叠时并不触发，图表会保持旧宽度
  if (dashboardRef.value && typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => {
      pieChart?.resize()
      lineChart?.resize()
    })
    resizeObserver.observe(dashboardRef.value)
  }
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  pieChart?.dispose()
  lineChart?.dispose()
})
</script>

<style scoped>
.dashboard-tab {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 200px;
}

/* auto-fit：列数随可用宽度连续变化，不必为每个断点各写一条规则 */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr));
  gap: 16px;
}

.stat-card-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
  white-space: nowrap;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-value.primary {
  color: var(--el-color-primary);
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(360px, 100%), 1fr));
  gap: 16px;
}

.chart-card {
  border-radius: 12px;
}

.chart {
  /* 高度跟随视口，矮窗自动压缩 */
  height: clamp(200px, 32vh, 300px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
}

.recent-card {
  border-radius: 12px;
}

.amount {
  font-weight: 600;
  color: var(--el-color-danger);
}
</style>
