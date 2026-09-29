import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'
import { ElInputNumber, ElSelect, ElDatePicker } from 'element-plus'
import ExpenseTab from '@/components/ExpenseTab.vue'
import { todayLocal } from '@/utils/constants'
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

function findSaveButton(wrapper: VueWrapper): HTMLButtonElement {
  const btn = wrapper
    .findAll('button')
    .find((b) => b.text().includes('保存记录'))
  expect(btn, '应存在"保存记录"按钮').toBeTruthy()
  return btn!.element as HTMLButtonElement
}

describe('ExpenseTab', () => {
  let wrapper: VueWrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockApi.getCategories.mockResolvedValue({
      data: [
        { id: 1, name: '餐饮', icon: '🍜', is_default: true },
        { id: 2, name: '交通', icon: '🚌', is_default: true }
      ]
    })
    mockApi.getStatistics.mockResolvedValue({
      data: { year: 2026, month: 9, total: 0, categories: [] }
    })
    mockApi.getExpenses.mockResolvedValue({ data: [] })
    mockApi.createExpense.mockResolvedValue({
      data: {
        id: 1,
        amount: 15.57,
        category: '餐饮',
        description: '',
        date: todayLocal(),
        created_at: '2026-09-30 12:00:00'
      }
    })
  })

  afterEach(() => {
    wrapper?.unmount()
    cleanupBody()
  })

  it('挂载后加载分类与本月概览（getCategories + getStatistics + getExpenses）', async () => {
    wrapper = mount(ExpenseTab)
    await flushPromises()

    const now = new Date()
    expect(mockApi.getCategories).toHaveBeenCalledTimes(1)
    expect(mockApi.getStatistics).toHaveBeenCalledWith(
      now.getFullYear(),
      now.getMonth() + 1
    )
    expect(mockApi.getExpenses).toHaveBeenCalledWith(
      now.getFullYear(),
      now.getMonth() + 1
    )
  })

  it('金额输入框初始为空（非 0 / 0.01），日期初始值为 todayLocal()', async () => {
    wrapper = mount(ExpenseTab)
    await flushPromises()

    const amountInput = wrapper.findComponent(ElInputNumber)
    expect(amountInput.props('modelValue')).toBeUndefined()
    expect(
      (amountInput.find('input').element as HTMLInputElement).value
    ).toBe('')

    expect(wrapper.findComponent(ElDatePicker).props('modelValue')).toBe(
      todayLocal()
    )
  })

  it('不填任何内容直接点"保存记录"：校验拦截，createExpense 不被调用', async () => {
    wrapper = mount(ExpenseTab)
    await flushPromises()

    await wrapper.findAll('button')
      .find((b) => b.text().includes('保存记录'))!
      .trigger('click')
    await flushPromises()

    expect(mockApi.createExpense).not.toHaveBeenCalled()
  })

  it('填金额 15.567 + 分类后提交：createExpense 收到两位小数 15.57', async () => {
    wrapper = mount(ExpenseTab)
    await flushPromises()

    wrapper.findComponent(ElInputNumber).vm.$emit('update:modelValue', 15.567)
    wrapper.findComponent(ElSelect).vm.$emit('update:modelValue', '餐饮')
    await flushPromises()

    findSaveButton(wrapper).click()
    await flushPromises()

    expect(mockApi.createExpense).toHaveBeenCalledTimes(1)
    expect(mockApi.createExpense).toHaveBeenCalledWith({
      amount: 15.57,
      category: '餐饮',
      description: '',
      date: todayLocal()
    })
  })

  it('提交成功后表单清空（金额输入框变空）', async () => {
    wrapper = mount(ExpenseTab)
    await flushPromises()

    wrapper.findComponent(ElInputNumber).vm.$emit('update:modelValue', 15.567)
    wrapper.findComponent(ElSelect).vm.$emit('update:modelValue', '餐饮')
    await flushPromises()

    findSaveButton(wrapper).click()
    await flushPromises()

    expect(mockApi.createExpense).toHaveBeenCalledTimes(1)
    const amountInput = wrapper.findComponent(ElInputNumber)
    expect(
      amountInput.props('modelValue') === undefined ||
        amountInput.props('modelValue') === null
    ).toBe(true)
    expect(
      (amountInput.find('input').element as HTMLInputElement).value
    ).toBe('')
    expect(document.body.textContent).toContain('记录保存成功')
  })
})
