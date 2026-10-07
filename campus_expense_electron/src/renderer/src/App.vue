<template>
  <el-container
    :class="['app-container', `nav-${navMode}`, { 'compact-height': isCompactHeight }]"
  >
    <!-- 侧边导航（非底部模式） -->
    <el-aside v-if="navMode !== 'bottom'" :width="asideWidth" class="sidebar">
      <div class="logo">
        <el-icon :size="28"><Wallet /></el-icon>
        <h2 v-show="navMode === 'full'">校园记账</h2>
      </div>
      <el-menu
        :default-active="activeTab"
        class="sidebar-menu"
        :collapse="navMode === 'rail'"
        :collapse-transition="false"
        @select="handleSelect"
      >
        <el-menu-item v-for="item in navItems" :key="item.key" :index="item.key">
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.label }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容 -->
    <el-main class="main-content">
      <transition name="fade" mode="out-in">
        <component :is="currentComponent" :key="activeTab" />
      </transition>
    </el-main>

    <!-- 底部标签栏（竖窗 / 窄窗） -->
    <nav v-if="navMode === 'bottom'" class="bottom-tab">
      <button
        v-for="item in navItems"
        :key="item.key"
        class="tab-item"
        :class="{ active: activeTab === item.key }"
        @click="handleSelect(item.key)"
      >
        <el-icon :size="20"><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </button>
    </nav>
  </el-container>
</template>

<script setup lang="ts">
import { ref, shallowRef, computed, onMounted, type Component } from 'vue'
import {
  Wallet,
  Plus,
  Document,
  DataAnalysis,
  TrendCharts,
  Setting,
  HomeFilled
} from '@element-plus/icons-vue'
import DashboardTab from './components/DashboardTab.vue'
import ExpenseTab from './components/ExpenseTab.vue'
import RecordsTab from './components/RecordsTab.vue'
import StatisticsTab from './components/StatisticsTab.vue'
import BudgetTab from './components/BudgetTab.vue'
import SettingsTab from './components/SettingsTab.vue'
import { useTheme } from './composables/useTheme'
import { useLayout } from './composables/useLayout'

const activeTab = ref('dashboard')
const { initTheme } = useTheme()
const { navMode, isCompactHeight } = useLayout()

const navItems = [
  { key: 'dashboard', label: '首页', icon: HomeFilled },
  { key: 'expense', label: '记账', icon: Plus },
  { key: 'records', label: '记录', icon: Document },
  { key: 'statistics', label: '统计', icon: DataAnalysis },
  { key: 'budget', label: '预算', icon: TrendCharts },
  { key: 'settings', label: '设置', icon: Setting }
]

const componentMap: Record<string, Component> = {
  dashboard: DashboardTab,
  expense: ExpenseTab,
  records: RecordsTab,
  statistics: StatisticsTab,
  budget: BudgetTab,
  settings: SettingsTab
}

const currentComponent = shallowRef<Component>(DashboardTab)
const asideWidth = computed(() => (navMode.value === 'rail' ? '64px' : '220px'))

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

/* 竖窗/窄窗：主区在上、底部栏在下，改为纵向排列 */
.app-container.nav-bottom {
  flex-direction: column;
}

.sidebar {
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
  transition: width 0.2s ease, background 0.3s, border-color 0.3s;
}

.logo {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid var(--el-border-color-light);
  overflow: hidden;
  white-space: nowrap;
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
  transition: background 0.3s, padding 0.2s;
}

/* 超宽屏：内容居中限宽，避免图表被拉成超扁条 */
@media (min-aspect-ratio: 21/9) {
  .main-content > * {
    max-width: 1400px;
    margin-inline: auto;
  }
}

/* 矮窗（16:9 笔记本）：压缩纵向留白 */
.compact-height .main-content {
  padding: 16px;
}

/* 底部标签栏 */
.bottom-tab {
  display: flex;
  border-top: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  flex-shrink: 0;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 8px 0 6px;
  border: none;
  background: transparent;
  color: var(--el-text-color-secondary);
  font-size: 11px;
  cursor: pointer;
  transition: color 0.2s;
}

.tab-item.active {
  color: var(--el-color-primary);
  font-weight: 600;
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
