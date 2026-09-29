import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { useTheme } from '@/composables/useTheme'

// useTheme 内部是模块级单例 ref，测试之间必须手动清理
// document 的 class 与 localStorage，否则会互相污染
beforeEach(() => {
  localStorage.clear()
  document.documentElement.classList.remove('dark')
  useTheme().isDark.value = false
})

afterEach(() => {
  localStorage.clear()
  document.documentElement.classList.remove('dark')
  useTheme().isDark.value = false
})

describe('useTheme', () => {
  it('localStorage 预置 theme=dark 后 initTheme() 给 <html> 加 dark 类', () => {
    localStorage.setItem('theme', 'dark')
    const { initTheme, isDark } = useTheme()

    initTheme()

    expect(isDark.value).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('dark 状态下 toggleTheme() 翻转到 light 并持久化', () => {
    localStorage.setItem('theme', 'dark')
    const { initTheme, toggleTheme, isDark } = useTheme()
    initTheme()
    expect(document.documentElement.classList.contains('dark')).toBe(true)

    toggleTheme()

    expect(isDark.value).toBe(false)
    expect(localStorage.getItem('theme')).toBe('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('light 状态下 toggleTheme() 翻转到 dark 并持久化', () => {
    localStorage.setItem('theme', 'light')
    const { initTheme, toggleTheme, isDark } = useTheme()
    initTheme()
    expect(document.documentElement.classList.contains('dark')).toBe(false)

    toggleTheme()

    expect(isDark.value).toBe(true)
    expect(localStorage.getItem('theme')).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})
