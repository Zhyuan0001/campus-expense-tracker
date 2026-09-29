<template>
  <div class="settings-tab">
    <el-card shadow="hover" class="settings-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="20"><Setting /></el-icon>
          <h2>分类管理</h2>
        </div>
      </template>

      <div class="category-management">
        <el-form :inline="true" :model="newCategory" class="add-form">
          <el-form-item label="新分类名称">
            <el-input
              v-model="newCategory.name"
              placeholder="输入分类名称"
              maxlength="20"
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="图标">
            <el-input
              v-model="newCategory.icon"
              placeholder="Emoji图标"
              style="width: 100px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="addCategory" :loading="adding">
              添加分类
            </el-button>
          </el-form-item>
        </el-form>

        <el-table :data="categories" stripe style="width: 100%; margin-top: 20px">
          <el-table-column prop="icon" label="图标" width="80" align="center">
            <template #default="{ row }">
              <span style="font-size: 22px">{{ row.icon }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="分类名称" />
          <el-table-column label="类型" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.is_default" type="info">默认</el-tag>
              <el-tag v-else type="success">自定义</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center">
            <template #default="{ row }">
              <el-popconfirm
                v-if="!row.is_default"
                title="确定删除这个分类吗？"
                @confirm="deleteCategory(row.id)"
              >
                <template #reference>
                  <el-button type="danger" size="small" text>
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
              <span v-else style="color: var(--el-text-color-placeholder)">不可删除</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <el-card shadow="hover" class="settings-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="20"><Download /></el-icon>
          <h2>数据导出</h2>
        </div>
      </template>

      <div class="export-section">
        <p style="color: var(--el-text-color-secondary); margin-bottom: 16px">
          导出所有消费记录为CSV文件，可用于备份或数据分析
        </p>
        <el-button type="primary" size="large" @click="exportData" :loading="exporting">
          <el-icon><Download /></el-icon>
          导出CSV
        </el-button>
      </div>
    </el-card>

    <el-card shadow="hover" class="settings-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="20"><InfoFilled /></el-icon>
          <h2>关于</h2>
        </div>
      </template>

      <div class="about-section">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="应用名称">校园消费记账系统</el-descriptions-item>
          <el-descriptions-item label="版本">3.0 (Electron)</el-descriptions-item>
          <el-descriptions-item label="技术栈">Electron + Vue3 + TypeScript + Element Plus + FastAPI</el-descriptions-item>
          <el-descriptions-item label="特点">
            <el-tag type="success">便携版</el-tag>
            <el-tag type="success">现代化UI</el-tag>
            <el-tag type="success">高DPI支持</el-tag>
            <el-tag type="success">跨平台</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Setting, Delete, Download, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { api, type Category } from '@/api'

const categories = ref<Category[]>([])
const adding = ref(false)
const exporting = ref(false)
const newCategory = ref({
  name: '',
  icon: '📌'
})

const loadCategories = async (): Promise<void> => {
  try {
    const res = await api.getCategories()
    categories.value = res.data
  } catch {
    ElMessage.error('加载分类失败')
  }
}

const addCategory = async (): Promise<void> => {
  if (!newCategory.value.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }

  adding.value = true
  try {
    await api.createCategory(newCategory.value)
    ElMessage.success('分类添加成功')
    newCategory.value = { name: '', icon: '📌' }
    await loadCategories()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  } finally {
    adding.value = false
  }
}

const deleteCategory = async (id: number): Promise<void> => {
  try {
    await api.deleteCategory(id)
    ElMessage.success('删除成功')
    await loadCategories()
  } catch {
    ElMessage.error('删除失败')
  }
}

const exportData = async (): Promise<void> => {
  exporting.value = true
  try {
    const res = await api.exportCSV()
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    const today = new Date().toISOString().split('T')[0]
    link.setAttribute('download', `campus_expenses_${today}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.settings-tab {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.add-form {
  padding: 12px 0;
}

.export-section,
.about-section {
  padding: 12px 0;
}
</style>
