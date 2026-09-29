import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'
import { ElDatePicker, ElPopconfirm } from 'element-plus'
import RecordsTab from '@/components/RecordsTab.vue'
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

const rows = [
  {
    id: 1,
    amount: 15.5,
    category: '餐饮',
    description: '午饭',
    date: '2026-09-01',
    created_at: '2026-09-01 12:00:00'
  },
  {
    id: 2,
    amount: 8,
    category: '交通',
    description: '地铁',
    date: '2026-09-02',
    created_at: '2026-09-02 08:30:00'
  }
]

describe('RecordsTab', () => {
  let wrapper: VueWrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockApi.getExpenses.mockResolvedValue({ data: rows })
    mockApi.deleteExpense.mockResolvedValue({ data: {} })
  })

  afterEach(() => {
    wrapper?.unmount()
    cleanupBody()
  })

  it('表头包含设计文档要求的列：ID、日期、分类、描述、金额', async () => {
    wrapper = mount(RecordsTab)
    await flushPromises()

    const headerText = wrapper.find('.el-table__header').text()
    for (const col of ['ID', '日期', '分类', '描述', '金额']) {
      expect(headerText, `表头应包含 ${col}`).toContain(col)
    }
  })

  it('getExpenses 返回的记录渲染成行，金额显示两位小数', async () => {
    wrapper = mount(RecordsTab)
    await flushPromises()

    const trs = wrapper.findAll('.el-table__body tbody tr')
    expect(trs.length).toBe(2)
    expect(trs[0].text()).toContain('¥15.50')
    expect(trs[0].text()).toContain('午饭')
    expect(trs[1].text()).toContain('¥8.00')
  })

  it('设置月份筛选 2026-09 后，以 year=2026、month=9 重新请求', async () => {
    wrapper = mount(RecordsTab)
    await flushPromises()
    expect(mockApi.getExpenses).toHaveBeenLastCalledWith(undefined, undefined)

    wrapper.findComponent(ElDatePicker).vm.$emit('update:modelValue', '2026-09')
    await flushPromises()

    expect(mockApi.getExpenses).toHaveBeenCalledTimes(2)
    expect(mockApi.getExpenses).toHaveBeenLastCalledWith(2026, 9)
  })

  it('ElPopconfirm 触发 confirm 后以该行 id 调用 deleteExpense', async () => {
    wrapper = mount(RecordsTab)
    await flushPromises()

    const popconfirms = wrapper.findAllComponents(ElPopconfirm)
    expect(popconfirms.length).toBe(2)
    popconfirms[0].vm.$emit('confirm')
    await flushPromises()

    expect(mockApi.deleteExpense).toHaveBeenCalledTimes(1)
    expect(mockApi.deleteExpense).toHaveBeenCalledWith(1)
    expect(document.body.textContent).toContain('删除成功')
  })
})
