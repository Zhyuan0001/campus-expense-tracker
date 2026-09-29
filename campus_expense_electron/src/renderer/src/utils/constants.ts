export const CATEGORY_COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
  '#FFEAA7', '#DDA0DD', '#FF8A5C', '#A8A8A8',
  '#6366F1', '#10B981'
]

export const CATEGORY_ICON_MAP: Record<string, string> = {
  '餐饮': '🍜', '交通': '🚌', '学习': '📚', '娱乐': '🎮',
  '社交': '👥', '购物': '🛒', '医疗': '💊', '其他': '📌'
}

export function getCategoryIcon(name: string, fallbackMap?: Record<string, string>): string {
  if (fallbackMap && fallbackMap[name]) return fallbackMap[name]
  return CATEGORY_ICON_MAP[name] || '📌'
}

export function isDarkMode(): boolean {
  return document.documentElement.classList.contains('dark')
}

export function getChartTextColor(): string {
  return isDarkMode() ? '#ccc' : '#666'
}

export function getChartBorderColor(): string {
  return isDarkMode() ? '#1e1e32' : '#fff'
}
