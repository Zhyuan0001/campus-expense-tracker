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

      <div class="filter-bar">
        <el-input
          v-model="keyword"
          placeholder="搜索描述 / 分类"
          clearable
          class="filter-keyword"
          @keyup.enter="applyFilters"
          @clear="applyFilters"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select
          v-model="filterCategory"
          placeholder="全部分类"
          clearable
          class="filter-category"
          @change="applyFilters"
        >
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="`${cat.icon} ${cat.name}`"
            :value="cat.name"
          />
        </el-select>
        <el-button type="primary" @click="applyFilters">
          <el-icon><Search /></el-icon>
          筛选
        </el-button>
        <el-button v-if="hasActiveFilters" @click="resetFilters">重置</el-button>
        <span v-if="hasActiveFilters" class="filter-count">匹配 {{ expenses.length }} 条</span>
      </div>

      <el-table
        :data="pagedExpenses"
        stripe
        style="width: 100%"
        v-loading="loading"
        empty-text="暂无记录"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="date" label="日期" width="115" />
        <el-table-column prop="category" label="分类" min-width="110">
          <template #default="{ row }">
            <el-tag>{{ getCategoryIcon(row.category) }} {{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip min-width="160" />
        <el-table-column prop="amount" label="金额" width="110" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="110" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="openEdit(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
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
          :page-sizes="[10, 20, 50]"
          :total="expenses.length"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-card>

    <el-dialog v-model="editVisible" title="编辑记录" width="480px">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="70px">
        <el-form-item label="金额" prop="amount">
          <el-input-number
            v-model="editForm.amount"
            :min="0.01"
            :precision="2"
            :step="10"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="editForm.category" placeholder="选择分类" style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="`${cat.icon} ${cat.name}`"
              :value="cat.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="2"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="editForm.date"
            type="date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Document, Delete, Edit, Search } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { api, type Category, type Expense } from '@/api'
import { getCategoryIcon } from '@/utils/constants'

const expenses = ref<Expense[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const filterDate = ref('')
const keyword = ref('')
const filterCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const hasActiveFilters = computed(() =>
  Boolean(keyword.value || filterCategory.value || filterDate.value)
)

const pagedExpenses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return expenses.value.slice(start, start + pageSize.value)
})

const loadExpenses = async (): Promise<void> => {
  loading.value = true
  try {
    let year: number | undefined
    let month: number | undefined
    if (filterDate.value) {
      const parts = filterDate.value.split('-').map(Number)
      year = parts[0]
      month = parts[1]
    }
    const res = await api.getExpenses(year, month, {
      keyword: keyword.value || undefined,
      category: filterCategory.value || undefined
    })
    expenses.value = res.data
  } catch {
    ElMessage.error('加载记录失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async (): Promise<void> => {
  try {
    categories.value = (await api.getCategories()).data
  } catch {
    // 分类加载失败不阻塞记录列表本身
  }
}

const applyFilters = (): void => {
  currentPage.value = 1
  loadExpenses()
}

const resetFilters = (): void => {
  keyword.value = ''
  filterCategory.value = ''
  filterDate.value = ''
  applyFilters()
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

const editVisible = ref(false)
const saving = ref(false)
const editFormRef = ref<FormInstance>()
const editingId = ref<number | null>(null)
const editForm = ref({ amount: 0, category: '', description: '', date: '' })

const editRules: FormRules = {
  amount: [
    { required: true, message: '请输入金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
  ],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

const openEdit = (row: Expense): void => {
  editingId.value = row.id
  editForm.value = {
    amount: row.amount,
    category: row.category,
    description: row.description,
    date: row.date
  }
  editVisible.value = true
}

const submitEdit = async (): Promise<void> => {
  if (!editFormRef.value || editingId.value === null) return
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const amount = Number(editForm.value.amount.toFixed(2))
      await api.updateExpense(editingId.value as number, { ...editForm.value, amount })
      ElMessage.success('保存成功')
      editVisible.value = false
      await loadExpenses()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

watch(filterDate, () => {
  currentPage.value = 1
  loadExpenses()
})

onMounted(() => {
  loadCategories()
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

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.filter-keyword {
  width: 220px;
}

.filter-category {
  width: 160px;
}

.filter-count {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  margin-left: auto;
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
