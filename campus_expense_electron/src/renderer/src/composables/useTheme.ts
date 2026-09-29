import { ref } from 'vue'

// 模块级单例：设置页的开关与 App 启动时的初始化必须共享同一份状态，
// 否则切换 Tab 后组件重新挂载会读到旧值
const isDark = ref(false)

function applyTheme(): void {
  document.documentElement.classList.toggle('dark', isDark.value)
}

export function useTheme() {
  function initTheme(): void {
    isDark.value = localStorage.getItem('theme') === 'dark'
    applyTheme()
  }

  function setDark(value: boolean): void {
    isDark.value = value
    localStorage.setItem('theme', value ? 'dark' : 'light')
    applyTheme()
  }

  function toggleTheme(): void {
    setDark(!isDark.value)
  }

  return { isDark, initTheme, setDark, toggleTheme }
}
