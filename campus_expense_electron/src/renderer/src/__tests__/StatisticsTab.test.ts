import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'
import StatisticsTab from '@/components/StatisticsTab.vue'
import { installDomStubs, cleanupBody } from './testHelpers'

installDomStubs()

const mockApi = vi.hoisted(() => ({
  getExpenses: vi.fn(),
  createExpense: vi.fn(),
  deleteExpense: vi.fn(),
  getCategories: vi.fn(),
  createCategory: vi.fn(),
  deleteCategory: vi.fn(),
  getStatistics: vi.fn(),
  getBudget: vi.fn(),
  setBudget: vi.fn(),
  exportCSV: vi.fn()
}))

vi.mock('@/api', () => ({ api: mockApi }))

// jsdom 没有 canvas，组件里 echarts.init 必须 mock 掉
const mockChart = vi.hoisted(() => ({
  setOption: vi.fn(),
  resize: vi.fn(),
  dispose: vi.fn()
}))
vi.mock('echarts', () => ({
  init: vi.fn(() => mockChart)
}))

// vitest 配置未开启 css 处理，SFC 的 scoped 样式不会注入 jsdom。
// 为了按设计文档断言"总额是醒目的红色大字"，从组件源码中提取真实样式，
// 把 var(--el-color-danger) 展开为 Element Plus 的标准值 #f56c6c 后注入。
function injectComponentStyles(): void {
  const sfc = readFileSync(
    resolve(__dirname, '../components/StatisticsTab.vue'),
    'utf-8'
  )
  const styleBlock = sfc.match(/<style scoped>([\s\S]*?)<\/style>/)
  expect(styleBlock, 'StatisticsTab.vue 应有 scoped 样式块').toBeTruthy()
  const css = styleBlock![1].replace(/var\(--el-color-danger\)/g, '#f56c6c')
  const style = document.createElement('style')
  style.textContent = css
  document.head.appendChild(style)
}

describe('StatisticsTab', () => {
  let wrapper: VueWrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockApi.getStatistics.mockResolvedValue({
      data: {
        year: 2026,
        month: 9,
        total: 15.5,
        categories: [{ category: '餐饮', total: 15.5 }]
      }
    })
  })

  afterEach(() => {
    wrapper?.unmount()
    cleanupBody()
  })

  it('total=15.5、单分类 15.5 时显示 ¥15.50 和 100.0%', async () => {
    wrapper = mount(StatisticsTab)
    await flushPromises()

    expect(wrapper.find('.total-amount').text()).toBe('¥15.50')
    expect(wrapper.find('.percentage').text()).toBe('100.0%')
    expect(mockChart.setOption).toHaveBeenCalled()
  })

  it('categories 为空数组时显示"该月暂无数据"', async () => {
    mockApi.getStatistics.mockResolvedValue({
      data: { year: 2026, month: 9, total: 0, categories: [] }
    })
    wrapper = mount(StatisticsTab)
    await flushPromises()

    expect(wrapper.text()).toContain('该月暂无数据')
    expect(wrapper.find('.pie-chart').exists()).toBe(false)
  })

  it('总额元素为醒目的红色（--el-color-danger / rgb(245,108,108)）', async () => {
    injectComponentStyles()
    wrapper = mount(StatisticsTab)
    await flushPromises()

    const totalEl = wrapper.find('.total-amount').element as HTMLElement
    const color = window.getComputedStyle(totalEl).color
    expect(
      color === 'rgb(245, 108, 108)' || color === '#f56c6c',
      `总额颜色应为 Element Plus danger 红，实际为 "${color}"`
    ).toBe(true)
  })
})
