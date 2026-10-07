import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

export type NavMode = 'full' | 'rail' | 'bottom'

/**
 * 窗口尺寸 / 比例的响应式状态，驱动导航形态与栅格列数。
 *
 * 断点沿用 Windows 官方分级（Small ≤640 / Medium 641–1007 / Large ≥1008），
 * 并叠加"竖窗/超宽"两类形状判断——这是纯宽度断点看不见的维度。
 */
export function useLayout() {
  const width = ref(window.innerWidth)
  const height = ref(window.innerHeight)

  const onResize = (): void => {
    width.value = window.innerWidth
    height.value = window.innerHeight
  }

  onMounted(() => window.addEventListener('resize', onResize))
  onBeforeUnmount(() => window.removeEventListener('resize', onResize))

  const ratio = computed(() => (height.value > 0 ? width.value / height.value : 1))
  // 竖窗：宽 < 高（像手机那样把窗口拉成竖条）
  const isPortrait = computed(() => ratio.value <= 1)
  const isNarrow = computed(() => width.value <= 640)
  // 超宽屏：21:9 及以上
  const isUltrawide = computed(() => ratio.value >= 21 / 9)
  // 矮窗（16:9 笔记本，高度紧张）——纯宽度断点永远触发不了
  const isCompactHeight = computed(() => height.value <= 700)

  // 导航形态：竖窗/窄窗 → 底部 tab；中宽 → 图标轨；宽 → 全栏
  const navMode = computed<NavMode>(() => {
    if (isPortrait.value || width.value <= 768) return 'bottom'
    if (width.value <= 1007) return 'rail'
    return 'full'
  })

  // 内容区栅格列数（指标卡用）
  const cols = computed(() => {
    if (isUltrawide.value) return 4
    if (width.value >= 1008) return 4
    if (width.value > 640) return 2
    return 1
  })

  return { width, height, ratio, isPortrait, isNarrow, isUltrawide, isCompactHeight, navMode, cols }
}
