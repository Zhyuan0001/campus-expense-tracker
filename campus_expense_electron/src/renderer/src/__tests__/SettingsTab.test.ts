import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'
import { ElSwitch, ElPopconfirm } from 'element-plus'
import SettingsTab from '@/components/SettingsTab.vue'
import { useTheme } from '@/composables/useTheme'
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

const categories = [
  { id: 1, name: '餐饮', icon: '🍜', is_default: true },
  { id: 9, name: '宠物', icon: '🐾', is_default: false }
]

function findButton(wrapper: VueWrapper, text: string) {
  const btn = wrapper.findAll('button').find((b) => b.text().includes(text))
  expect(btn, `应存在"${text}"按钮`).toBeTruthy()
  return btn!
}

describe('SettingsTab', () => {
  let wrapper: VueWrapper

  beforeEach(() => {
    vi.clearAllMocks()
    // useTheme 是模块级单例，必须手动复位，避免用例间互相污染
    localStorage.clear()
    document.documentElement.classList.remove('dark')
    useTheme().isDark.value = false

    mockApi.getCategories.mockResolvedValue({ data: categories })
    mockApi.createCategory.mockResolvedValue({
      data: { id: 10, name: '宠物', icon: '📌', is_default: false }
    })
    mockApi.deleteCategory.mockResolvedValue({ data: {} })
    mockApi.exportCSV.mockResolvedValue({ data: 'ID,日期,分类,描述,金额' })
  })

  afterEach(() => {
    wrapper?.unmount()
    cleanupBody()
  })

  it('存在"暗色主题"开关：打开加 dark 类并写 localStorage，再关则移除', async () => {
    wrapper = mount(SettingsTab)
    await flushPromises()
    expect(wrapper.text()).toContain('暗色主题')

    const themeSwitch = wrapper.findComponent(ElSwitch)
    expect(themeSwitch.exists()).toBe(true)

    // 模拟真实交互：el-switch 先经 v-model 更新 isDark，再 emit change
    themeSwitch.vm.$emit('update:modelValue', true)
    themeSwitch.vm.$emit('change', true)
    await flushPromises()
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('theme')).toBe('dark')

    themeSwitch.vm.$emit('update:modelValue', false)
    themeSwitch.vm.$emit('change', false)
    await flushPromises()
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(localStorage.getItem('theme')).toBe('light')
  })

  it('空分类名点"添加分类"：createCategory 不被调用', async () => {
    wrapper = mount(SettingsTab)
    await flushPromises()

    await findButton(wrapper, '添加分类').trigger('click')
    await flushPromises()

    expect(mockApi.createCategory).not.toHaveBeenCalled()
    expect(document.body.textContent).toContain('请输入分类名称')
  })

  it('填"宠物"点"添加分类"：以 { name, icon } 调用并提示成功', async () => {
    wrapper = mount(SettingsTab)
    await flushPromises()

    const nameInput = wrapper.find('input[placeholder="输入分类名称"]')
    expect(nameInput.exists()).toBe(true)
    await nameInput.setValue('宠物')

    await findButton(wrapper, '添加分类').trigger('click')
    await flushPromises()

    expect(mockApi.createCategory).toHaveBeenCalledTimes(1)
    expect(mockApi.createCategory).toHaveBeenCalledWith({
      name: '宠物',
      icon: '📌'
    })
    expect(document.body.textContent).toContain('分类添加成功')
  })

  it('is_default=true 的行显示"不可删除"，is_default=false 的行有删除按钮', async () => {
    wrapper = mount(SettingsTab)
    await flushPromises()

    expect(wrapper.text()).toContain('不可删除')
    const popconfirms = wrapper.findAllComponents(ElPopconfirm)
    expect(popconfirms.length).toBe(1)
    expect(popconfirms[0].text()).toContain('删除')
  })

  it('window.electronAPI 为 undefined 时"关于"卡片回退到内置版本号', async () => {
    expect((window as any).electronAPI).toBeUndefined()
    wrapper = mount(SettingsTab)
    await flushPromises()

    // 断言版本格式而非具体版本号：版本号随发布递增，锁死会导致每次发版改测试
    expect(wrapper.text()).toMatch(/\d+\.\d+\.\d+ \(Electron\)/)
  })

  it('点"导出CSV"调用 exportCSV 并走 blob 下载回退', async () => {
    // jsdom 没有 URL.createObjectURL / 下载能力，测试内 stub
    const createObjectURL = vi.fn(() => 'blob:mock-url')
    const revokeObjectURL = vi.fn()
    Object.defineProperty(window.URL, 'createObjectURL', {
      value: createObjectURL,
      configurable: true,
      writable: true
    })
    Object.defineProperty(window.URL, 'revokeObjectURL', {
      value: revokeObjectURL,
      configurable: true,
      writable: true
    })
    const clickSpy = vi
      .spyOn(HTMLAnchorElement.prototype, 'click')
      .mockImplementation(() => {})

    wrapper = mount(SettingsTab)
    await flushPromises()

    await findButton(wrapper, '导出CSV').trigger('click')
    await flushPromises()

    expect(mockApi.exportCSV).toHaveBeenCalledTimes(1)
    expect(createObjectURL).toHaveBeenCalled()
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:mock-url')
    expect(document.body.textContent).toContain('导出成功')

    clickSpy.mockRestore()
  })
})
