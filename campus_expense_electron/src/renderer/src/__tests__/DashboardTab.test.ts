import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'
import DashboardTab from '@/components/DashboardTab.vue'
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

function remainingBudgetCard(wrapper: VueWrapper) {
  const card = wrapper
    .findAll('.stat-card')
    .find((c) => c.text().includes('剩余预算'))
  expect(card, '应存在"剩余预算"卡片').toBeTruthy()
  return card!.find('.stat-value')
}

describe('DashboardTab', () => {
  let wrapper: VueWrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockApi.getStatistics.mockResolvedValue({
      data: {
        year: 2026,
        month: 9,
        total: 16,
        categories: [{ category: '餐饮', total: 16 }]
      }
    })
    mockApi.getExpenses.mockResolvedValue({
      data: [
        {
          id: 1,
          amount: 16,
          category: '餐饮',
          description: '午饭',
          date: '2026-09-01',
          created_at: '2026-09-01 12:00:00'
        }
      ]
    })
  })

  afterEach(() => {
    wrapper?.unmount()
    cleanupBody()
  })

  it('monthly_budget=null 时"剩余预算"卡片显示"未设置"而不是 ¥0.00', async () => {
    mockApi.getBudget.mockResolvedValue({
      data: { monthly_budget: null, spent: 0, remaining: 0, percentage: 0 }
    })
    wrapper = mount(DashboardTab)
    await flushPromises()

    const value = remainingBudgetCard(wrapper)
    expect(value.text()).toBe('未设置')
    expect(value.text()).not.toContain('¥0.00')
  })

  it('monthly_budget=2000、remaining=1984 时显示 ¥1984.00', async () => {
    mockApi.getBudget.mockResolvedValue({
      data: { monthly_budget: 2000, spent: 16, remaining: 1984, percentage: 0.8 }
    })
    wrapper = mount(DashboardTab)
    await flushPromises()

    expect(remainingBudgetCard(wrapper).text()).toBe('¥1984.00')
  })

  it('挂载后 getStatistics 至少被调用 7 次（本月 1 次 + 近 6 月趋势 6 次）', async () => {
    mockApi.getBudget.mockResolvedValue({
      data: { monthly_budget: 2000, spent: 16, remaining: 1984, percentage: 0.8 }
    })
    wrapper = mount(DashboardTab)
    await flushPromises()

    expect(mockApi.getStatistics.mock.calls.length).toBeGreaterThanOrEqual(7)
    expect(mockApi.getBudget).toHaveBeenCalledTimes(1)
    expect(mockApi.getExpenses).toHaveBeenCalledTimes(1)
  })
})
