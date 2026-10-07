<template>
  <div ref="statsRef" class="statistics-tab">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="20"><DataAnalysis /></el-icon>
          <h2>分类统计</h2>
          <el-date-picker
            v-model="selectedMonth"
            type="month"
            placeholder="选择月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
            style="margin-left: auto"
          />
        </div>
      </template>

      <div class="stats-content" v-loading="loading">
        <div class="total-card">
          <div class="total-label">{{ selectedMonth }} 总支出</div>
          <div class="total-amount">¥{{ total.toFixed(2) }}</div>
        </div>

        <div class="chart-container" v-if="categoryData.length > 0">
          <div ref="chartRef" class="pie-chart"></div>
        </div>

        <el-empty v-else description="该月暂无数据" />

        <div class="category-list" v-if="categoryData.length > 0">
          <el-table :data="categoryData" stripe>
            <el-table-column prop="category" label="分类" width="150">
              <template #default="{ row }">
                <el-tag>{{ getCategoryIcon(row.category) }} {{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total" label="金额" align="right">
              <template #default="{ row }">
                <span class="amount">¥{{ row.total.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="占比" width="150" align="right">
              <template #default="{ row }">
                <span class="percentage">{{ ((row.total / total) * 100).toFixed(1) }}%</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { api, type CategoryStat } from '@/api'
import {
  CATEGORY_COLORS,
  getCategoryIcon,
  getChartTextColor,
  getChartBorderColor,
  thisMonthLocal
} from '@/utils/constants'
import { useLayout } from '@/composables/useLayout'

const selectedMonth = ref(thisMonthLocal())
const loading = ref(false)
const total = ref(0)
const categoryData = ref<CategoryStat[]>([])
const chartRef = ref<HTMLElement>()
const statsRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const { isPortrait } = useLayout()

// legend 随比例换位：横窗放右侧（省纵向），竖窗移到底部（右侧竖排会挤压饼图）
const legendOption = computed(() =>
  isPortrait.value
    ? { orient: 'horizontal' as const, bottom: 0, left: 'center' as const }
    : { orient: 'vertical' as const, right: '5%', top: 'center' as const }
)

const loadStatistics = async (): Promise<void> => {
  if (!selectedMonth.value) return

  loading.value = true
  try {
    const parts = selectedMonth.value.split('-').map(Number)
    const res = await api.getStatistics(parts[0], parts[1])

    total.value = res.data.total
    categoryData.value = res.data.categories

    await nextTick()
    renderChart()
  } catch {
    ElMessage.error('加载统计失败')
  } finally {
    loading.value = false
  }
}

const renderChart = (): void => {
  if (!chartRef.value || categoryData.value.length === 0) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      ...legendOption.value,
      textStyle: { color: getChartTextColor() }
    },
    series: [
      {
        name: '消费分类',
        type: 'pie',
        radius: ['42%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: getChartBorderColor(),
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 15, fontWeight: 'bold', color: getChartTextColor() },
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.15)' }
        },
        data: categoryData.value.map((item, index) => ({
          value: item.total,
          name: item.category,
          itemStyle: { color: CATEGORY_COLORS[index % CATEGORY_COLORS.length] }
        }))
      }
    ]
  })
}

watch(selectedMonth, () => {
  loadStatistics()
})

// 竖窗/横窗切换时图例位置要重排
watch(isPortrait, () => {
  renderChart()
})

onMounted(async () => {
  await loadStatistics()
  // 跟容器走：侧栏折叠或窗口缩放都能触发重绘
  if (statsRef.value && typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => chart?.resize())
    resizeObserver.observe(statsRef.value)
  }
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
})
</script>

<style scoped>
.statistics-tab {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
}

.card-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
}

.stats-content {
  padding: 12px 0;
}

.total-card {
  text-align: center;
  padding: 28px;
  background: linear-gradient(
    135deg,
    var(--el-color-primary-light-9) 0%,
    var(--el-color-primary-light-7) 100%
  );
  border-radius: 12px;
  margin-bottom: 28px;
}

.total-label {
  font-size: 15px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.total-amount {
  font-size: 38px;
  font-weight: 700;
  color: var(--el-color-danger);
}

.chart-container {
  margin-bottom: 28px;
}

.pie-chart {
  width: 100%;
  /* 高度随视口，矮窗自动压缩 */
  height: clamp(260px, 40vh, 380px);
}

.category-list {
  margin-top: 20px;
}

.amount {
  font-weight: 600;
  color: var(--el-color-danger);
}

.percentage {
  color: var(--el-text-color-secondary);
}
</style>
