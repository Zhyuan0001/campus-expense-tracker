<template>
  <div class="records-tab">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Document /></el-icon>
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
        :data="expenses"
        stripe
        style="width: 100%"
        v-loading="loading"
        empty-text="暂无记录"
      >
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag>{{ getCategoryIcon(row.category) }} {{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-popconfirm title="确定删除这条记录吗？" @confirm="deleteExpense(row.id)">
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
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="loadExpenses"
          @current-change="loadExpenses"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Document, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api'

interface Expense {
  id: number
  amount: number
  category: string
  description: string
  date: string
}

interface Category {
  id: number
  name: string
  icon: string
}

const expenses = ref<Expense[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const filterDate = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadExpenses = async () => {
  loading.value = true
  try {
    let url = `${API_BASE}/expenses`
    const params: any = {}

    if (filterDate.value) {
      const [year, month] = filterDate.value.split('-').map(Number)
      params.year = year
      params.month = month
    }

    const res = await axios.get(url, { params })
    const allExpenses = res.data

    total.value = allExpenses.length
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    expenses.value = allExpenses.slice(start, end)
  } catch (error) {
    ElMessage.error('加载记录失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const res = await axios.get(`${API_BASE}/categories`)
    categories.value = res.data
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

const getCategoryIcon = (categoryName: string) => {
  const cat = categories.value.find((c) => c.name === categoryName)
  return cat ? cat.icon : '📌'
}

const deleteExpense = async (id: number) => {
  try {
    await axios.delete(`${API_BASE}/expenses/${id}`)
    ElMessage.success('删除成功')
    await loadExpenses()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

watch(filterDate, () => {
  currentPage.value = 1
  loadExpenses()
})

onMounted(() => {
  loadExpenses()
  loadCategories()
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
  gap: 12px;
}

.card-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.amount {
  font-weight: 600;
  color: var(--el-color-danger);
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
