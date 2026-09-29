<template>
  <div class="records-tab">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="20"><Document /></el-icon>
          <h2>消费记录</h2>
          <el-date-picker
            v-model="filterDate"
            type="month"
            placeholder="按月筛选"
            format="YYYY-MM"
            value-format="YYYY-MM"
            style="margin-left: auto"
            clearable
          />
        </div>
      </template>

      <el-table
        :data="pagedExpenses"
        stripe
        style="width: 100%"
        v-loading="loading"
        empty-text="暂无记录"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="category" label="分类" min-width="120">
          <template #default="{ row }">
            <el-tag>{{ getCategoryIcon(row.category) }} {{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip min-width="200" />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              title="确定删除这条记录吗？"
              @confirm="deleteExpense(row.id)"
            >
              <template #reference>
                <el-button type="danger" size="small" text>
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="expenses.length"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Document, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { api, type Expense } from '@/api'
import { getCategoryIcon } from '@/utils/constants'

const expenses = ref<Expense[]>([])
const loading = ref(false)
const filterDate = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const pagedExpenses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return expenses.value.slice(start, start + pageSize.value)
})

const loadExpenses = async (): Promise<void> => {
  loading.value = true
  try {
    const params: { year?: number; month?: number } = {}
    if (filterDate.value) {
      const [year, month] = filterDate.value.split('-').map(Number)
      params.year = year
      params.month = month
    }
    const res = await api.getExpenses(params.year, params.month)
    expenses.value = res.data
  } catch {
    ElMessage.error('加载记录失败')
  } finally {
    loading.value = false
  }
}

const deleteExpense = async (id: number): Promise<void> => {
  try {
    await api.deleteExpense(id)
    ElMessage.success('删除成功')
    await loadExpenses()
  } catch {
    ElMessage.error('删除失败')
  }
}

watch(filterDate, () => {
  currentPage.value = 1
  loadExpenses()
})

onMounted(() => {
  loadExpenses()
})
</script>

<style scoped>
.records-tab {
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

.amount {
  font-weight: 600;
  color: var(--el-color-danger);
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
