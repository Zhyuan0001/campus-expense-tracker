<template>
  <div class="expense-tab">
    <el-card class="expense-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Plus /></el-icon>
          <h2>添加消费记录</h2>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        size="large"
        class="expense-form"
      >
        <el-form-item label="金额" prop="amount">
          <el-input-number
            v-model="form.amount"
            :min="0.01"
            :precision="2"
            :step="10"
            placeholder="请输入金额"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="选择分类" style="width: 100%">
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
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="添加描述（可选）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="form.date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            @click="submitForm"
            :loading="submitting"
            style="width: 100%"
          >
            <el-icon><Check /></el-icon>
            <span>保存记录</span>
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 今日消费概览 -->
    <el-card class="overview-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><DataLine /></el-icon>
          <h3>本月概览</h3>
        </div>
      </template>
      <div class="overview-stats">
        <div class="stat-item">
          <div class="stat-label">本月支出</div>
          <div class="stat-value">¥{{ monthlyTotal.toFixed(2) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">记录笔数</div>
          <div class="stat-value">{{ recordCount }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Check, DataLine } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api'

interface Category {
  id: number
  name: string
  icon: string
}

const formRef = ref<FormInstance>()
const categories = ref<Category[]>([])
const submitting = ref(false)
const monthlyTotal = ref(0)
const recordCount = ref(0)

const form = ref({
  amount: 0,
  category: '',
  description: '',
  date: new Date().toISOString().split('T')[0]
})

const rules: FormRules = {
  amount: [
    { required: true, message: '请输入金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ]
}

const loadCategories = async () => {
  try {
    const res = await axios.get(`${API_BASE}/categories`)
    categories.value = res.data
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

const loadMonthlyStats = async () => {
  try {
    const now = new Date()
    const res = await axios.get(`${API_BASE}/statistics/${now.getFullYear()}/${now.getMonth() + 1}`)
    monthlyTotal.value = res.data.total
    const expensesRes = await axios.get(`${API_BASE}/expenses`, {
      params: { year: now.getFullYear(), month: now.getMonth() + 1 }
    })
    recordCount.value = expensesRes.data.length
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await axios.post(`${API_BASE}/expenses`, form.value)
      ElMessage.success('记录保存成功')
      
      // 重置表单
      form.value = {
        amount: 0,
        category: '',
        description: '',
        date: new Date().toISOString().split('T')[0]
      }
      formRef.value?.resetFields()
      
      // 刷新统计
      await loadMonthlyStats()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  loadCategories()
  loadMonthlyStats()
})
</script>

<style scoped>
.expense-tab {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.expense-card,
.overview-card {
  border-radius: 12px;
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

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.expense-form {
  padding: 16px 0;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  padding: 16px 0;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--el-color-primary);
}
</style>
