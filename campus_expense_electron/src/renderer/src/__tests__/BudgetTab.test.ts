import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'
import { ElInputNumber } from 'element-plus'
import BudgetTab from '@/components/BudgetTab.vue'
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

function budgetData(overrides: Partial<{
  monthly_budget: number | null
  spent: number
  remaining: number
  percentage: number
}> = {}) {
  return {
    data: {
      monthly_budget: 2000,
      spent: 1000,
      remaining: 1000,
      percentage: 50,
      ...overrides
    }
  }
}

describe('BudgetTab', () => {
  let wrapper: VueWrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockApi.setBudget.mockResolvedValue({ data: {} })
  })

  afterEach(() => {
    wrapper?.unmount()
    cleanupBody()
  })

  it('monthly_budget=null 时显示"尚未设置月度预算"', async () => {
    mockApi.getBudget.mockResolvedValue(
      budgetData({ monthly_budget: null, spent: 0, remaining: 0, percentage: 0 })
    )
    wrapper = mount(BudgetTab)
    await flushPromises()

    expect(wrapper.text()).toContain('尚未设置月度预算')
    expect(wrapper.find('.budget-overview').exists()).toBe(false)
  })

  it('已设置预算时显示 月度预算/已使用/剩余 三个数值', async () => {
    mockApi.getBudget.mockResolvedValue(
      budgetData({ monthly_budget: 2000, spent: 1600, remaining: 400, percentage: 80 })
    )
    wrapper = mount(BudgetTab)
    await flushPromises()

    const stats = wrapper.findAll('.stat-card')
    expect(stats.length).toBe(3)
    expect(stats[0].text()).toContain('月度预算')
    expect(stats[0].text()).toContain('¥2000.00')
    expect(stats[1].text()).toContain('已使用')
    expect(stats[1].text()).toContain('¥1600.00')
    expect(stats[2].text()).toContain('剩余')
    expect(stats[2].text()).toContain('¥400.00')
  })

  it('预算输入为 0 时点"保存"：setBudget 不被调用并弹出警告', async () => {
    mockApi.getBudget.mockResolvedValue(
      budgetData({ monthly_budget: null, spent: 0, remaining: 0, percentage: 0 })
    )
    wrapper = mount(BudgetTab)
    await flushPromises()

    wrapper.findComponent(ElInputNumber).vm.$emit('update:modelValue', 0)
    await flushPromises()

    const saveBtn = wrapper.findAll('button').find((b) => b.text().includes('保存'))
    expect(saveBtn, '应存在"保存"按钮').toBeTruthy()
    await saveBtn!.trigger('click')
    await flushPromises()

    expect(mockApi.setBudget).not.toHaveBeenCalled()
    expect(document.body.textContent).toContain('请输入有效的预算金额')
  })

  it('percentage=80（边界）显示"预算使用提醒"而不是"良好"', async () => {
    mockApi.getBudget.mockResolvedValue(
      budgetData({ monthly_budget: 2000, spent: 1600, remaining: 400, percentage: 80 })
    )
    wrapper = mount(BudgetTab)
    await flushPromises()

    expect(wrapper.text()).toContain('预算使用提醒')
    expect(wrapper.text()).not.toContain('预算状态良好')
    expect(wrapper.text()).not.toContain('预算超支警告')
  })

  it('percentage=105 显示"预算超支警告"', async () => {
    mockApi.getBudget.mockResolvedValue(
      budgetData({ monthly_budget: 2000, spent: 2100, remaining: -100, percentage: 105 })
    )
    wrapper = mount(BudgetTab)
    await flushPromises()

    expect(wrapper.text()).toContain('预算超支警告')
    expect(wrapper.text()).toContain('¥100.00')
  })

  it('percentage=50 显示"预算状态良好"', async () => {
    mockApi.getBudget.mockResolvedValue(budgetData())
    wrapper = mount(BudgetTab)
    await flushPromises()

    expect(wrapper.text()).toContain('预算状态良好')
    expect(wrapper.text()).not.toContain('预算使用提醒')
  })
})
