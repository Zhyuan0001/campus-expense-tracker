<template>
  <el-container class="app-container">
    <!-- 侧边栏导航 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="32"><Wallet /></el-icon>
        <h2>校园记账</h2>
      </div>
      <el-menu :default-active="activeTab" class="sidebar-menu" @select="handleSelect">
        <el-menu-item index="expense">
          <el-icon><Plus /></el-icon>
          <span>记账</span>
        </el-menu-item>
        <el-menu-item index="records">
          <el-icon><Document /></el-icon>
          <span>记录</span>
        </el-menu-item>
        <el-menu-item index="statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计</span>
        </el-menu-item>
        <el-menu-item index="budget">
          <el-icon><TrendCharts /></el-icon>
          <span>预算</span>
        </el-menu-item>
        <el-menu-item index="settings">
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </el-menu-item>
      </el-menu>
      <div class="theme-switch">
        <el-switch
          v-model="isDark"
          :active-action-icon="Moon"
          :inactive-action-icon="Sunny"
          @change="toggleTheme"
        />
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-main class="main-content">
      <transition name="fade" mode="out-in">
        <component :is="currentComponent" :key="activeTab" />
      </transition>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, shallowRef, onMounted } from 'vue'
import {
  Wallet,
  Plus,
  Document,
  DataAnalysis,
  TrendCharts,
  Setting,
  Moon,
  Sunny,
} from '@element-plus/icons-vue'
import ExpenseTab from './components/ExpenseTab.vue'
import RecordsTab from './components/RecordsTab.vue'
import StatisticsTab from './components/StatisticsTab.vue'
import BudgetTab from './components/BudgetTab.vue'
import SettingsTab from './components/SettingsTab.vue'

const activeTab = ref('expense')
const isDark = ref(false)

const currentComponent = shallowRef(ExpenseTab)

const componentMap: Record<string, any> = {
  expense: ExpenseTab,
  records: RecordsTab,
  statistics: StatisticsTab,
  budget: BudgetTab,
  settings: SettingsTab,
}

const handleSelect = (index: string) => {
  activeTab.value = index
  currentComponent.value = componentMap[index]
}

const toggleTheme = () => {
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  isDark.value = savedTheme === 'dark'
  document.documentElement.classList.toggle('dark', isDark.value)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
}

.app-container {
  height: 100vh;
  background: var(--el-bg-color-page);
}

.sidebar {
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
}

.logo {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.logo h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  padding: 12px 8px;
}

.sidebar-menu .el-menu-item {
  border-radius: 8px;
  margin-bottom: 8px;
  height: 48px;
  line-height: 48px;
  font-size: 15px;
}

.sidebar-menu .el-menu-item.is-active {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-weight: 600;
}

.theme-switch {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: center;
}

.main-content {
  padding: 32px;
  overflow-y: auto;
  background: var(--el-bg-color-page);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 暗色主题优化 */
html.dark {
  --el-bg-color: #1a1a1a;
  --el-bg-color-page: #0d0d0d;
  --el-border-color-light: #2a2a2a;
}
</style>
