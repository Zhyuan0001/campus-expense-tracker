import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ExpenseTab from '../components/ExpenseTab.vue'

describe('ExpenseTab', () => {
  it('renders component correctly', () => {
    const wrapper = mount(ExpenseTab)
    expect(wrapper.exists()).toBe(true)
  })

  it('is a Vue component', () => {
    const wrapper = mount(ExpenseTab)
    expect(wrapper.vm).toBeDefined()
  })
})
