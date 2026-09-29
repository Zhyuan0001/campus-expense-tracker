import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BudgetTab from '../components/BudgetTab.vue'

describe('BudgetTab', () => {
  it('renders component correctly', () => {
    const wrapper = mount(BudgetTab)
    expect(wrapper.exists()).toBe(true)
  })

  it('is a Vue component', () => {
    const wrapper = mount(BudgetTab)
    expect(wrapper.vm).toBeDefined()
  })
})
