<template>
  <el-container class="app-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="28"><Wallet /></el-icon>
        <h2>校园记账</h2>
      </div>
      <el-menu
        :default-active="activeTab"
        class="sidebar-menu"
        @select="handleSelect"
      >
        <el-menu-item index="dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
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
    </el-aside>

    <el-main class="main-content">
      <transition name="fade" mode="out-in">
        <component :is="currentComponent" :key="activeTab" />
      </transition>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, shallowRef, onMounted, type Component } from 'vue'
import {
  Wallet, Plus, Document, DataAnalysis, TrendCharts,
  Setting, HomeFilled
} from '@element-plus/icons-vue'
import DashboardTab from './components/DashboardTab.vue'
import ExpenseTab from './components/ExpenseTab.vue'
import RecordsTab from './components/RecordsTab.vue'
import StatisticsTab from './components/StatisticsTab.vue'
import BudgetTab from './components/BudgetTab.vue'
import SettingsTab from './components/SettingsTab.vue'
import { useTheme } from './composables/useTheme'

const activeTab = ref('dashboard')
const currentComponent = shallowRef<Component>(DashboardTab)
const { initTheme } = useTheme()

const componentMap: Record<string, Component> = {
  dashboard: DashboardTab,
  expense: ExpenseTab,
  records: RecordsTab,
  statistics: StatisticsTab,
  budget: BudgetTab,
  settings: SettingsTab
}

const handleSelect = (index: string): void => {
  activeTab.value = index
  currentComponent.value = componentMap[index] ?? DashboardTab
}

onMounted(() => {
  initTheme()
})
</script>

<style>
.app-container {
  height: 100vh;
  background: var(--el-bg-color-page);
}

.sidebar {
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
  transition: background 0.3s, border-color 0.3s;
}

.logo {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.logo h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  padding: 8px;
}

.sidebar-menu .el-menu-item {
  border-radius: 8px;
  margin-bottom: 4px;
  height: 44px;
  line-height: 44px;
  font-size: 14px;
  transition: background 0.2s, color 0.2s;
}

.sidebar-menu .el-menu-item.is-active {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-weight: 600;
}

.sidebar-menu .el-menu-item:hover {
  background: var(--el-color-primary-light-9);
}

.main-content {
  padding: 28px;
  overflow-y: auto;
  background: var(--el-bg-color-page);
  transition: background 0.3s;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
