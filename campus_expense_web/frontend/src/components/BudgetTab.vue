<template>
  <div class="budget-tab">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><TrendCharts /></el-icon>
          <h2>月度预算</h2>
        </div>
      </template>

      <div class="budget-content">
        <el-form :model="budgetForm" label-width="120px" size="large">
          <el-form-item label="设置月预算">
            <el-input-number
              v-model="budgetForm.amount"
              :min="0"
              :precision="2"
              :step="100"
              placeholder="输入月度预算金额"
              style="width: 300px"
            />
            <el-button
              type="primary"
              @click="setBudget"
              :loading="saving"
              style="margin-left: 16px"
            >
              保存
            </el-button>
          </el-form-item>
        </el-form>

        <div class="budget-overview" v-if="budgetData.monthly_budget">
          <el-progress
            :percentage="Math.min(budgetData.percentage, 100)"
            :color="progressColor"
            :stroke-width="24"
            :text-inside="true"
            style="margin: 32px 0"
          />

          <div class="budget-stats">
            <div class="stat-card">
              <div class="stat-icon" style="background: var(--el-color-primary-light-9)">
                <el-icon :size="32" color="var(--el-color-primary)"><Wallet /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">月度预算</div>
                <div class="stat-value">¥{{ budgetData.monthly_budget.toFixed(2) }}</div>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon" style="background: var(--el-color-danger-light-9)">
                <el-icon :size="32" color="var(--el-color-danger)"><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">已使用</div>
                <div class="stat-value">¥{{ budgetData.spent.toFixed(2) }}</div>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon" :style="{ background: remainingColor.bg }">
                <el-icon :size="32" :color="remainingColor.icon"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">剩余</div>
                <div class="stat-value" :style="{ color: remainingColor.icon }">
                  ¥{{ budgetData.remaining.toFixed(2) }}
                </div>
              </div>
            </div>
          </div>

          <el-alert
            v-if="budgetData.percentage > 100"
            title="预算超支警告"
            type="error"
            :description="`本月已超支 ¥${Math.abs(budgetData.remaining).toFixed(2)}，请注意控制开支！`"
            show-icon
            :closable="false"
            style="margin-top: 24px"
          />
          <el-alert
            v-else-if="budgetData.percentage > 80"
            title="预算使用提醒"
            type="warning"
            :description="`已使用 ${budgetData.percentage.toFixed(1)}%，剩余 ¥${budgetData.remaining.toFixed(2)}`"
            show-icon
            :closable="false"
            style="margin-top: 24px"
          />
          <el-alert
            v-else
            title="预算状态良好"
            type="success"
            :description="`已使用 ${budgetData.percentage.toFixed(1)}%，剩余 ¥${budgetData.remaining.toFixed(2)}`"
            show-icon
            :closable="false"
            style="margin-top: 24px"
          />
        </div>

        <el-empty v-else description="尚未设置月度预算" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { TrendCharts, Wallet, Money } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api'

interface BudgetData {
  monthly_budget: number | null
  spent: number
  remaining: number
  percentage: number
}

const budgetForm = ref({ amount: 0 })
const budgetData = ref<BudgetData>({
  monthly_budget: null,
  spent: 0,
  remaining: 0,
  percentage: 0
})
const saving = ref(false)

const progressColor = computed(() => {
  if (budgetData.value.percentage > 100) return '#f56c6c'
  if (budgetData.value.percentage > 80) return '#e6a23c'
  return '#67c23a'
})

const remainingColor = computed(() => {
  if (budgetData.value.remaining < 0) {
    return { bg: 'var(--el-color-danger-light-9)', icon: 'var(--el-color-danger)' }
  }
  if (budgetData.value.percentage > 80) {
    return { bg: 'var(--el-color-warning-light-9)', icon: 'var(--el-color-warning)' }
  }
  return { bg: 'var(--el-color-success-light-9)', icon: 'var(--el-color-success)' }
})

const loadBudget = async () => {
  try {
    const res = await axios.get(`${API_BASE}/budget`)
    budgetData.value = res.data
    if (res.data.monthly_budget) {
      budgetForm.value.amount = res.data.monthly_budget
    }
  } catch (error) {
    console.error('加载预算失败', error)
  }
}

const setBudget = async () => {
  if (budgetForm.value.amount <= 0) {
    ElMessage.warning('请输入有效的预算金额')
    return
  }

  saving.value = true
  try {
    await axios.put(`${API_BASE}/budget`, { amount: budgetForm.value.amount })
    ElMessage.success('预算设置成功')
    await loadBudget()
  } catch (error) {
    ElMessage.error('设置失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadBudget()
})
</script>

<style scoped>
.budget-tab {
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.budget-content {
  padding: 16px 0;
}

.budget-overview {
  margin-top: 32px;
}

.budget-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin: 32px 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: var(--el-bg-color);
  border-radius: 12px;
  border: 1px solid var(--el-border-color-light);
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
}
</style>
